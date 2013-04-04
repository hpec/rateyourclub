from django import template
from clubreview.forms import *
from django.http import HttpResponseRedirect
from hamlpy import hamlpy

register = template.Library()


@register.inclusion_tag('review_form.html', takes_context=True)
def review_form_handler(context):
    print context
    request = context['request']
    if request.method == 'POST':
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/')
    else:
        form = ReviewForm()
    return {'form':form}


#t = get_template('review_form.html')
#register.inclusion_tag(t)(review_form_handler, takes_context=True)