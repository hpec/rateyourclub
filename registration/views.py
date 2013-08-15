from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib import messages
from forms import *
# Create your views here.

def register(request, template_name='register.html'):
    context = RequestContext(request)
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = UserCreationForm()
    return render_to_response(template_name, {'form': form}, context_instance=context)


def activate(request, activation_key,
             template_name='activate.html'):
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    user = User.objects.activate_user(activation_key)
    context = RequestContext(request)

    return render_to_response(template_name,
                              { 'user': user,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=context)


def login(request, template_name='login.html'):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, 'Logged in successfully.')
                return HttpResponseRedirect('/')
            else:
                messages.error(request, 'You have not activated your account yet.')
        else:
            messages.error(request, 'Incorrect username and password.')
            print "no user found"
            # Return an 'invalid login' error message.
    context = RequestContext(request)
    return render_to_response(template_name, context_instance=context)