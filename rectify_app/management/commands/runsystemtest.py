from django.core.management.base import BaseCommand, CommandError
from rectify_app.models import Solution, TestCaseResult
from rectify_app.tasks import *

class Command(BaseCommand):
  help = 'Runs the system test on all the solution'

  def add_arguments(self, parser):
    parser.add_argument('--id',
      action = 'store_true',
      dest = 'solution_id',
      default = False,
      help = 'Run system test on specific id'
    )

  def handle(self, *args, **options):

    solution_list = []
    if options['solution_id']:
      try:
        solution_list.append(Solution.objects.get(
          id = int(options['solution_id']))
        )
      except Solution.DoesNotExist, ValueError:
        self.stout.write('Invalid Solution Id')
        return
    else:
      solution_list = Solution.objects.all()

    self.stdout.write(str(len(solution_list)) + " Solutions to Judge")
    for solution in solution_list:
      '''
        Background Task run using brokers assumes that TestCaseResult objects
        already exist. So create them before passing judge task.
      '''
      sys_test_cases = solution.problem.test_cases.filter(is_system_test = True)
      self.stdout.write("Judging Solution ID - " + str(solution.id))
      for sys_test in sys_test_cases:
        result = TestCaseResult(solution = solution, test_case = sys_test)
        result.save()
      judge_solution_easy_cases.delay(solution.id, True)

    self.stdout.write('All Solutions have been queued for judging')
