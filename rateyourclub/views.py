from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, QueryDict, Http404, HttpResponse
from fb_events import *
from django.shortcuts import redirect
import os.path, requests , urllib

try:
    import simplejson as json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import json
_parse_json = json.loads


fb = FacebookGroup('')
def update_config(options):
    if os.path.isfile(settings.CONFIGURATION_YAML):
        defaults = yaml.safe_load(file(settings.CONFIGURATION_YAML,'r'))
        defaults.update(options)
        yaml.dump(defaults, file(settings.CONFIGURATION_YAML,'w') )

def facebook_auth_view(request, *args, **kwargs):
    if request.user.is_superuser or request.user.is_staff:
        if all(arg in request.GET and request.GET[arg] for arg in ('access_token',)):
            r = requests.get(fb.extended_token_url(user_access_token = request.GET['access_token']))
            if r.status_code == 200:
                params = QueryDict(r.text)
                update_config({"USER_ACCESS_TOKEN" : str(params['access_token'])})
                return HttpResponse("%s updated with %s : %s" % (os.path.basename(settings.CONFIGURATION_YAML), "USER_ACCESS_TOKEN", params['access_token'] ), content_type="text/plain")
            else:
                return HttpResponse("Error!", content_type="text/plain")
        else:
            return render_to_response("facebook_auth.html", { "login_url" : fb.login_url})
    else:
        raise Http404
