from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime, string
from django.core.exceptions import ValidationError
# Create your models here.

class Metadata(models.Model):

  YET_TO_START = 1
  CODING_PHASE = 2
  BREAK_PHASE = 3
  HACKING_PHASE = 4
  ENDED = 5

  coding_start_time = models.DateTimeField()
  coding_end_time = models.DateTimeField()
  hacking_start_time = models.DateTimeField()
  hacking_end_time = models.DateTimeField()

  @classmethod
  def get_meta_data(cls):
    res = cls.objects.all()
    if len(res) > 1:
      for x in res:
        x.delete()
    if len(res) == 0:
      current_time = timezone.now()
      # Create a dummy metadata  - Development
      new_row = cls(
        coding_start_time = current_time + datetime.timedelta(minutes = 5),
        coding_end_time = current_time + datetime.timedelta(minutes = 10),
        hacking_start_time = current_time + datetime.timedelta(minutes = 15),
        hacking_end_time = current_time + datetime.timedelta(minutes = 20)
      )
      new_row.save()
      return new_row
    else:
      return res[0]

  @property
  def phase(self):
    current_time = timezone.now()
    if current_time < self.coding_start_time:
      return self.YET_TO_START
    elif current_time <= self.coding_end_time:
      return self.CODING_PHASE
    elif current_time < self.hacking_start_time:
      return self.BREAK_PHASE
    elif current_time <= self.hacking_end_time:
      return self.HACKING_PHASE
    else:
      return self.ENDED

  def clean(self):
    if Metadata.objects.count() > 1 or Metadata.objects.get().id != self.id:
      raise ValidationError('Only One Instance of Metadata can be created !!')

class Announcements(models.Model):
  text = models.TextField()
  time_posted = models.DateTimeField(auto_now_add = True)

  class Meta:
    ordering = ['-time_posted']

  def __str__(self):
    return str(self.id) + ' - ' + str(self.text[:len(self.text)
      if len(self.text) < 11 else 10])

class Participant(models.Model):
  user = models.OneToOneField(User,
    on_delete = models.CASCADE,
    related_name='participant'
  )
  name = models.CharField(max_length = 200)
  college = models.CharField(max_length = 300)
  contact = models.BigIntegerField()
  org_score = models.IntegerField(default = 0)
  main_score = models.IntegerField(default = 0)
  chal_score_earned = models.IntegerField(default = 0)
  chal_score_lost = models.IntegerField(default = 0)

  '''
    org_score = The total cumulative score of user at any given time
    main_score = The score gained by user due to passing pre-test / system test
    chal_score_earned = The score earned or lost my user by challenging other's
    solution
    chal_score_lost = The score lost by user because of their solution being
    challenged by other users

    org_score = main_score + chal_score_earned - chal_score_lost
  '''

  # Overriding save function to ensure that the above condition is always true
  def save(self, *args, **kwargs):
    rhs = self.main_score + self.chal_score_earned - self.chal_score_lost
    assert (self.org_score == rhs), "The Scores are in inconsistent state"

    # If everything is alright, then execute the save()
    super(Participant, self).save(*args, **kwargs)

  def __str__(self):
    return str(self.name)

  @property
  def rank(self):
    query_set = Participant.objects.filter(org_score__gt = self.org_score)
    return query_set.aggregate(rank = models.Count('org_score'))['rank'] + 1

  @property
  def pretest_solved(self):
    return self.solutions.filter(status = Solution.PRE_TEST_PASSED).aggregate(
      co = models.Count('problem', distinct = True)
    )['co']

  @property
  def systest_solved(self):
    return self.solutions.filter(status = Solution.SYS_TEST_PASSED).aggregate(
      co = models.Count('problem', distinct = True)
    )['co']

  @property
  def no_of_successful_hack(self):
    return len(self.challenges_posted.filter(status = Challenge.SUCCESSFUL))

class Problem(models.Model):
  name = models.CharField(max_length = 100)
  problem_text = models.TextField()
  code = models.TextField(default = '')
  correct_code = models.TextField(default = '')
  time_limit = models.IntegerField(default = 3)

  @property
  def max_points(self):
    points = 0
    for case in self.test_cases.all():
      points += case.points
    return points

  def __str__(self):
    return str(self.name)

class TestCases(models.Model):
  problem = models.ForeignKey(Problem, related_name = 'test_cases')
  input_data = models.TextField() # The input that will be given in Test Case
  output_data = models.TextField() # The Expected Output of the Test Case
  points = models.IntegerField() # The score that will be added for this case
  is_system_test = models.BooleanField(default = False)

  '''ToDo - Impose Memory Limit'''

  def save(self, *args, **kwargs):
    self.output_data = str(self.output_data).translate(None, string.whitespace)
    super(TestCases, self).save(*args, **kwargs)

  def __str__(self):
    return str(self.id)

class Solution(models.Model):
  PROCESSING = 'pr'
  COMPILE_ERROR = 'ce'
  PRE_TEST_FAILED = 'ptf'
  PRE_TEST_PASSED = 'ptp'
  SYS_TEST_FAILED = 'stf'
  SYS_TEST_PASSED = 'stp'

  participant = models.ForeignKey(Participant, related_name = 'solutions')
  problem = models.ForeignKey(Problem)
  code = models.TextField()

  ''' Currently the application only supports cpp. But in Future the Support for
  other languages should be easy to add :)'''
  language = models.CharField(max_length = 10, default = 'cpp')
  test_results = models.ManyToManyField(TestCases, through = 'TestCaseResult')
  score_earned = models.IntegerField(default = 0)
  compile_throw = models.TextField(default = '')
  status = models.CharField(max_length = 10, default = PROCESSING)
  submit_time = models.DateTimeField(auto_now_add = True)
  is_hacked = models.BooleanField(default = False)

  def __str__(self):
    return str(self.id)

  class Meta:
    ordering = ['-submit_time']

class TestCaseResult(models.Model):
  WAITING = 'wt'
  COMPILE_ERROR = 'ce'
  ACCEPTED = 'ac'
  WRONG_ANS = 'wa'
  RUNTIME_ERROR = 're'
  TIME_LIMIT_EXCEEDED = 'tle'
  UNKNOWN_ERROR = 'ue'

  solution = models.ForeignKey(Solution,
    on_delete = models.CASCADE,
    related_name = 'test_case_results'
  )
  test_case = models.ForeignKey(TestCases,
    on_delete = models.CASCADE,
    related_name = 'should_not_be_accessed'
  )
  status = models.CharField(max_length = 10, default = WAITING)
  creation_time = models.DateTimeField(auto_now_add = True)
  last_updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return str(self.id)

  class Meta:
    unique_together = ('solution', 'test_case')

class Challenge(models.Model):
  WAITING = 'wt'
  INVALID_INPUT = 'inv'
  SUCCESSFUL = 'succ'
  FAILED = 'fail'

  '''
    INVALID_INPUT Status occurs when the challenger's input data is out of scope
    of the problem's constraint. Invalid input is detected by running the input
    against problem setter's code. If the problem setter's code causes a runtime
    error or time out exception - it means the invalid is invalid.

    Assumption - The Problem Setter's code raises runtime exception if invalid
    input is detected !!!
  '''

  challenger = models.ForeignKey(Participant,
    on_delete = models.CASCADE,
    related_name = 'challenges_posted'
  )
  solution = models.ForeignKey(Solution,
    on_delete = models.CASCADE,
    related_name = 'challenge'
  )
  input_data = models.TextField()
  status = models.CharField(max_length = 10, default = WAITING)
  submit_time = models.DateTimeField(auto_now_add = True)

  '''
    Currently the score added and subtracted for each challenge is constant and
    is hard coded in the task.py file. In future you many want to score these
    constants in databases so that it can be changed in admin panel without
    changing any code.

    Or Better : Add a custom challenge gain or loss points on each problem. That
    would be really cool :D
  '''

  def __str__(self):
    return "Challenge ID - " + str(self.id)
