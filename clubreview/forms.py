from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django import forms
from models import *
from selectable.forms import AutoCompleteSelectWidget
from lookups import *

class ReviewForm(ModelForm):
    

    class Meta:
        model = Review
        fields = ('club', 'ratings', 'content')
        widgets = {'club':AutoCompleteSelectWidget(ClubLookUp)}
    

    
