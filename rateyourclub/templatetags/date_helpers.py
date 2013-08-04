from django import template
from datetime import datetime
import pdb
register = template.Library()
@register.filter(name='year_and_current_year')
def year_and_current_year(value):
    current_year = datetime.now().year
    return (value,current_year)
