from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import simplejson

from functools import wraps

def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        json = simplejson.dumps({ 'not_authenticated': True, 'redirect':reverse('login') + '?next=' + request.path })
        messages.info(request, "Login to access more features!")
        return HttpResponse(json, mimetype='application/json')
    return wrapper
