from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
import urllib2, urllib, requests, urlparse, re
from clubreview.models import *
from django.core.exceptions import (ObjectDoesNotExist,
                                        MultipleObjectsReturned, FieldError, ValidationError, NON_FIELD_ERRORS )
from django.db import DatabaseError
import pdb
import traceback
import sys


clubs_found = []
clubs_partially_found = []
clubs_not_found = []
def main(callback = None):
    """
    Parser to harvest social media links from callink.berkeley.edu
    TODO:
        Update club info in database depending if club exists using exact match on name. Assume http://students.berkeley.edu/osl/studentgroups/public/index.asp is the single source of truth.
        Attempt to retrieve facebook_id using fb_events.py
        Store callink url or identifier into the database
        Create a callink_url property for Club.
        Integrate with django commands
    """
    BASE_URL = "http://callink.berkeley.edu/"
    ORGANIZATION_URL = "http://callink.berkeley.edu/Organizations"
    DEFAULT_PARAMS = { 'SearchType'         : 'None',
                       'SelectedCategoryId' : 0,
                       'CurrentPage'        : 1 }
    FACEBOOK_CLASS = 'facebook'
    WEBSITE_CLASS = 'earth'
    TWITTER_CLASS = 'twitter'

    def parse(url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
        links = soup.select('.icon-social')
        link_types = [ FACEBOOK_CLASS ,
                       WEBSITE_CLASS  ,
                       TWITTER_CLASS   ]
        link_dict = {}
        for link in links:
            for class_name in link_types:
                if class_name in link['class']:
                    link_dict[class_name] = link['href']
        return link_dict

    r = requests.get(ORGANIZATION_URL, params = DEFAULT_PARAMS)
    last_links = None
    links = None
    params = DEFAULT_PARAMS.copy()
    while r.status_code == 200:
        soup = BeautifulSoup(r.text)
        links  = soup.select('.result h5 a')
        print "%s\n" % params['CurrentPage'], '\n\t'.join([a['href'] for a  in links]), "\n%s" % len(links)

        if last_links == links:
            break

        for link in links:
            link = str(link)
            relative_link = re.findall(r'href="(.*?)"', link)[0]
            name =  re.findall(r'<a.*>(.*?)</a>', link)[0]
            full_url = urlparse.urljoin( BASE_URL, relative_link )
            link_dict = parse( full_url )
            link_dict['name'] = name
            link_dict['permalink'] = relative_link.split('/')[2]
            if callable(callback):
                callback(link_dict)

        last_links = links

        params['CurrentPage'] += 1
        r = requests.get(ORGANIZATION_URL, params = params)


def updateExistingClubs(meta_dict):
    def save_club_links(club, meta_dict):
        try:
            changed = False
            if not club.website and 'earth' in meta_dict:
                club.website = meta_dict['earth']
                changed = True
            if not club.facebook_url and 'facebook' in meta_dict:
                club.facebook_url = meta_dict['facebook']
                changed = True
            if changed and club.full_clean():
                print "saving!!! " + club, meta_dict
                club.save()
        except (ValidationError, DatabaseError) as e:
            if isinstance(e, DatabaseError):
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                                                        limit=10, file=sys.stdout)
                #don't require category

    try:
        print meta_dict['permalink']
        club = Club.objects.get(name = meta_dict['name'])
        clubs_found.append(club.name)
    except (Club.DoesNotExist,  DatabaseError) as e:
        try:
            if isinstance(e, DatabaseError):
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                                                        limit=10, file=sys.stdout)


            abbreviation = re.findall(r'\([^\(^\)]*\)',meta_dict['name']) #find first set of parenthesis-wrapped words
            abbreviation = abbreviation[0].strip() if len(abbreviation) > 0 else None

            if abbreviation :
                just_name = meta_dict['name'].replace(abbreviation, '')
            else:
                just_name = ''

            if len(Club.objects.filter(name__icontains = meta_dict['name'])) > 0:
                club = Club.objects.filter(name__icontains = meta_dict['name'])[0]
                clubs_partially_found.append(meta_dict['name'])
                save_club_links(club, meta_dict)
            elif abbreviation and len( Club.objects.filter(name__contains = abbreviation) ) > 0:

                if len( Club.objects.filter(name__contains = abbreviation) ) > 0:
                    clubs_partially_found.append(meta_dict['name'])
                    club = Club.objects.filter(name__contains = abbreviation)[0]
                    save_club_links(club, meta_dict)
            elif just_name.strip() and just_name != meta_dict['name'] and len( Club.objects.filter(name__contains = just_name.strip()) ) > 0:
                just_name = just_name.strip()
                if len( Club.objects.filter(name__contains = just_name) ) > 0:
                    club = Club.objects.filter(name__contains = just_name)[0]
                    save_club_links(club, meta_dict)
            else:
                clubs_not_found.append(meta_dict['name'])
        except DatabaseError as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                                                     limit=10, file=sys.stdout)

class Command(BaseCommand):
    def handle(self, *args, **options):
        main(updateExistingClubs)

        print "Clubs found %s \n" % len(clubs_found)
        print "Clubs partially found %s \n" % len(clubs_partially_found)
        print "Clubs not found %s \n" % len(clubs_not_found)
