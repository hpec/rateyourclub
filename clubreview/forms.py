from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django import forms
from models import *
from selectable.forms import AutoCompleteSelectField
from lookups import *
from django.forms.widgets import *

class ReviewForm(forms.Form):

    # class Meta:
    #     model = Review
    #     fields = ('club', 'content')
    #     widgets = {'club': AutoCompleteSelectWidget(ClubLookUp),
    #                'content': Textarea(attrs={'cols': 20, 'rows': 5})
    #                }
    # class Media:
    #     css = {
    #         'all': ()
    #     }
    club = AutoCompleteSelectField(required=True,
        lookup_class=ClubLookUp)

    content = forms.CharField(required=True,
        widget=Textarea(attrs={'cols': 20, 'rows': 5}))

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        try:
            self.ratings = kwargs['data']['rating-val']
        except KeyError:
            pass

    def clean(self):
        try:
            self.cleaned_data['ratings'] = int(self.ratings)
        except ValueError:
            raise forms.ValidationError('illegal ratings')
        if not (self.cleaned_data['ratings'] <=5 and self.cleaned_data['ratings'] >=1):
            raise forms.ValidationError('illegal ratings')

        return self.cleaned_data

    def save(self):
        review = Review(club=self.cleaned_data['club'],
            content=self.cleaned_data['content'],
            ratings=self.cleaned_data['ratings'])
        review.save()


