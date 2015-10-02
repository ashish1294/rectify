from __future__ import absolute_import
from celery import shared_task
from models import *
@shared_task
def add(x, y):
  print "Add Task Received"
  return x + y

@shared_task
def judge_solution_easy_cases(solution_id):

