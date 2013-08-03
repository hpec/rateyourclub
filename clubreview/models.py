from django.db import models
from django.utils import timezone
from django.core.exceptions import (ObjectDoesNotExist,
                                        MultipleObjectsReturned, FieldError, ValidationError, NON_FIELD_ERRORS)
import pdb
import urlparse, fb_events

# Create your models here.

NAME_LENGTH = 80

class School(models.Model):
    name = models.CharField(max_length=NAME_LENGTH)

    def __unicode__(self):
        return "%s" % (self.name)

class Category(models.Model):
    name = models.CharField(max_length=NAME_LENGTH)

    def __unicode__(self):
        return "%s" % (self.name)

class FacebookManager(models.Manager):
    def get_query_set(self):
        return super(FacebookManager, self).get_query_set().filter(facebook_id__isnull=False)
class Club(models.Model):
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
    callink_permalink = models.TextField(blank=True,null=True)
    requirements = models.TextField(blank=True,null=True)
    meeting = models.TextField(blank=True,null=True) #information about club meetings
    address = models.TextField(blank=True,null=True)
    activity_summary = models.TextField(blank=True,null=True)

    objects = models.Manager()
    facebook_clubs = FacebookManager()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
    @property
    def callink_url(self):
        return urlparse.urljoin("https://callink.berkeley.edu/organization", self.permalink) if self.permalink else None

    @property
    def students_berkeley_edu_url(self):
        return "http://students.berkeley.edu/osl/studentgroups/public/index.asp?todo=getgroupinfo&SGID=%s" % self.SGID if self.SGID else None

    @property
    def _EventManager(self):
        return Event.objects

    @property
    def facebook_graph_url(self):
        return "https://graph.facebook.com/%s" % self.facebook_id if self.facebook_id else None
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
    event = models.ForeignKey(Event, blank=True, null=True)

    ratings = models.TextField(blank=False, null=True)
    content = models.TextField(blank=True, null=True)
    anonymous = models.BooleanField(default=True)
    date_posted = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return "%s" % (self.content)

