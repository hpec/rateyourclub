# Create your views here.
from models import *
from forms import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib import messages



def club_list_view(request, template_name='club_list.html'):

    if request.method == 'GET' and 'q' in request.GET:
        clubs = Club.objects.filter(name__icontains=request.GET.get('q')).order_by('review_count')
    else:
        clubs = Club.objects.all().order_by('review_count')
    paginator = Paginator(clubs, 25) # Show 25 clubs per page

    page = request.GET.get('page')
    try:
        clubs = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        clubs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        clubs = paginator.page(paginator.num_pages)
    context = RequestContext(request)
    messages.add_message(request, messages.INFO, 'Hello world.')
    return render_to_response(template_name, { 'clubs': clubs }, context_instance=context)

def club_info_view(request, club_id, template_name='club_info.html'):
    club = Club.objects.get(id=int(club_id))
    reviews = Review.objects.filter(club=club)
    context = RequestContext(request)
    return render_to_response(template_name, { 'club': club, 'reviews': reviews }, context_instance=context)

def add_review(request, success_url=None,
               form_class=ReviewForm,
               template_name='add_review.html'):
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            review = form.save()
            print "Validation Successful!"
            return HttpResponseRedirect('/')
        else:
            print "Form Error"
    else:
        form = form_class()
    context = RequestContext(request)
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)



