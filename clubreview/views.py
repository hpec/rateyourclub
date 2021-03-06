import datetime
import itertools
import urllib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson

from registration.models import Subscription
from decorators import *
from models import *
from forms import *

def landing(request, template_name = 'landing.html' ):
    context = RequestContext(request)
    return render_to_response(template_name, { }, context_instance=context)

def club_list_view(request, template_name='club_list.html'):
    order_mapping = {'name':'name', 'ratings':'-average_rating', 'pop':'-hit'}

    order = request.GET.get('order', 'ratings')
    query = request.GET.get('q', '')
    category = urllib.unquote(request.GET.get('cat', '')).decode('utf-8')

    clubs = Club.objects.all()
    if category: clubs = Club.objects.filter(categories__name=category)
    if order == 'ratings': clubs = clubs.rated()
    clubs = clubs.order_by(order_mapping[order], '-hit', 'name') # break tie by hit then name
    for word in query.split():
        clubs = clubs.filter(Q(name__icontains=word)|Q(introduction__icontains=word))

    paginator = Paginator(clubs, 10) # Show 10 clubs per page

    page = request.GET.get('page')
    try:
        clubs = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        clubs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        clubs = paginator.page(paginator.num_pages)

    categories = Category.objects.order_by('name')
    events = Event.objects.filter(start_time__gt=datetime.datetime.now()).order_by('start_time')[:5]
    return render_to_response(
        template_name,
        { 'clubs': clubs, 'order': order , 'categories': categories, 'events': events },
        context_instance=RequestContext(request)
    )

def club_info_view(request, club_id, template_name='club_info.html'):
    club = get_object_or_404(Club, permalink=club_id)
    club.hit += 1
    club.save()
    events = club.display_events(6)
    reviews = Review.objects.filter(club=club, is_deleted=False)
    try:
        rating = int(club.review_score)*1.0 / int(club.review_count)
    except:
        rating = 0.0
    context = RequestContext(request)
    if request.user.is_authenticated():
        context['subscribed'] = Subscription.objects.filter(club=club, user=request.user).count() > 0
    return render_to_response(template_name,
        { 'club': club, 'reviews': reviews, 'events': events, 'rating': rating, 'related_clubs': Club.objects.get_related_clubs(club) }, context_instance=context)


def event_info_view(request, event_id, template_name='event_info.html'):
    event = get_object_or_404(Event, id=event_id)
    return render_to_response(template_name, {'event':event}, context_instance=RequestContext(request))

def event_ical_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    response = HttpResponse(event.ical(), mimetype="text/calendar")
    response['Content-Disposition'] = 'attachment; filename=%s.ics' % event.name
    return response

@login_required
def create_review(request):
    response = {}
    if request.method == 'POST':
        form = ReviewForm(user=request.user, data=request.POST)
        if form.is_valid():
            review = form.save()
            status = 201
            messages.success(request, 'Review submitted!')
        else:
            status = 406
            response['error'] = 'Content cannot be blank'
    return HttpResponse(json.dumps(response), content_type="application/json", status=status)

@login_required
def delete_review(request, id):
    try:
        review = Review.objects.get(id=id)
        if not review.is_deleted and (review.user == request.user or request.user.is_staff):
            review.is_deleted = True
            club = review.club
            club.review_count -= 1
            club.review_score -= review.ratings
            review.save()
            club.save()
            messages.success(request, 'Successfully deleted your review')
        else:
            messages.error(request, "You can only delete your own review!")
    except Review.DoesNotExist:
        messages.error(request, 'The review that you are trying to delete does not exist')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def undelete_review(request, id):
    try:
        review = Review.objects.get(id=id)
        if review.is_deleted and (review.user == request.user or request.user.is_staff):
            review.is_deleted = False
            club = review.club
            club.review_count += 1
            club.review_score += review.ratings
            review.save()
            club.save()
            messages.success(request, 'Successfully restored your review')
        else:
            messages.error(request, "You can only restore your own review!")
    except Review.DoesNotExist:
        messages.error(request, 'The review that you are trying to delete does not exist')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

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


@login_required
def review_list(request):
    if request.user.is_staff:
        return render_to_response('review_list.html', { 'reviews' : Review.objects.all() })
    else:
        messages.error(request, "You are not allowed to view this page")
        try:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        except KeyError:
            return HttpResponseRedirect('/')

@ajax_login_required
def subscribe_club(request, club_id):
    user = request.user
    club = get_object_or_404(Club, id=club_id)
    try:
        subscription = Subscription.objects.create(user=user, club=club)
    except IntegrityError, e:
        print e
    if request.is_ajax():
        return HttpResponse()
    else:
        return HttpResponseRedirect(reverse('club_info_view', args=[club.permalink]))

@ajax_login_required
def unsubscribe_club(request, club_id):
    user = request.user
    club = get_object_or_404(Club, id=club_id)
    subscription = Subscription.objects.get(user_id=user.id, club=club)
    subscription.delete()
    if request.is_ajax():
        return HttpResponse()
    else:
        return HttpResponseRedirect(reverse('club_info_view', args=[club.permalink]))

