from django.shortcuts import render
from django.template.context_processors import csrf
from forms import *
from django.contrib.auth.models import User
# Create your views here.

def signin(request):
  return render(request, 'login.html', {})

def register_participant(request):

  if request.method == 'POST':
    print request.POST
    form = ParticipantRegistrationForm(request.POST)
    if form.is_valid():
      print "Valid Form = ", form.cleaned_data
  else:
    form = ParticipantRegistrationForm()
  context = {}
  context.update(csrf(request))
  return render(request, 'register_participant.html', {'form' : form})
