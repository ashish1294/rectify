from django import forms
from django.contrib.auth.models import User
from  models import Participant, Problem
class ParticipantRegistrationForm(forms.Form):
  name = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = {
      'class' : 'form-control',
      'required' : 'required',
      'placeholder' : 'Eg. Animesh Gupta',
      'autofocus' : 'autofocus'
    }),
    max_length = 200
  )
  user_name = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = {
      'class' : 'form-control',
      'required' : 'required',
      'placeholder' : 'Eg. dark_master'
    }),
    max_length = 200,
    label = "User Name"
  )
  email = forms.EmailField(
    required = True,
    widget = forms.EmailInput(attrs = {
      'class' : 'form-control',
      'required' : 'required',
      'placeholder' : 'Eg. dark123@gmail.com'
    }),
    label = "Email Id"
  )
  college = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = {
      'class' : 'form-control',
      'required' : 'required',
      'placeholder' : 'Eg. NITK Surathkal'
    }),
    max_length = 300,
    label = "Institution"
  )
  contact = forms.IntegerField(
    required = True,
    widget = forms.NumberInput(attrs = {
      'class' : 'form-control',
      'required' : 'required',
      'placeholder' : 'Eg. 9965309653'
    }),
    label = "Phone Number"
  )
  password = forms.CharField(
    required = True,
    widget = forms.PasswordInput(attrs = {
      'class' : 'form-control',
      'required' : 'required'
    }),
    label = "Password"
  )
  con_password = forms.CharField(
    required = True,
    widget = forms.PasswordInput(attrs = {
      'class' : 'form-control',
      'required' : 'required',
    }),
    label = "Confirm Password"
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
      'class' : 'form-control',
      'placeholder' : 'User Name',
      'autofocus' : 'autofocus',
      'required' : 'required',
    }),
    max_length = 200,
    label = "User Name"
  )
  password = forms.CharField(
    required = True,
    widget = forms.PasswordInput(attrs = {
      'class' : 'form-control',
      'placeholder' : 'Password',
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
