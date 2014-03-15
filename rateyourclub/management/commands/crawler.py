from django.core.management.base import BaseCommand, CommandError
from clubreview.models import *
from bs4 import BeautifulSoup, BeautifulStoneSoup
import urllib2
import pdb
import re, sys, traceback
import django.utils.html as django_html
from django.core.exceptions import (ObjectDoesNotExist,
                                        MultipleObjectsReturned, FieldError, ValidationError, NON_FIELD_ERRORS)
from django.core.validators import validate_email, URLValidator
import requests

RECURSION_LIMIT = 3000
def main():
    """
    Retrieves all club metadata and stores to database.
    TODO: convert to unicode to store in database
          schemamigration for club to store metadata
    """
    URL_VALIDATOR_INSTANCE = URLValidator()
    def validate_url(url_string):
        try:
            URL_VALIDATOR_INSTANCE(url_string)
            return True
        except ValidationError:
            return False

    BASIC_WEBSITE_REGEX = re.compile(r"(?P<url>https?://[^\s]+)", re.MULTILINE) #http://stackoverflow.com/questions/839994/extracting-a-url-in-python

    WHITESPACE_REGEX = re.compile(r"\s+", re.MULTILINE)
    BASIC_DOMAIN_REGEX = re.compile('[^\s]+\.[A-Za-z]{2,3}[^\s]*')
    def strip_tags(string, replacement=''):
        """
        Returns the given HTML with all tags stripped.
        Based off of django.utils.html.strip_tags
        """
        try:
            #attempt to add space for removed html elements in django 1.5.1
            return django_html.strip_tags_re.replace(replacement, django_html.force_text(string))
        except:
            return django_html.strip_tags(string)
    def get_text(string):
        """
        Strip html tags and convert html entities and return string
        TODO: return utf-8 string
        http://stackoverflow.com/a/1209015/1123985
        https://github.com/django/django/blob/master/django/utils/html.py
        http://www.crummy.com/software/BeautifulSoup/bs4/doc/#output-formatters
        """
        decoded = WHITESPACE_REGEX.sub( " ", strip_tags( unicode(BeautifulSoup(string)), replacement=' ' ) )
        return  decoded.strip()

    MEMBERSHIP_REQS = "Membership requirements"
    ACTIVITIES = "Activities"
    MEETINGS = "Meetings"
    PHONE = "Phone"
    URL = "URL"
    ADDRESS = "Address"
    EMAIL = "Email"
    def validateEmail( email ):
        """
        http://stackoverflow.com/a/3218128/1123985
        """
        try:
            validate_email( email )
            return True
        except ValidationError:
            return False

    def initialize_club_dict(header_dict):
        for header in [MEMBERSHIP_REQS, ACTIVITIES, MEETINGS, PHONE, URL, ADDRESS, EMAIL]:
                header_dict.setdefault(header, None)
        return header_dict

    def parse_metadata(html_string):
        #['</p>Address: 101 Haviland Hall<br>Berkeley, CA 94720<br>Activities: seminars, luncheons, educational development']
        #assumes all headers are of the form [A-Z][a-z]
        HEADER_REGEX = re.compile(r'([A-Z][a-z]+\s*[a-zA-Z]+|[A-Z]+\s*):')
        header_titles = HEADER_REGEX.findall( html_string )
        header_dict = initialize_club_dict({})

        for i, title in enumerate(header_titles):
            header_start =  html_string.index( "%s:" % title)
            header_start_pre = header_start - 1 if header_start > 0 else header_start
            if i == len(header_titles)  - 1:
                contents = html_string[header_start_pre:]
            else:
                next_header = header_titles[i+1]
                next_header_start = html_string.index( "%s:" % next_header)
                contents = html_string[header_start_pre:next_header_start]

            value = contents[len(title)+2:] #everything after title and colon
            header_dict[title] = get_text(value)
        return header_dict
    def parse_signatories(html_string):
        signatories_start = html_string.index("Group Signatories:") + len("Group Signatories:") + 1
        signatories_content = html_string[signatories_start:]
        signatories_end = signatories_content.index('<hr>')
        if signatories_end > 0:
            signatories_content = signatories_content[:signatories_end]
        signatories_content = re.findall(r'(?<!<br>).*?([A-Z]{1}.*?<br>\s*Email:.*?)<br>', signatories_content)

        name_email_list = []

        try:
            for name_email in signatories_content:
                name, email = get_text(name_email).split("Email:")
                name = name.strip()
                email = email.strip()
                name_email_list.append( (name, email) )
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                        limit=10, file=sys.stdout)

        return name_email_list

    def parse(url):
        metadata = initialize_club_dict({})
        print url
        soup = BeautifulSoup(urllib2.urlopen(url).read())
        content = soup.find(id='node-2810')
        clubname = content.find_all('b')[0].string
        clubname = re.sub('[\r|\t|\n]','',clubname)
        print clubname
        abbrev = re.search(r'\((.+?)\)$', clubname)
        if abbrev:
            abbrev = abbrev.group(0)[1:-1]
        #content = str(content.findAll(text=True))
        #content = content.replace(u'\r', '').replace(u'\t', '').replace(u'\n', '')
        intro = re.search(r'Purpose: (.+?<p>)', unicode(content))
        #print intro
        if intro:

            content_str = unicode(content).replace('\t','').replace('\n','').replace('\r','')
            start = content_str.index('Purpose')
            end = content_str.index('This group has been viewed')
            signatories_content = content_str[end:]
            signatories = parse_signatories(signatories_content)
            #print signatories
            content_str = content_str[start:end]
            content_str_intermediate = content_str
            content_str = content_str.replace(unicode(intro.group(0)), '')
            content_str_intermediate_two = content_str

            website = BeautifulSoup(content_str.replace('<p>','').replace('</p>',''))

            #pdb.set_trace()
            website = website.findAll('a', href=True)
            if website:
                website = website[0].get('href')
                #print 'Website:', website

            #website = re.search(r'http://[\w.-~/]+', content_str)
            #if website:
            #    website = website.group(0)
            #    print 'Website: ', website
            email = re.search(r'Email: [^@<>]+@[^@<>]+\.[^@<>]+', content_str)
            if email:
                email = email.group(0)[7:]
                #print 'Email:', email



            #cut_length =
            #content_str = content.get_text().encode('ascii','ignore').replace('\t','').replace('\n','').replace('\r','')
            #start = content_str.index('Purpose')
            #end = content_str.index('This group has been viewed')
            #content_str = content_str[start:end]
            #content_str = content_str.replace(str(intro.group(0)), '')
            #content_str = re.sub(r'Purpose: (.+?)','', content_str)
            intro = intro.group(0)[9:-3]
            additional = content_str.replace(unicode(website), '').replace(unicode(email), '').split('<br/>')
            #if url == 'http://students.berkeley.edu/osl/studentgroups/public/index.asp?todo=getgroupinfo&SGID=15133':
            #    pdb.set_trace()

            metadata.update( parse_metadata( content_str ) )
            metadata.update( {'website' : unicode(website).split(',')[0] } )

            if not metadata[EMAIL]:
                metadata.update( { EMAIL : email })

        metadata.update({ 'name' : clubname,
                          'abbrev' : abbrev,
                          'introduction': intro,
                            })
        return metadata
    sys.setrecursionlimit(RECURSION_LIMIT)
    GREEKS_BASE = 'http://lead.berkeley.edu/greek/recognized_chapters'
    GROUPS_BASE = 'http://students.berkeley.edu/osl/studentgroups/public/index.asp?todo=listgroups'
    GROUPS_BASE_URL = 'http://students.berkeley.edu'

    GROUP_INFO_BASE_URL = 'http://students.berkeley.edu/osl/studentgroups/public/index.asp?todo=getgroupinfo&SGID='

    soup = BeautifulSoup(urllib2.urlopen(GROUPS_BASE).read())
    content = soup.find(id='node-2810').prettify()
    content = content.replace('&amp;','&')
    gid_list = re.findall(r'SGID=(\d+)', content)
    url_list = list()

    school, created = School.objects.get_or_create(name='UC Berkeley')
    default_category, default_category_created = Category.objects.get_or_create(name="Default") #this passes validation
    school.full_clean()
    default_category.full_clean()

    for gid in gid_list:
        metadata =  { 'gid' : gid }
        try:
            metadata.update(parse(unicode(GROUP_INFO_BASE_URL+gid)))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                        limit=10, file=sys.stdout)
        try:
            try:
                club = Club.objects.get(school=school, name=metadata['name'])
                club.SGID = long(gid)
                #club = Club.objects.get(school=school, SGID = long(gid))
            except Club.DoesNotExist:
                club = Club(abbrev=metadata['abbrev'], school=school, SGID=long(gid))

            if club.contact_email != metadata[EMAIL]:
                contact_emails = re.findall("[^\s;,]+@.*?[^\s;,]+", metadata[EMAIL])

                if len(contact_emails) > 0 and validateEmail(contact_emails[0]):
                    club.contact_email = contact_emails[0]

            if club.name != metadata['name'] and metadata['name']:
                club.name = metadata['name']

            if club.abbrev != metadata['abbrev'] and metadata['abbrev']:
                club.abbrev = metadata['abbrev']

            if club.introduction != metadata['introduction'] and metadata['introduction']:
                club.introduction = metadata['introduction']

            if not club.school and school:
                club.school = school

            if not club.school and school:
                club.school = school


            if metadata[URL] and not ( unicode(metadata[URL]) in unicode(club.website) ):
                    website_to_add = BASIC_WEBSITE_REGEX.search(metadata[URL]).group('url') if BASIC_WEBSITE_REGEX.search(metadata[URL]) else (BASIC_DOMAIN_REGEX.findall(metadata[URL])[0] if BASIC_DOMAIN_REGEX.search(metadata[URL]) else None)
                    try:
                        if website_to_add:
                            website_to_add = "http://%s" % website_to_add if not urlparse.urlparse(website_to_add).scheme else website_to_add #add http protocol if protocol does not exist
                            print website_to_add
                            r = requests.get(website_to_add) if validate_url(website_to_add) else None #check to see that url exists
                            if r and r.status_code == 200:
                                club.website = website_to_add

                                facebook_url = re.search(r'(facebook\.com[^\s]*)', website_to_add)
                                if facebook_url and not ( unicode(facebook_url.group(1)) in unicode(club.facebook_url) ):

                                    facebook_url = urlparse.urlparse(facebook_url.group(1))
                                    facebook_url = urlparse.urljoin(facebook_url.netloc, facebook_url.path)
                                    club.facebook_url = "https://wwww.%s" % facebook_url
                                    club.website = club.facebook_url
                                    fb = fb_events.FacebookGroup(club.facebook_url, user_access_token = config.FACEBOOK_USER_ACCESS_TOKEN,
                                                                 email = config.FACEBOOK_USER_EMAIL,
                                                                 password = config.FACEBOOK_USER_PASSWORD,
                                                                 APP_ID = config.FACEBOOK_APP_ID,
                                                                 APP_SECRET = config.FACEBOOK_APP_SECRET_ID)
                                    fb.get_id()
                                    if fb.id:
                                        club.facebook_id = long(fb.id)
                    except:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=10, file=sys.stdout)
            if club.contact_phone != metadata[PHONE] and metadata[PHONE]:
                metadata[PHONE] = re.sub(r'[^0-9]', '', metadata[PHONE])
                if metadata[PHONE] and len(metadata[PHONE]) == 10:
                    club.contact_phone = metadata[PHONE]

            if club.requirements != metadata[MEMBERSHIP_REQS] and metadata[MEMBERSHIP_REQS]:
                club.requirements = metadata[MEMBERSHIP_REQS]

            if club.activity_summary != metadata[ACTIVITIES] and metadata[ACTIVITIES]:
                club.activity_summary = metadata[ACTIVITIES]

            if club.meeting != metadata[MEETINGS] and metadata[MEETINGS]:
                club.meeting = metadata[MEETINGS]

            if club.address != metadata[ADDRESS] and metadata[ADDRESS]:
                club.address = metadata[ADDRESS]

            if club.categories.count() == 0:
                club.categories.add(default_category)

            if type(club.full_clean()) == type(None): #no errors
                club.save()
        except (Exception, ValidationError) as e:
            import pprint
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=10, file=sys.stdout)
            pprint.pprint(metadata)


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()

