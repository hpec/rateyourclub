# Create your views here.
from models import *
from forms import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.contrib import messages

def club_list_view(request, template_name='club_list.html'):

    order = request.GET.get('order', '')
    query = request.GET.get('q', '')

    if order == 'name':
        order_by = 'name'
    else:
        order_by = '-hit'

    clubs = Club.objects.filter(name__icontains=query).order_by(order_by)

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
    return render_to_response(template_name, { 'clubs': clubs, 'order': order }, context_instance=context)

def club_info_view(request, club_id, template_name='club_info.html'):
    club = Club.objects.get(id=int(club_id))
    club.hit += 1
    club.save()
    events = list(club.event_set.all()[:5])
    reviews = Review.objects.filter(club=club)
    try:
        rating = int(club.review_score)*1.0 / int(club.review_count)
    except:
        rating = 0.0
    context = RequestContext(request)
    return render_to_response(template_name,
        { 'club': club, 'reviews': reviews, 'events': events, 'rating': rating }, context_instance=context)

def create_review(request):
    response = {}
    if request.method == 'POST':
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            review = form.save()
            response['status'] = 'success'
        else:
            response['status'] = 'error'
            response['error'] = form.errors
        print json.dumps(response)
    return HttpResponse(json.dumps(response), content_type="application/json")
