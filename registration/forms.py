import re

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect

from models import *


def check_email_domain(email):
    domain = email.split('@')[1]
    return re.search(r'berkeley.edu$', domain)

class UserCreationForm(forms.Form):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    email = forms.EmailField(label='Email')
    screen_name = forms.CharField(label='Screen Name')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    invitation_key = forms.CharField(label='', widget=forms.HiddenInput, required=False)


    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not check_email_domain(email):
            raise forms.ValidationError("Must use berkeley.edu email")

        try:
            User.objects.get(email=email)
            raise forms.ValidationError("The email address is already in use")
        except User.DoesNotExist:
            pass

        return self.cleaned_data['email']

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 6:
            raise forms.ValidationError("Password must be at least 6 characters")
        return password1

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean(self):
        invitation_key = self.cleaned_data['invitation_key']
        if invitation_key:
            if not valid_hash(invitation_key):
                raise forms.ValidationError("Invalid Inivitation")

            try:
                invitation = Invitation.objects.get(invitation_key=invitation_key)
            except Invitation.DoesNotExist:
                raise forms.ValidationError("Invalid Inivitation")

            if 'email' in self.cleaned_data and invitation.email != self.cleaned_data['email']:
                raise forms.ValidationError("Invalid Inivitation")

            self.cleaned_data['email'] = invitation.email

        return self.cleaned_data

    def save(self, commit=True):
        if self.cleaned_data['invitation_key']:
            user = User.objects.create_user(email=self.cleaned_data['email'], screen_name=self.cleaned_data['screen_name'],
                password=self.cleaned_data['password1'])
        else:
            user = User.objects.create_inactive_user(email=self.cleaned_data['email'], screen_name=self.cleaned_data['screen_name'],
                password=self.cleaned_data['password1'])

        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'password', 'screen_name', 'is_active', 'is_admin']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


