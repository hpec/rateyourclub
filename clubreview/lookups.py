import json
from models import *
from django.http import HttpResponse
from django.db.models import Q

from selectable.base import ModelLookup
from selectable.registry import registry


class ClubLookUp(ModelLookup):
    model = Club
    search_fields = ('name__icontains', )
registry.register(ClubLookUp)


def club_lookup(request):
    result = []
    query = request.GET.get('term')
    querySet = Club.objects.all()
    for word in query.split():
        querySet = querySet.filter(Q(name__icontains=word)|Q(introduction__icontains=word))

    sorted_clubs = sorted(list(querySet), key=lambda club: -club.relevance(query))[:12]
    for club in sorted_clubs:
        result.append({'label':club.name, 'id':club.id, 'permalink':club.permalink })
    return HttpResponse(json.dumps(result), content_type="application/json")
