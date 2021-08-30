from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from. models import Account

class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password',
        'class':'form-control'
    }))

    repeat_password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Repeat password',
        'class':'form-control'
    }))
       
    class Meta:
        model=Account
        fields=['first_name','last_name','email','phone_number','password']
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            placeholder='Enter '
            self.fields[field].widget.attrs['class']='form-control'
            placeholder=placeholder+str(field)
            placeholder=placeholder.replace('_',' ')
            self.fields[field].widget.attrs['placeholder']=placeholder

    def clean(self):
        cleaned_data=super(RegistrationForm,self).clean()
        password1=cleaned_data.get('password')
        password2=cleaned_data.get('repeat_password')

        if password1!=password2:
            raise forms.ValidationError('The password must be the same')

class LoginForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=['email','password']

            

