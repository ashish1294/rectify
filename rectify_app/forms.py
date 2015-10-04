from django import forms
from django.contrib.auth.models import User
from  models import Participant, Problem
class ParticipantRegistrationForm(forms.Form):
  name = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = {
      'class' : 'validate',
      'required' : 'required',
      'autofocus' : 'autofocus'
    }),
    max_length = 200
  )
  user_name = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = {
      'class' : 'validate',
      'required' : 'required',
    }),
    max_length = 200,
  )
  email = forms.EmailField(
    required = True,
    widget = forms.EmailInput(attrs = {
      'class' : 'validate',
      'required' : 'required',
    }),
  )
  college = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = {
      'class' : 'validate',
      'required' : 'required',
    }),
    max_length = 300,
  )
  contact = forms.IntegerField(
    required = True,
    widget = forms.NumberInput(attrs = {
      'class' : 'validate',
      'required' : 'required',
    }),
  )
  password = forms.CharField(
    required = True,
    widget = forms.PasswordInput(attrs = {
      'class' : 'validate',
      'required' : 'required'
    }),
  )
  con_password = forms.CharField(
    required = True,
    widget = forms.PasswordInput(attrs = {
      'class' : 'validate',
      'required' : 'required',
    }),
  )

  def clean(self):
    cleaned_data = super(ParticipantRegistrationForm, self).clean()

    #Checking If Password Is same as confirm password
    if 'password' in cleaned_data and 'con_password' in cleaned_data and \
      cleaned_data['con_password'] != cleaned_data['password']:
      raise forms.ValidationError(('Passwords Do Not Match'), code = 'invalid')

    #Checking if such a user exist already
    try:
      user = User.objects.get(username = cleaned_data['user_name'])
      raise forms.ValidationError(('Username Taken :('), code = 'invalid')
    except User.DoesNotExist:
      pass

    #Genuine New User.
    return self.cleaned_data

class SignInForm(forms.Form):
  user_name = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = {
      'class' : 'validate',
      'required' : 'required',
    }),
    max_length = 200,
    label = "User Name"
  )
  password = forms.CharField(
    required = True,
    widget = forms.PasswordInput(attrs = {
      'class' : 'validate',
      'required' : 'required',
    }),
    label = "Password"
  )

class HackingRequestForm(forms.Form):
  participant = forms.ChoiceField(
    required = True,
    label = "Participant"
  )
  problem = forms.ChoiceField(
    required = True,
    label = "Problem",
  )
  input_data = forms.CharField(
    required = False,
    label = "Input Data",
    widget = forms.Textarea(attrs = {'class' : 'materialize-textarea'})
  )

  def __init__(self, *args, **kwargs):
    super(HackingRequestForm, self).__init__(*args, **kwargs)
    self.fields['participant'] = forms.ChoiceField(
      choices = tuple((p.id, p.name) for p in Participant.objects.only('id',
        'name')),
      required = True,
      label = "Participant"
    )
    self.fields['problem'] = forms.ChoiceField(
      choices = tuple((p.id, p.name) for p in Problem.objects.only('id',
        'name')),
      required = True,
      label = "Problem"
    )
