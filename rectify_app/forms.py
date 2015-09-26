from django import forms

class ParticipantRegistrationForm(forms.Form):

  iattr = {'class' : 'form-control'}
  name = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = iattr),
    max_length = 200
  )
  user_name = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = iattr),
    max_length = 200,
    label = "User Name"
  )
  email = forms.CharField(
    required = True,
    widget = forms.EmailInput(attrs = iattr),
    label = "Email Id"
  )
  college = forms.CharField(
    required = True,
    widget = forms.TextInput(attrs = iattr),
    max_length = 300,
    label = "Institution"
  )
  contact = forms.IntegerField(
    required = True,
    widget = forms.NumberInput(attrs = iattr),
    label = "Phone Number"
  )
  password = forms.CharField(
    required = True,
    widget = forms.PasswordInput(attrs = iattr),
    label = "Password"
  )
  con_password = forms.CharField(
    required = True,
    widget = forms.PasswordInput(attrs = iattr),
    label = "Confirm Password"
  )

  def clean(self):
    cleaned_data = super(ParticipantRegistrationForm, self).clean()
    print cleaned_data
    #if cleaned_data['con_password'] != cleaned_data['password']:
    #  raise forms.ValidationError("Passwords Do Not Match")
    return self.cleaned_data
