from django.db import models
from django.utils import timezone

# Create your models here.

NAME_LENGTH = 80

class School(models.Model):
    name = models.CharField(max_length=NAME_LENGTH)

    def __unicode__(self):
        return "%s" % (self.name)

class Club(models.Model):
    school = models.ForeignKey(School)
    
    name = models.CharField(max_length=NAME_LENGTH)
    website = models.URLField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=10, blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    introduction = models.TextField(blank=True)
    size = models.IntegerField(blank=True, null=True)
    review_count = models.IntegerField(default=0)
    hit = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s" % (self.name)

class Event(models.Model):
    club = models.ManyToManyField(Club)

    name = models.CharField(max_length=NAME_LENGTH)
    date = models.DateField()
    location = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return "%s" % (self.name)

class Review(models.Model):
    club = models.ForeignKey(Club)
    event = models.ForeignKey(Event, blank=True, null=True)

    ratings = models.TextField(blank=True)
    content = models.TextField(blank=True)
    anonymous = models.BooleanField(default=True)
    date_posted = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return "%s" % (self.content)
