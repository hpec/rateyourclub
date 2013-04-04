from models import *
from selectable.base import ModelLookup
from selectable.registry import registry

class ClubLookUp(ModelLookup):
    model = Club
    search_fields = ('name__icontains', )
registry.register(ClubLookUp)