from __future__ import absolute_import
from celery import shared_task
from .models import *
import time, string, random, signal, os, subprocess
from django.db import transaction, IntegrityError
from django.db.models import Max

'''
  This file contains the background jobs that will be executed separately from
  the HTTP Request - Response Cycle. Judging Solutions might take some time and
  we cannot expect user to wait for the HttpResponse that long.
'''

# Custom Exception for simulating Timeout
class ProcessTimeOutException(Exception):
  ''' Note to future developers:
    This Exception is created to simulate the timeout period for the running of
    solution. Given the time I (Ashish Kedia) had to develop this application I
    could not find a better solution for implementing a timeout mechanism for
    subprocesses that will execute the user's submitted code.

    This method uses the SIGALRM signal on Unix platforms which raises an ALARM
    signal after a given period of time. So just before executing user's code we
    set the alarm period. If the alarm is triggered the raise_timeout_exception
    function is called which in turn raises this exception. This exception can
    then be easily caught to determine if TIME LIMIT EXCEEDED Error has occurred
  '''
  pass

def raise_timeout_exception(signum, frame):
  raise ProcessTimeOutException('Process Has Timed Out')

@shared_task
def judge_solution_easy_cases(solution_id, is_system_test = False):
  '''
    This background task accepts two parameters - solution_id and is_system_test
    is_system_test ensures that this same task can be used for both normal
    pre test and system test which will be run at the end of the contest.
  '''
  solution = Solution.objects.get(id = solution_id)
  result_list = solution.test_case_results.all()

  # Generating a random file name
  file_name = ''.join(random.choice(string.ascii_uppercase) for i in range(6))
  full_file_name = file_name + '.cpp'

  # Writing code to a file
  fp = open(full_file_name, 'w+')
  fp.write(solution.code)
  fp.flush()
  fp.close()

  #Compiling the file
  try:
    signal.signal(signal.SIGALRM, raise_timeout_exception)
    signal.alarm(5)
    process = subprocess.Popen(['g++', '-o', file_name, full_file_name],
      stdin = subprocess.PIPE,
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE
    )
    (output, error) = process.communicate()
    signal.alarm(0)
    ret_code = process.poll()
  except ProcessTimeOutException:
    ret_code = -1
    error = "The code compilation is timed - out :( Try with optimizing code"

  if ret_code is not 0:
    #Compilation Unsuccessful
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

  else:
    # Now Run All Test Cases
    # Total Scores that a participant can earn
    total_score = 0
    #Max Score earned by participant for this problem
    max_score = solution.participant.solutions.filter(
      problem__id = solution.problem.id).aggregate(
        Max('score_earned'))['score_earned__max']
    score_earned = 0

    #Judging Each Solution
    for result in result_list:
      total_score += result.test_case.points
      if result.status == TestCaseResult.WAITING:
        try:
          # Creating a TimeOut. SIGALRM is passed after timelimit
          signal.signal(signal.SIGALRM, raise_timeout_exception)
          signal.alarm(solution.problem.time_limit + 1)
          proc = subprocess.Popen(['./' + file_name],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE)
          output = proc.communicate(input = str(result.test_case.input_data))[0]
          signal.alarm(0)
          ret_code = proc.poll()
          if ret_code is None or ret_code < 0 :
            # Runtime Error Was Called
            result.status = TestCaseResult.RUNTIME_ERROR
          else:
            #Removing Whitespace from the output before comparing
            output = str(output).translate(None, string.whitespace)
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
      elif result.status == TestCaseResult.ACCEPTED:
        score_earned += result.test_case.points

    #Checking the total score earned
    solution.score_earned = score_earned
    if score_earned < total_score:
      if is_system_test is False:
        solution.status = Solution.PRE_TEST_FAILED
      else:
        solution.status = Solution.SYS_TEST_FAILED
    else:
      if is_system_test is False:
        solution.status = Solution.PRE_TEST_PASSED
      else:
        solution.status = Solution.SYS_TEST_PASSED
    solution.save()

    # Checking if we need to update participant Score
    # User might have already solved this problem before !!
    if score_earned > max_score:
      solution.participant.main_score += score_earned - max_score
      solution.participant.org_score += score_earned - max_score
      solution.participant.save()

    # Cleaning Up the temporary code files
    os.remove(file_name)
  os.remove(full_file_name)

@shared_task
def judge_challenge(challenge_id):
  challenge = Challenge.objects.get(id = challenge_id)

  # Generating a random file name for problem setter's source code
  file_name_ps = ''.join(random.choice(string.ascii_uppercase) for i in range(6))
  full_file_name_ps = file_name_ps + '.cpp'

  fp = open(full_file_name_ps, 'w+')
  fp.write(challenge.solution.problem.correct_code)
  fp.close()

  process = subprocess.Popen(['g++', '-o', file_name_ps, full_file_name_ps],
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE
  )
  (output, error) = process.communicate()

  #Cleaning Problem Setter's Code
  os.remove(full_file_name_ps)

  try:
    # Creating a TimeOut. SIGALRM is passed after timelimit
    signal.signal(signal.SIGALRM, raise_timeout_exception)
    signal.alarm(challenge.solution.problem.time_limit + 1)
    proc = subprocess.Popen(['./' + file_name_ps],
      stdin = subprocess.PIPE,
      stdout = subprocess.PIPE)
    expected_output = proc.communicate(input = challenge.input_data)[0]
    signal.alarm(0)
    expected_output = str(expected_output).translate(None, string.whitespace)
    ret_code = proc.poll()
    if ret_code is None or ret_code != 0:
      challenge.status = Challenge.INVALID_INPUT
    else:
      # Cleaning Problem Setter's Binary
      os.remove(file_name_ps)
  except ProcessTimeOutException:
    challenge.status = Challenge.INVALID_INPUT

  if challenge.status != Challenge.INVALID_INPUT:
    # Generating a random file name for solution source code
    file_name = ''.join(random.choice(string.ascii_uppercase) for i in range(6))
    full_file_name = file_name + '.cpp'

    # Writing solution code to a file
    fp = open(full_file_name, 'w+')
    fp.write(challenge.solution.code)
    fp.close()

    # Compiling the solution source code
    process = subprocess.Popen(['g++', '-o', file_name, full_file_name],
      stdin = subprocess.PIPE,
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE
    )
    (output, error) = process.communicate()
    #Cleaning Solution Code
    os.remove(full_file_name)

    try:
      # Creating a TimeOut. SIGALRM is passed after timelimit
      signal.signal(signal.SIGALRM, raise_timeout_exception)
      signal.alarm(challenge.solution.problem.time_limit + 1)
      proc = subprocess.Popen(['./' + file_name],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE)
      obtained_output = proc.communicate(input = challenge.input_data)[0]
      signal.alarm(0)
      obtained_output = str(obtained_output).translate(None, string.whitespace)
      ret_code = proc.poll()
      if ret_code == 0:
        #Cleaning Up Binary
        os.remove(file_name)
      if ret_code == 0 and obtained_output == expected_output:
        challenge.status = Challenge.FAILED
      else:
        challenge.status = Challenge.SUCCESSFUL
    except ProcessTimeOutException:
      challenge.status = Challenge.SUCCESSFUL

  # Updating objects based on the result
  # Change these contests if you want to change the score for challenge
  if challenge.status == Challenge.SUCCESSFUL:
    challenge.solution.participant.chal_score_lost += 50
    challenge.solution.participant.org_score -= 50
    challenge.solution.participant.save()
    challenge.solution.is_hacked = True
    challenge.solution.save()
    challenge.challenger.chal_score_earned += 50
    challenge.challenger.org_score += 50
  else:
    challenge.challenger.chal_score_earned -= 25
    challenge.challenger.org_score -= 25
  challenge.challenger.save()
  challenge.save()
