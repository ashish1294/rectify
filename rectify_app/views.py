from django.shortcuts import render
from django.template.context_processors import csrf
from forms import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from models import *
from django.http import HttpResponseRedirect
from django.db import transaction, IntegrityError
import datetime
from tasks import *
# Create your views here.

def signin(request, message_code = 0):
  if request.user.is_authenticated():
    return HttpResponseRedirect('/dashboard')
  context = {'form' : SignInForm()}
  #Adding the custom errors
  if message_code is not None:
    message_code = int(message_code)
    if message_code == 1:
      context['success'] = "User Successfully Registered :)"

  if request.method == 'POST':
    form = SignInForm(request.POST)
    if form.is_valid():
      user = authenticate(username = form.cleaned_data['user_name'],
        password = form.cleaned_data['password'])
      if user is not None:
        if user.is_active:
          login(request, user)
          return HttpResponseRedirect('/dashboard')
        else:
          #User Account is Disabled
          form.add_error(field = None, error = forms.ValidationError(('Your Account is Disabled !! Contact Admin')))
      else:
        #Invalid Login Credentials
        form.add_error(field = None, error = forms.ValidationError(('Invalid Login Credentials !! Please Try Again!!')))
    context['form'] = form
  context.update(csrf(request))
  return render(request, 'login.html', context)

def signout(request):
  if request.user.is_authenticated():
    logout(request)
  return HttpResponseRedirect('/')

def register_participant(request):
  if request.user.is_authenticated():
    return HttpResponseRedirect('/dashboard')
  if request.method == 'POST':
    form = ParticipantRegistrationForm(request.POST)
    if form.is_valid():
      #Creating New User
      try :
        # Creating Both User and Participant Inside a Transaction !!
        with transaction.atomic():
          user = User.objects.create_user(
            username = form.cleaned_data['user_name'],
            email = form.cleaned_data['email'],
            password = form.cleaned_data['password']
          )
          user.save()
          participant = Participant(
            user = user,
            name = form.cleaned_data['name'],
            college = form.cleaned_data['college'],
            contact = form.cleaned_data['contact'],
          )
          participant.save()
        return HttpResponseRedirect('/success/1')
      except IntegrityError:
        form.add_error('Error While Saving Details !!')
  else:
    form = ParticipantRegistrationForm()
  context = {'form' : form}
  context.update(csrf(request))
  return render(request, 'register_participant.html', context)

def dashboard(request):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')
  meta = Metadata.get_meta_data()
  anl = Announcements.objects.all()
  context = {
    'meta' : meta,
    'phase' : meta.phase,
    'announcement_list' : anl
  }
  return render(request, 'dashboard.html', context)

def problem_list(request):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')
  meta = Metadata.get_meta_data()
  context = {
    'meta' : meta,
    'phase' : meta.phase,
    'problem_list' : Problem.objects.all(),
  }
  return render(request, 'problem_list.html', context)

def solve(request, problem_id):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')
  meta = Metadata.get_meta_data()
  if meta.phase == meta.YET_TO_START:
    return HttpResponseRedirect('/problem_list')
  try:
    problem = Problem.objects.get(id = int(problem_id))
  except Problem.DoesNotExist, ValueError:
    return HttpResponseRedirect('/problem_list')
  meta = Metadata.get_meta_data()
  context = {
    'problem' : problem,
    'meta' : meta,
    'phase' : meta.phase,
  }

  if context['phase'] == Metadata.CODING_PHASE:
    #Coding Phase is Going On
    if request.method == 'POST' and 'code' in request.POST:
      #This Means User has Submitted Code
      with transaction.atomic():
        # Create Solution Objects in Transaction
        solution = Solution(
          participant = request.user.participant,
          problem = problem,
          code = request.POST['code'],
        )
        solution.save()

        ''' Special Note for future developers :
          All the TestCaseResult objects should be created in the HTTP request
          response cycle. The TestCaseResult in later updated with appropriate
          status and result in the background job (using celery). This is
          because user will be immediately redirected to the solution view page
          after the successful submission of task to background task broker and
          when user lands on solution view page, the TestCaseResult objects must
          exist !!
        '''

        pre_test_list = solution.problem.test_cases.filter(
          is_system_test = False)
        for pre_test in pre_test_list:
          #Result of Each Testcase is created with waiting status
          result = TestCaseResult(solution = solution, test_case = pre_test)
          result.save()
      #Pass the solution to celery workers
      judge_solution_easy_cases.delay(solution.id, False)
      return HttpResponseRedirect('/solution/' + str(solution.id))

    #Update the context because form will be displayed in coding phase
    context.update(csrf(request))
  return render(request, 'solve.html', context)

def solution(request, solution_id):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')
  meta = Metadata.get_meta_data()
  context = {'meta' : meta, 'phase' : meta.phase}
  try:
    context['solution'] = request.user.participant.solutions.get(
      id = int(solution_id))
  except Solution.DoesNotExist, ValueError:
    pass
  return render(request, 'solution_view.html', context)

def my_submissions(request):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')
  context = {
    'solution_list' : request.user.participant.solutions.order_by(
      '-submit_time'),
    'challenge_list' : request.user.participant.challenges_posted.order_by(
      '-submit_time'),
  }
  return render(request, 'mysubmissions.html', context)

def leaderboard(request):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')
  context = {'rank_list' : Participant.objects.only('name',
    'org_score').order_by('-org_score') }
  return render(request, 'leaderboard.html', context)

def hack_solutions(request):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')

  meta = Metadata.get_meta_data()
  context = { 'meta' :  meta, 'phase' : meta.phase}

  if meta.phase == meta.HACKING_PHASE:
    if request.method == 'POST':
      form = HackingRequestForm(request.POST)
      if form.is_valid():
        # User has chosen Participant and Problem
        p_id = int(form.cleaned_data['participant'])
        if p_id != request.user.participant.id:
          solution_list = Solution.objects.filter(
            participant__id = p_id,
            problem__id = int(form.cleaned_data['problem']),
            status = Solution.PRE_TEST_PASSED,
          ).order_by('-submit_time')[:1]

          if len(solution_list) is not 1:
            form.add_error(
              field = None,
              error = forms.ValidationError('This participant has not submitted any code for this problem')
            )
          elif solution_list[0].is_hacked is True:
            form.add_error(
              field = None,
              error = forms.ValidationError('This solution has already been hacked. Try Another One !!')
            )
          else:
            #A Hackable Solution is Found
            if 'input_data' in request.POST:
              #User Has Submitted a Hack
              ''' Note for future developers:
                Read the note on solve function to understand why challenge
                object should be created in HTTP cycle and not as a part of
                background task.
              '''
              challenge = Challenge(
                challenger = request.user.participant,
                solution = solution_list[0],
                input_data = form.cleaned_data['input_data']
              )
              challenge.save()
              judge_challenge.delay(challenge.id)
              return HttpResponseRedirect('/view_challenge/' + str(challenge.id))
            else:
              context['solution'] = solution_list[0]
        else:
          #User is trying to hack his/her own solution
          form.add_error(field = None, error = forms.ValidationError('You cannot hack your own solution :('))
      else:
        form.add_error(field = None, error = forms.ValidationError('Invalid Input in Form !'))
    else:
      #Simple Get Request. Send an empty form
      form = HackingRequestForm()
    context['form'] = form
  elif meta.phase < meta.HACKING_PHASE:
    context['error'] = 'Hacking phase has not started yet !!'
  else:
    context['error'] = 'Hacking phase has ended !! No More Hacks Allowed !!'

  context.update(csrf(request))
  return render(request, 'hack_solutions.html', context)

def view_challenge(request, challenge_id):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')
  context = {}
  try:
    context['challenge'] = request.user.participant.challenges_posted.get(
      id = int(challenge_id))
  except Challenge.DoesNotExist, ValueError:
    pass
  return render(request, 'view_challenge.html', context)
