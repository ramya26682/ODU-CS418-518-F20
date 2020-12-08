from django import forms 
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import Profile,search_history
from django.forms import ModelForm
from django.core.paginator import Paginator, Page
  
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


class SearchHistoryForm(forms.ModelForm):
    class Meta:
        model=search_history
        fields=('username','search')




class DSEPaginator(Paginator):
    """
    Override Django's built-in Paginator class to take in a count/total number of items;
    Elasticsearch provides the total as a part of the query results, so we can minimize hits.
    """
    def __init__(self, *args, **kwargs):
        super(DSEPaginator, self).__init__(*args, **kwargs)
        self._count = self.object_list.hits.total

    def page(self, number):
        # this is overridden to prevent any slicing of the object_list - Elasticsearch has
        # returned the sliced data already.
        number = self.validate_number(number)
        return Page(self.object_list, number, self)


class DSEPaginator(Paginator):
    """
    Override Django's built-in Paginator class to take in a count/total number of items;
    Elasticsearch provides the total as a part of the query results, so we can minimize hits.
    """
    def __init__(self, *args, **kwargs):
        super(DSEPaginator, self).__init__(*args, **kwargs)
        self._count = self.object_list.hits.total

    def page(self, number):
        # this is overridden to prevent any slicing of the object_list - Elasticsearch has
        # returned the sliced data already.
        number = self.validate_number(number)
        return Page(self.object_list, number, self)