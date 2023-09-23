from django import forms
from django.contrib.auth.models import Group

from .models import Profile


class AboutMeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "avatar", "bio", "agreement_accepted"


