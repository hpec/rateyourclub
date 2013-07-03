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
                   'ratings': None,
                   'content': Textarea(attrs={'cols': 20, 'rows': 5})
                   }
    class Media:
        css = {
            'all': ()
        }

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        try:
            self.ratings = max(map(int, kwargs['data']['rating']))
        except KeyError:
            pass

    def clean_ratings(self):
        self.cleaned_data['ratings'] = self.ratings
        if not (self.cleaned_data['ratings'] <=5 and self.cleaned_data['ratings'] >=1):
            raise forms.ValidationError('illegal ratings')
        return self.cleaned_data['ratings']




