import re

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect

from models import *


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
        domain = email.split('@')[1]
        if not re.search(r'berkeley.edu$', domain):
            raise forms.ValidationError("Must use berkeley.edu email")

        try:
            User.objects.get(email=email)
            raise forms.ValidationError("The email address is already in use")
        except User.DoesNotExist:
            pass

        return self.cleaned_data['email']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean(self):
        print self.cleaned_data
        invitation_key = self.cleaned_data['invitation_key']
        if invitation_key:
            SHA1_RE = re.compile('^[a-f0-9]{40}$')
            if not SHA1_RE.search(activation_key):
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


class MyUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'screen_name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('screen_name',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'screen_name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(User, MyUserAdmin)
# ... and, since we're not using Django's builtin permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)