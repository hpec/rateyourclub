from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django import forms
from models import *
from selectable.forms import AutoCompleteSelectWidget
from lookups import *
from django.forms.widgets import *

class ReviewForm(ModelForm):
    

    class Meta:
        model = Review
        fields = ('club', 'content')
        widgets = {'club': AutoCompleteSelectWidget(ClubLookUp),
                   # 'ratings': TextInput(),
                   'content': Textarea(attrs={'cols': 20, 'rows': 5})
                   }
    class Media:
        css = {
            'all': ()
        }
    

    
