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
from django.core.validators import URLValidator


clubs_found = []
def is_valid_url(url):
    try:
        URLValidator()(url)
        return True
    except ValidationError:
        return False
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
                    if 'http' not in link_dict[class_name] and '::' not in link_dict[class_name]:
                        link_dict[class_name] = 'http://'+link_dict[class_name]
        return link_dict
    def parse_description(url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
        description =  ' '.join(list((map(lambda p: str(p), soup.select('#largeColumn .section p')))))
        return description

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
            name =  ("" + re.findall(r'<a.*>(.*?)</a>', link)[0] + "").decode('utf-8')
            full_url = urlparse.urljoin( BASE_URL, relative_link )
            link_dict = parse( full_url )
            link_dict['name'] = name
            link_dict['permalink'] = relative_link.split('/')[2]
            about_url = full_url + '/about'
            description = parse_description(about_url)
            if callable(callback):
               callback(link_dict, name, description)

        last_links = links

        params['CurrentPage'] += 1
        r = requests.get(ORGANIZATION_URL, params = params)


def updateExistingClubs(meta_dict, name, description):
    def save_club_links(club, meta_dict):
        try:
            changed = False
            if not club.website and 'earth' in meta_dict:
                if is_valid_url(meta_dict['earth']):
                    club.website = meta_dict['earth']
                    changed = True
            if not club.facebook_url and 'facebook' in meta_dict:
                if is_valid_url(meta_dict['facebook']):
                    club.facebook_url = meta_dict['facebook']
                    changed = True
            if not club.callink_permalink and 'permalink' in meta_dict:
                club.callink_permalink = meta_dict['permalink']
                changed = True
            if changed and type(club.full_clean()) == type(None):
                club.save()
        except (ValidationError, DatabaseError) as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                                                    limit=10, file=sys.stdout)

    try:
        club = Club.objects.get(callink_permalink= meta_dict['permalink'])
        save_club_links(club, meta_dict)
        clubs_found.append(club.name)
    except (Club.DoesNotExist,  DatabaseError) as e:
        try:
            if isinstance(e, DatabaseError):
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                                                        limit=10, file=sys.stdout)


            abbreviation = re.findall(r'\([^\(^\)]*\)',meta_dict['name']) #find first set of parenthesis-wrapped words
            abbreviation = abbreviation[0].strip() if len(abbreviation) > 0 else None

            print "creating club %s" % name
            club = Club(name=name, introduction=description, abbrev=abbreviation, school=School.objects.get(name="UC Berkeley"))
            save_club_links(club, meta_dict)
        except DatabaseError as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                                                     limit=10, file=sys.stdout)

class Command(BaseCommand):
    def handle(self, *args, **options):
        main(updateExistingClubs)

        print "Clubs found %s \n" % len(clubs_found)
