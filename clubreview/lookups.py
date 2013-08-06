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
    for club in Club.objects.filter(name__icontains=search_string):
        result.append({'label':club.name, 'id':club.id})
    return HttpResponse(json.dumps(result), content_type="application/json")
