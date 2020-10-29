from django import forms 
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import Profile
from django.forms import ModelForm
  
class UserRegisterForm(UserCreationForm): 
    email = forms.EmailField() 
    class Meta: 
        model = User 
        fields = ['username','email', 'password1', 'password2'] 


    def save(self,commit=True):
    	user=super(UserRegisterForm,self).save(commit=False)
    	user.email=self.cleaned_data['email']

    	if commit:
    		user.save()
    	return user



class EditProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('user'),


class UserProfileForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('username','email')
