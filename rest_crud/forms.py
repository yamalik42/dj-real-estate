from django.forms import ModelForm
from .models import Profile
from django.contrib.auth.models import User


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')
