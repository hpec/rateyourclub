from django import template
from django.contrib import messages
from django.http import HttpResponseRedirect

from hamlpy import hamlpy

from clubreview.forms import *


register = template.Library()


@register.inclusion_tag('review_form.html', takes_context=True)
def review_form_handler(context):
    #print context
    initials = {}
    if 'club' in context:
        initials['club'] = context['club']
    request = context['request']
    if request.method == 'POST':
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review submitted successfully')
            print "Validation Successful!"
        else:
            messages.error(request, 'Form Error')
            print "Form Error"
            print form.errors
        return {'form':form} #HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = ReviewForm(initial=initials)
    return {'form':form}


#t = get_template('review_form.html')
#register.inclusion_tag(t)(review_form_handler, takes_context=True)