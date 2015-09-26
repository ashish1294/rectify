from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Participant(models.Model):
  user = models.OneToOneField(User)
  name = models.CharField(max_length = 200)
  college = models.CharField(max_length = 300)
  contact = models.IntegerField()
  org_score = models.IntegerField(default = 0)
  chal_score_earned = models.IntegerField(default = 0)
  chal_score_lost = models.IntegerField(default = 0)
  total_score = models.IntegerField(default = 0)

class Problem(models.Model):
  name = models.CharField(max_length = 100)
  problem_text = models.TextField()
  code = models.TextField()
  start_time = models.DateTimeField(auto_now_add = True)
  end_time = models.DateTimeField(auto_now_add = True)
  code = models.TextField()

class TestCases(models.Model):
  problem = models.ForeignKey(Problem)
  input_data = models.TextField() # The input that will be given in Test Case
  output_data = models.TextField() # The Expected Output of the Test Case
  points = models.IntegerField() # The score that will be added for this case
  time_limit = models.IntegerField() # In Seconds
  is_system_test = models.BooleanField(default = False)

  '''ToDo - Impose Memory Limit'''

class Solution(models.Model):
  WAITING = 'wt'
  PROCESSING = 'pr'
  COMPILE_ERROR = 'ce'
  ACCEPTED = 'ac'
  WRONG_ANS = 'wa'
  RUNTIME_ERROR = 're'
  UNKNOWN_ERROR = 'ue'

  team = models.ForeignKey(Participant)
  problem = models.ForeignKey(Problem)
  code = models.TextField()

  ''' Currently the application only supports cpp. But in Future the Support for
  other languages should be easy to add :)'''
  language = models.CharField(max_length = 10, default = 'cpp')

  score_earned = models.IntegerField(default = 0)
  compile_throw = models.TextField()
  status = models.CharField(max_length = 10)
  score_earned = models.IntegerField(default = 0)
  submit_time = models.DateTimeField(auto_now_add = True)

class Challenge(models.Model):
  team = models.ForeignKey(Participant)
  solution = models.ForeignKey(Solution)
  input_data = models.TextField()
