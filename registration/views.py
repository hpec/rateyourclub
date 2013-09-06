from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from forms import *
from models import *

def register(request, template_name='register.html'):
    context = RequestContext(request)
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            if user.is_active:
                user = authenticate(username=request.POST['email'], password=request.POST['password1'])
                auth_login(request, user)
                messages.success(request, "You have successfully created your account!")
            else:
                messages.success(request, "You have successfully created your account! Please check your email and confirm your registration.")
            return HttpResponseRedirect('/clubs/')
        else:
            pass
            # for field, error in form.errors.items():
            #     messages.error(request, "{0}: {1}".format(field, form.errors[field]))
    else:
        invitation_key = request.GET.get('invitation', None)
        initial = {}
        if valid_hash(invitation_key):
            try:
                invitation = Invitation.objects.get(invitation_key=invitation_key)
                initial['email'] = invitation.email
                initial['invitation_key'] = invitation_key
            except Invitation.DoesNotExist:
                messages.error(request, "Invalid Invitation")
                return HttpResponseRedirect('/accounts/register/')

        form = UserCreationForm(initial=initial)

    return render_to_response(template_name, {'form': form}, context_instance=context)


def activate(request, activation_key,
             template_name='activate.html'):
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    user = User.objects.activate_user(activation_key)
    context = RequestContext(request)
    messages.success(request, 'Your account is activated!')

    return render_to_response(template_name,
                              { 'user': user,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=context)

@login_required
def invite(request, template_name='invite.html'):
    if request.method == 'POST':
        email = request.POST.get('email')
        if check_email_domain(email):
            invitation = User.objects.create_invitation(email)
            User.objects.send_invitation_email(invitation, request.user)
            messages.success(request, 'Invitation sent successfully!')
        else:
            messages.error(request, 'You can only send invitation to @berkeley.edu')

    context = RequestContext(request)
    return render_to_response(template_name, context_instance=context)


def login(request, template_name='login.html'):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, 'Logged in successfully.')
                next_url = request.REQUEST.get('next', None)
                return HttpResponseRedirect(next_url) if next_url else HttpResponseRedirect('/clubs/')
            else:
                messages.error(request, 'You have not activated your account yet. Please check your email and confirm your registration.')
        else:
            messages.error(request, 'Incorrect username and password.')

    context = RequestContext(request)
    return render_to_response(template_name, context_instance=context)

def logout(request):
    auth_logout(request)
    messages.info(request, 'You have successfully logged out.')
    return HttpResponseRedirect('/')

