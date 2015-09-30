from django.shortcuts import render
from django.template.context_processors import csrf
from forms import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from models import *
from django.http import HttpResponseRedirect
# Create your views here.

def signin(request, message_code = 0):
  if request.user.is_authenticated():
    logout(request)
    print "Authenticate User - ", request.user
    return HttpResponseRedirect('/dashboard')
  context = {'form' : SignInForm()}
  #Adding the custom errors
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
        else:
          #User Account is Disabled
          form.add_error(field = None, error = 'Your Account is Diabled !! Contact Admin')
      else:
        #Invalid Login Credentials
        print "Un ss"
        form.add_error(('Invalid Login Credentials!! Please Try Again'))
    context['form'] = form
  context.update(csrf(request))
  return render(request, 'login.html', context)

def register_participant(request):
  if request.user.is_authenticated():
    return HttpResponseRedirect('/dashboard')
  if request.method == 'POST':
    form = ParticipantRegistrationForm(request.POST)
    if form.is_valid():
      #Creating New User
      user = User(
        form.cleaned_data['user_name'],
        form.cleaned_data['email'],
        form.cleaned_data['password']
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
  else:
    form = ParticipantRegistrationForm()
  context = {}
  context.update(csrf(request))
  return render(request, 'register_participant.html', {'form' : form})
