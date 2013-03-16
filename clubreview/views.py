# Create your views here.
from models import *
from forms import *
from django.shortcuts import render_to_response
from django.template import RequestContext

def club_list_view(request, template_name='club_list.html'):
    clubs = Club.objects.all().order_by('review_count')
    return render_to_response(template_name, { 'clubs': clubs })

def club_info_view(request, club_id, template_name='club_info.html'):
    club = Club.objects.get(id=int(club_id))
    reviews = Review.objects.filter(club=club)
    return render_to_response(template_name, { 'club': club, 'reviews': reviews })

def add_review(request, success_url=None,
               form_class=ReviewForm,
               template_name='add_review.html'):
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            form.save()
        pass
    else:
        form = form_class()

    context = RequestContext(request)
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context) 