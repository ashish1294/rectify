from __future__ import absolute_import
from celery import shared_task
from .models import *
import time

@shared_task
def add(x, y):
  print "Add Task Received"
  return x + y

@shared_task
def judge_solution_easy_cases(solution_id):
  print "Juding Solution id ", solution_id
  solution = Solution.objects.get(id = solution_id)
  pre_test_list = solution.problem.test_cases.filter(is_system_test = False)
  total_score = 0
  max_score = 0
  #Judging Solution on Each test case
  for pre_test in pre_test_list:
    time.sleep(10)
    result = TestCaseResult.objects.get(
      solution = solution,
      test_case = pre_test,
    )
    if result.status == result.WAITING:
      #Judge the solution against pre_test Here

      #Change the result status as obtained by judging the solution
      result.status = result.ACCEPTED
    result.save()
    total_score += result.test_case.points

  #Updating the total Scored Earned
  solution.score_earned = total_score
  solution.save()
