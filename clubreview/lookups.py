import json
from models import *
from django.http import HttpResponse

from selectable.base import ModelLookup
from selectable.registry import registry


class ClubLookUp(ModelLookup):
    model = Club
    search_fields = ('name__icontains', )
registry.register(ClubLookUp)


def club_lookup(request):
    result = []
    search_string = request.GET.get('term')
    clubs = Club.objects.filter(name__icontains=search_string)[:6]
    for club in clubs:
        result.append({'label':club.name, 'id':club.id, 'permalink':club.permalink })
    return HttpResponse(json.dumps(result), content_type="application/json")
