# Create your views here.
from models import *
from django.shortcuts import render_to_response

def club_list_view(request, template_name='club_list.html'):
    clubs = Club.objects.all().order_by('review_count')
    return render_to_response(template_name, { 'clubs': clubs })

def club_info_view(request, club_id, template_name='club_info.html'):
    club = Club.objects.get(id=int(club_id))
    reviews = Review.objects.filter(club=club)
    return render_to_response(template_name, { 'club': club, 'reviews': reviews })
