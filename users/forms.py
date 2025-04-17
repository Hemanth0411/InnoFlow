from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserProfile

class UserProfileCreationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'first_name', 'last_name')

class UserProfileChangeForm(UserChangeForm):
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'bio', 'position', 'company', 'date_of_birth', 'phone_number')