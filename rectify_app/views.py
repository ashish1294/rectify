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
  context = { 'meta' : meta, 'phase' : meta.phase(), 'announcement_list' : anl }
  return render(request, 'dashboard.html', context)

def problem_list(request):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')
  meta = Metadata.get_meta_data()
  context = {
    'meta' : meta,
    'phase' : meta.phase(),
    'problem_list' : Problem.objects.all()
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

  if request.method == 'POST' and 'code_submit' in request.POST \
    and 'code' in request.POST:
    #This Means User has Submitted Code
    solution = Solution(
      participant = request.user.participant,
      problem = problem,
      code = request.POST['code'],
    )
    solution.save()
    judge_solution_easy_cases.delay(solution.id)
    return HttpResponseRedirect('/solution/' + str(solution.id))
  context = { 'problem' : problem }
  context.update(csrf(request))
  return render(request, 'solve.html', context)

def solution(request, solution_id):
  if request.user.is_authenticated() is False:
    return HttpResponseRedirect('/')
  context = {}
  try:
    context['solution'] = Solution.objects.get(
      id = int(solution_id),
      participant = request.user.participant,
    )
  except Solution.DoesNotExist, ValueError:
    pass
  return render(request, 'solution_view.html', context)
