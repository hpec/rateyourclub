import itertools

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson

from models import *
from forms import *

def club_list_view(request, template_name='club_list.html'):
    order = request.GET.get('order', '')
    query = request.GET.get('q', '')

    order_by = 'name' if order == 'name' else '-hit'

    clubs = Club.objects.all().order_by(order_by)
    for word in query.split():
        clubs = clubs.filter(Q(name__icontains=word)|Q(introduction__icontains=word))

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

@login_required
def club_info_view(request, club_id, template_name='club_info.html'):
    club = get_object_or_404(Club, permalink=club_id)
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

@login_required
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
    return HttpResponse(json.dumps(response), content_type="application/json")
def add_url_edit(request, id):
    if request.method == 'POST':
        club = get_object_or_404(Club, pk=id)
        c1, c2 = None, None
        to_json = {}
        errors = []
        success_messages = []
        if request.POST['facebook_url']:
            c1 = ClubURIEdit(club=club)
            c1.value = request.POST['facebook_url']
            c1.attribute_type = ClubURIEdit.FACEBOOK_URL_TYPE
            try:
                c1_errors = None
                c1.full_clean()
            except ValidationError as e:
                c1_errors = []
                value_error = e.message_dict.pop('value', None)
                if value_error:
                    c1_errors.append(["Please enter a valid facebook url"])
                c1_errors.append(itertools.chain(e.message_dict.values()))
                errors.append(itertools.chain(*c1_errors))
            if not c1_errors:
                success_messages.append('Added facebook url: %s' % c1.value)
        if request.POST['website_url']:
            c2 = ClubURIEdit(club=club)
            c2.value = request.POST['website_url']
            c2.attribute_type = ClubURIEdit.WEBSITE_URL_TYPE
            try:
                c2_errors = None
                c2.full_clean()
            except ValidationError as e:
                c2_errors = []
                value_error = e.message_dict.pop('value', None)
                if value_error:
                    c2_errors.append(["Please enter a valid website url"])
                c2_errors.append(itertools.chain(e.message_dict.values()))
                errors.append(itertools.chain(*c2_errors))
            if not c2_errors:
                success_messages.append('Added website url: %s' % c2.value)
        if len(errors) > 0:
            to_json['message'] = ', '.join(itertools.chain(*errors))
            return HttpResponse(content=simplejson.dumps(to_json), mimetype='application/json', status=422)
        elif any([c1,c2]):
            if c1:
                c1.save()
            if c2:
                c2.save()
            to_json['message'] = ', '.join(success_messages)
            return HttpResponse(content=simplejson.dumps(to_json), mimetype='application/json')
        else:
            to_json['message'] = 'Facebook and/or website urls expected'
            return HttpResponse(content=simplejson.dumps(to_json), mimetype='application/json', status=422)
    else :
        raise Http404
