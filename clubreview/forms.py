from django.utils.translation import ugettext_lazy as _
from django import forms
from models import *
from selectable.forms import AutoCompleteSelectField
from lookups import *
from django.forms.widgets import *

class ReviewForm(forms.Form):

    club = AutoCompleteSelectField(required=False,
        lookup_class=ClubLookUp)

    content = forms.CharField(required=True,
        widget=Textarea(attrs={'cols': 20, 'rows': 5}))

    def __init__(self, user=None, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        try:
            self.ratings = kwargs['data']['rating-val']
            self.club_id = kwargs['data']['club_id']
            self.user = user
        except KeyError:
            pass

    def clean_club(self):
        print "cleaning club"
        try:
            club = Club.objects.get(id=self.club_id)
            self.cleaned_data['club'] = club
        except:
            pass
        return self.cleaned_data['club']

    def clean(self):
        try:
            self.cleaned_data['ratings'] = int(self.ratings)
        except ValueError:
            raise forms.ValidationError('illegal ratings')
        if not (self.cleaned_data['ratings'] <=5 and self.cleaned_data['ratings'] >=1):
            raise forms.ValidationError('illegal ratings')

        return self.cleaned_data

    def save(self):
        club = self.cleaned_data['club']
        review = Review(club=club, user=self.user,
            content=self.cleaned_data['content'],
            ratings=self.cleaned_data['ratings'])
        club.review_count += 1
        club.review_score += int(self.ratings)

        club.save()
        review.save()
        return review

class ClubEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ClubEditForm, self).__init__(*args, **kwargs)
    def clean(self):
        pass
    def save(self):
        club_edit = ClubEdit(club=club,attribute_type=self.cleaned_data['value'],value=self.cleaned_data['value'])
        club_edit.save()
        pass

