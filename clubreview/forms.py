from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from models import *
class ReviewForm(ModelForm):
    class Meta:
        model = Review


    #club = selectable.forms.AutoCompleteSelectField(lookup_class=ClubLookup,
    #                                                allow_new=True,
    #                                                require=False,
    #                                                label=_(u'Club name'))
