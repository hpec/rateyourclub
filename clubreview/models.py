from django.db import models
from django.utils import timezone
from django.core.exceptions import (ObjectDoesNotExist,
                                        MultipleObjectsReturned, FieldError, ValidationError, NON_FIELD_ERRORS)
import pdb
import urlparse
import random
import re
import nltk
import operator
from copy import copy
from datetime import timedelta, date
from django.db.models.signals import post_init
from django.utils.timezone import now
from django.db.models import Q
from django.dispatch import receiver
from django.utils.timezone import is_aware
from registration.models import User
from bs4 import BeautifulSoup

common_words = ['berkeley', 'dwinelle', 'association', 'associations', 'club', 'clubs', 'students', 'student']
NAME_LENGTH = 80

def sim(a,b):
    if not a or not b: return 0
    intersect = set(a).intersection(set(b))
    result = 0
    for x in intersect:
        result += min(a.count(x), b.count(x))
    return result

class School(models.Model):
    name = models.CharField(max_length=NAME_LENGTH)

    def __unicode__(self):
        return "%s" % (self.name)

class Category(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    def __unicode__(self):
        return "%s" % (self.name)

class ClubQuerySet(models.query.QuerySet):
    def facebook(self):
        return self.filter(facebook_id__isnull=False)
    def facebook_including_null_id(self):
        return self.exclude(facebook_url='')
    def facebook_null_id(self):
        return self.exclude(Q(facebook_url='')).filter(facebook_id__isnull=True)
    def rated(self):
        return self.extra(select={'average_rating':'CASE WHEN review_count > 0 THEN review_score/review_count ELSE 0 END'})
    def top_rated(self):
        return self.rated().order_by('-average_rating')

class ClubManager(models.Manager):

    use_for_related_fields = True

    def find_by_permalink(self, permalink):
        return self.get_query_set().get(permalink=permalink)
    def get_query_set(self):
        return ClubQuerySet(model=self.model)
    def facebook(self):
        return self.get_query_set().facebook()
    def rated(self):
        return self.get_query_set().rated()
    def top_rated(self):
        return self.get_query_set().top_rated()
    def facebook_null_id(self):
        return self.get_query_set().facebook_null_id()
    def facebook_including_null_id(self):
        return self.get_query_set().facebook_including_null_id()

    # Note: this is too expensive
    # def get_related_clubs(self, club):
    #     clubs = list(super(ClubManager, self).get_query_set().all())
    #     result = dict()
    #     for c in clubs:
    #         if c!=club:
    #             score = sim(club.word_list, c.word_list)
    #             if c.category and club.category == c.category: score += 5
    #             result[c] = score
    #     result = sorted(result.iteritems(), key=operator.itemgetter(1), reverse=True)
    #     return [club for club, score in result][:5]
    def get_related_clubs(self, club):
        results = []
        if club.related_clubs:
            club_ids = club.related_clubs.split(',')
            for club_id in club_ids:
                results.append(super(ClubManager, self).get_query_set().get(id=int(club_id)))
            if club.category:
                clubs_with_same_cat = list(super(ClubManager, self).get_query_set().filter(category=club.category))
                clubs_with_same_cat = [club for club in clubs_with_same_cat if club not in results]
                results.extend(random.sample(clubs_with_same_cat, 2))
        return results

class Club(models.Model):
    def ensure_has_permalink(self):
        if not self.permalink:
            clean_name = self.name.replace(self.abbrev, '') if self.abbrev else self.name
            self.permalink = re.sub('[^a-zA-Z0-9]', '-', clean_name.lower())
            self.permalink = re.sub('[^a-zA-Z0-9]+$','', self.permalink)
            self.permalink = re.sub('^[^a-zA-Z0-9]+','', self.permalink)
            self.permalink = re.sub('-+','-',self.permalink)[:50]
            if not self.permalink: self.permalink = re.sub('[^a-zA-Z0-9]+','', self.abbrev.lower())
            temp = self.permalink
            counter = 1
            while Club.objects.filter(permalink__icontains=self.permalink).count() > 0:
                self.permalink =  "%s-%s" % (temp[:50 - len(str(counter)) - 1], counter) # slug fields have length limit of 50
                counter += 1
            self.save()
    school = models.ForeignKey(School)
    category = models.ForeignKey(Category, null=True)

    name = models.TextField()
    abbrev = models.CharField(max_length=NAME_LENGTH, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    facebook_id = models.BigIntegerField(blank=True, default=None, unique=True, null=True)
    facebook_url = models.URLField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=10, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    introduction = models.TextField(blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    review_count = models.IntegerField(default=0)
    review_score = models.IntegerField(default=0)
    hit = models.IntegerField(default=0)
    SGID = models.BigIntegerField(blank=True,unique=True,null=True)
    callink_permalink = models.SlugField(blank=True,null=True)
    requirements = models.TextField(blank=True,null=True)
    meeting = models.TextField(blank=True,null=True) #information about club meetings
    address = models.TextField(blank=True,null=True)
    activity_summary = models.TextField(blank=True,null=True)
    permalink = models.SlugField(blank=True,null=True, unique=True)
    is_deleted = models.BooleanField(default=0)
    related_clubs = models.TextField(blank=True,null=True)

    objects = ClubManager()

    def is_float(self, val):
        try:
            float(val)
            return True
        except ValueError, TypeError:
            return False


    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    @property
    def display_requirements(self):
        #http://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
        #http://www.crummy.com/software/BeautifulSoup/bs4/doc/#get-text
        return BeautifulSoup(self.requirements).get_text()
    @property
    def display_activity_summary(self):
        return BeautifulSoup(self.activity_summary).get_text()
    @property
    def display_introduction(self):
        """
        Introduction without html entities. By default, django converts text to entities in templates
        """
        return BeautifulSoup(self.introduction).get_text()
    @property
    def display_meeting(self):
        return BeautifulSoup(self.meeting).get_text()
    @property
    def display_address(self):
        return BeautifulSoup(self.address).get_text()


    @property
    def callink_url(self):
        return urlparse.urljoin("https://callink.berkeley.edu/organization", self.permalink) if self.permalink else None

    @property
    def students_berkeley_edu_url(self):
        return "http://students.berkeley.edu/osl/studentgroups/public/index.asp?todo=getgroupinfo&SGID=%s" % self.SGID if self.SGID else None
    @property
    def legacy_students_berkeley_edu_url(self):
        """
        The students.berkeley.edu website was deprecated around August 2013 but many of the urls have been archived.
        """
        return "http://web.archive.org/web/20130127122716/" + self.students_berkeley_edu_url

    @property
    def _EventManager(self):
        return Event.objects

    @property
    def facebook_graph_url(self):
        return "https://graph.facebook.com/%s" % self.facebook_id if self.facebook_id else None
    @property
    def reviews(self):
        return self.review_set.all()
    @property
    def num_ratings(self):
        # This operation is too expensive # return len( [ r for r in  self.reviews if ( self.is_float(r.ratings) and float( r.ratings ) > 0 ) ] )
        return self.review_count
    @property
    def total_rating(self):
        # This operation is too expensive # return sum( map(lambda r : (float(r.ratings) if self.is_float(r.ratings) else 0), self.reviews) )
        return self.review_score
    @property
    def avg_rating(self):
        return self.total_rating / self.num_ratings if self.num_ratings > 0 else 0

    @property
    def word_list(self):
        if self.introduction:
            intro = self.introduction.lower()
            word_list = nltk.tokenize.wordpunct_tokenize(intro)
            word_list = [w for w in word_list if not w in nltk.corpus.stopwords.words('english') and not w in common_words]
            return word_list

    def relevance(self, query):
        from nltk.tokenize import wordpunct_tokenize

        name_words = wordpunct_tokenize(self.name.lower())
        score = 0
        for word in query.split():
            if word in name_words: score += 20

        return score + self.hit * 0.1




    def set_facebook_id(self):
        import fb_events
        if self.facebook_url:
            fb = fb_events.FacebookGroup(self.facebook_url)
            if fb.get_id() : self.facebook_id = fb.get_id()
            if self.facebook_id: self.save()

    def facebook_event_update(self):
        import fb_events
        if self.facebook_id == None:
            return
        fb = fb_events.FacebookGroup(self.facebook_graph_url)
        try:
            for _event in (fb.get_events()+fb.get_events_by_fql()):
                try:
                    event = self._EventManager.get( facebook_id = long(_event['id']) )
                except self._EventManager.model.DoesNotExist:
                    event = self._EventManager.model( facebook_id = long(_event['id']) )
                for field in event._meta.fields:
                    #https://github.com/django/django/blob/master/django/db/models/base.py
                    if field.name in _event and (field.attname == field.name and not field.primary_key): #is assignable property, property is a column in the table
                        setattr(event, field.name, _event[field.name])

                try:
                    if event.full_clean() == None:
                       event.save()
                       if len(self.event_set.filter(id=event.id)) == 0:
                        event.club.add(self)
                except (ValidationError) as e:
                    #TODO: handle errors accordingly
                    pass
        except fb_events.facebook.GraphAPIError as e:
            #TODO: handle errors accordingly
            pass

    def __unicode__(self):
        return "%s" % (self.name)
@receiver(post_init, sender=Club)
def post_init_callbacks(sender, instance, **kwargs):
    instance.ensure_has_permalink()

class EventQuerySet(models.query.QuerySet):
    def future(self):
        """
        Return ongoing or events in the future
        """
        return self.filter( Q(start_time__gte=now()) | Q(end_time__gte=now()) )


    def past(self):
        return self.exclude( Q(start_time__gte=now()) | Q(end_time__gte=now()) )
    def now(self):
        """
        Return ongoing events:
            1) Events that started and will be ending later.
            2) Full day events. Events without an end date.
        """
        return self.filter( ( Q(start_time__lte=now()) & Q(end_time__gte=now())) |
                            ( Q( start_time__month=now().month) & Q( start_time__day=now().day) & Q( start_time__year=now().year) & Q(end_time__isnull=True))  )


class EventsManager(models.Manager):
    use_for_related_fields = True
    def get_query_set(self):
        return EventQuerySet(model=self.model)

    def future(self):
        return self.get_query_set().future()
    def past(self):
        return self.get_query_set().past()
    def now(self):
        return self.get_query_set().now()

class Event(models.Model):
    """
    Model fields are modeled very closely after facebook event api attributes
    Events are dynamically created using Club#facebook_event_update
    http://developers.facebook.com/docs/reference/api/event/
    """
    club = models.ManyToManyField(Club)

    name = models.CharField(max_length=NAME_LENGTH)
    location = models.CharField(max_length=255, blank=True, null=True)
    facebook_id = models.BigIntegerField(unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    objects = EventsManager()

    @property
    def display_time(self):
        start_time = self.convert_to_local_time(self.start_time)
        return start_time.strftime("%A %m/%d, %I:%M %p")
    @property
    def display_start_time(self):
        return self.convert_to_local_time(self.start_time)
    @property
    def display_end_time(self):
        return self.convert_to_local_time(self.end_time)
    def convert_to_local_time(self, dt):
        # includes DST support
        # http://stackoverflow.com/questions/2775864/python-datetime-to-unix-timestamp
        # http://stackoverflow.com/a/2881048/1123985
        import rateyourclub.settings as settings
        import pytz, time
        localtimezone = pytz.timezone(settings.TIME_ZONE)
        is_dst = time.localtime( time.mktime(dt.timetuple()) ).tm_isdst == 1
        if is_aware(dt):
             time_without_zone = (dt - timedelta(hours=1) if is_dst else dt).astimezone(localtimezone).replace(tzinfo=None)
        else:
            time_without_zone = localtimezone.localize((dt - timedelta(hours=1) if is_dst else dt)).astimezone(localtimezone).replace(tzinfo=None)
        return localtimezone.localize(time_without_zone, is_dst=is_dst )

    def __unicode__(self):
        return "%s" % (self.name)
    @property
    def facebook_graph_url(self):
        return "https://graph.facebook.com/%s" % self.facebook_id
    @property
    def facebook_url(self):
        return "https://www.facebook.com/events/%s" % self.facebook_id

class Review(models.Model):
    club = models.ForeignKey(Club)
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event, blank=True, null=True)

    ratings = models.FloatField(blank=False, null=True)
    content = models.TextField(blank=True, null=True)
    anonymous = models.BooleanField(default=True)
    date_posted = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=0)

    def __unicode__(self):
        return "%s" % (self.content)

class ClubURIEdit(models.Model):
    WEBSITE_URL_TYPE = 0
    FACEBOOK_URL_TYPE = 1
    DENIED_STATE = False
    APPROVED_STATE = True
    club = models.ForeignKey(Club)
    attribute_type  = models.IntegerField()
    value = models.URLField(default='')
    state = models.NullBooleanField()
    def __unicode__(self):
        if self.club:
            return "%s %s: %s" % (self.club.name, self.display_attribute_type, self.value)
        else:
            return "%s: %s" % (self.display_attribute_type,  self.value)
    @property
    def club_name(self):
        return self.club.name
    @property
    def display_attribute_type(self):
        if self.attribute_type == ClubURIEdit.WEBSITE_URL_TYPE:
            return "Website"
        if self.attribute_type == ClubURIEdit.FACEBOOK_URL_TYPE:
            return "Facebook"
    @property
    def display_state(self):
        if self.state == ClubURIEdit.DENIED_STATE:
            return "Denied"
        if self.state == ClubURIEdit.APPROVED_STATE:
            return "Approved"
        return "Pending"

    def handle_attribute_save(self, state):
        if state == ClubURIEdit.APPROVED_STATE:
            if self.attribute_type == ClubURIEdit.WEBSITE_URL_TYPE:
                self.club.website = self.value
            if self.attribute_type == ClubURIEdit.FACEBOOK_URL_TYPE:
                self.club.facebook_url = self.value
            if type(self.club.full_clean()) == type(None):
                self.club.save()
                self.state = ClubURIEdit.APPROVED_STATE
                self.save()
        elif state == ClubURIEdit.DENIED_STATE:
            self.state = ClubURIEdit.DENIED_STATE
            self.save()

