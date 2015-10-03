from __future__ import absolute_import
from celery import shared_task
from .models import *
import time, string, random, signal, os
from django.db import transaction, IntegrityError
from django.db.models import Max

class ProcessTimeOutException(Exception):
  pass

def raise_timeout_exception():
  raise ProcessTimeOutException

@shared_task
def judge_solution_easy_cases(solution_id):
  print "Juding Solution id ", solution_id
  solution = Solution.objects.get(id = solution_id)
  result_list = solution.test_case_results.all()

  # Generating a random file name
  file_name = ''.join(random.choice(string.ascii_uppercase) for i in range(6))
  full_file_name = file_name + '.cpp'

  # Writing code to a file
  fp = open(full_file_name)
  fp.write(solution.code)
  fp.close()

  #Compiling the file
  process = subprocess.Popen(['g++', '-o', file_name, full_file_name],
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE
  )
  (output, error) = process.communicate()
  ret_code = process.poll()
  if ret_code == 0:
    #Compilation Successful
    total_score = 0
    #Max Score earned by participant for this problem
    max_score = solution.participant.solutions.filter(
      problem__id = solution.problem.id).aggregate(Max('score_earned'))['score_earned__max']
    score_earned = 0

    #Judging Each Solution
    for result in result_list:
      total_score += result.test_case.points
      proc = subprocess.Popen(['./' + file_name],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE)
      try:
        # Creating a TimeOut. SIGALRM is passed after timelimit
        signal.signal(signal.SIGALRM, raise_timeout_exception)
        signal.alarm(result.test_case.time_limit + 1)
        output = proc.communicate(stdin = result.test_case.input_data)[0]
        signal.alarm(0)
        ret_code = proc.poll()
        if ret_code < 0 :
          # Runtime Error Was Called
          result.status = TestCaseResult.RUNTIME_ERROR
        else:
          #Removing Whitespace from the output before comparing
          output = output.translate(None, string.whitespace)
          if output == result.test_case.output_data:
            result.status = TestCaseResult.ACCEPTED
            score_earned += result.test_case.points
          else:
            result.status = TestCaseResult.WRONG_ANS
      except ProcessTimeOutException:
        result.status = TestCaseResult.TIME_LIMIT_EXCEEDED
      except Exception:
        result.status = TestCaseResult.UNKNOWN_ERROR
        print "Serious Error While Judging Solution Location - 2!!"
      result.save()

    #Checking the total score earned
    solution.score_earned = score_earned
    if score_earned < total_score:
      solution.status = Solution.PRE_TEST_FAILED
    else:
      solution.status = Solution.PRE_TEST_PASSED
    solution.save()

    #Checking if we need to update participant Score
    if score_earned > max_score:
      solution.participant.main_score += score_earned - max_score
      solution.participant.org_score += score_earned - max_score
      solution.participant.save()

  else:
    #Compilation Unsuccessful
    try:
      with transaction.atomic():
        # Storing Error Message
        solution.status = Solution.COMPILE_ERROR
        solution.compile_throw = error
        solution.save()

        #Updating all the test case results
        for result in result_list:
          if result.status == result.WAITING:
            result.status = TestCaseResult.COMPILE_ERROR
            result.save()
    except IntegrityError:
      print "Serious Error While Judging Solution Location - 1!!"

  #Cleaning Up the temporary code files
  os.remove(file_name)
  os.remove(full_file_name)

def judge_challenge(challenge_id):
  print "Juding Challenge id ", challenge_id
