from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
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

  @classmethod
  def phase(cls):
    meta = cls.get_meta_data()
    current_time = timezone.now()
    if current_time < meta.coding_start_time:
      return cls.YET_TO_START
    elif current_time <= meta.coding_end_time:
      return cls.CODING_PHASE
    elif current_time < meta.hacking_start_time:
      return cls.BREAK_PHASE
    elif current_time <= meta.hacking_end_time:
      return cls.HACKING_PHASE
    else:
      return cls.ENDED

class Announcements(models.Model):
  text = models.TextField()

class Participant(models.Model):
  user = models.OneToOneField(User,
    on_delete = models.CASCADE,
    related_name='participant'
  )
  name = models.CharField(max_length = 200)
  college = models.CharField(max_length = 300)
  contact = models.BigIntegerField()
  org_score = models.IntegerField(default = 0)
  chal_score_earned = models.IntegerField(default = 0)
  chal_score_lost = models.IntegerField(default = 0)
  total_score = models.IntegerField(default = 0)

class Problem(models.Model):
  name = models.CharField(max_length = 100)
  problem_text = models.TextField()
  code = models.TextField(default = '')
  correct_code = models.TextField(default = '')

  @property
  def max_points(self):
    points = 0
    for case in self.test_cases.all():
      points += case.points
    return points

class TestCases(models.Model):
  problem = models.ForeignKey(Problem, related_name = 'test_cases')
  input_data = models.TextField() # The input that will be given in Test Case
  output_data = models.TextField() # The Expected Output of the Test Case
  points = models.IntegerField() # The score that will be added for this case
  time_limit = models.IntegerField() # In Seconds
  is_system_test = models.BooleanField(default = False)

  '''ToDo - Impose Memory Limit'''

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
  hackers = models.ManyToManyField(Participant, through = 'Challenge')
  is_hacked = models.BooleanField(default = False)

class TestCaseResult(models.Model):
  WAITING = 'wt'
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

class Challenge(models.Model):
  challenger = models.ForeignKey(Participant,
    on_delete = models.CASCADE,
    related_name = 'challenges_posted'
  )
  solution = models.ForeignKey(Solution,
    on_delete = models.CASCADE,
    related_name = 'challenges'
  )
  input_data = models.TextField()
