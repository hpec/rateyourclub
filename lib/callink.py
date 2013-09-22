import requests
import bs4
import pytz
import dateutil
import warnings
import unicodedata
from dateutil.parser import parse
from datetime import datetime
from copy import copy
import re


class CallinkEvent(object):
    def __init__(self, soup):
        self.soup = soup

    def pprint(self):
        import pprint
        pprint.pprint(event.as_dict)

    @property
    def valid(self):
        return self.start_time and self.end_time and self.end_time > self.start_time

    @property
    def location(self):
        if len(self.description_soup.select('.location')) > 0:
            return self.description_soup.select('.location')[0].text
    @property
    def facebook_event_id(self):
        match = re.findall(".*facebook.com/events/([0-9]+).*", self.description_soup.text, re.MULTILINE)
        if len(match) > 0 : return match[0]
    @property
    def facebook_event_url(self):
        if self.facebook_event_id: return "https://facebook.com/events/%s" % self.facebook_event_id

    @property
    def categories(self):
        """
        If event does not have a category it will be in the 'No Specific Category' category
        """
        return map(lambda category : category.text, self.soup.select('category'))

    @property
    def author(self):
        return self.soup.find('author').text

    @property
    def email(self):
        if self.author:
            match = re.match('.*@.+?\.[a-z]+', self.author)
            if match:
                email = match.group(0)
                if not re.match('no-reply', email): return email

    @property
    def image_url(self):
        """
        https://callink.berkeley.edu/images/W460xL600/0/noshadow/Event/2e98c6d8565f4549976cc6a18320ab89.jpg
        """
        enclosure = self.soup.find('enclosure')
        if enclosure and  enclosure.get('url') : return unicode(enclosure.get('url'))
    @property
    def image_thumb_url(self):
        """
        https://callink.berkeley.edu/images/W180xL240/0/noshadow/Event/2e98c6d8565f4549976cc6a18320ab89.jpg
        """
        if self.image_url:
            match = re.match('https://callink.berkeley.edu/images/.*/0/noshadow/Event/(.*).jpg', self.image_url)
            if match : return "https://callink.berkeley.edu/images/W180xL240/0/noshadow/Event/%s.jpg" % match.group(1)
    @property
    def text(self):
        return self.soup.text

    @property
    def callink_event_id(self):
        match = re.match('.*details/([0-9]+)', self.soup.find('link').text)
        if match :    return match.group(1)
    @property
    def redirect_permalink(self):
        """
        All permalinks follow this general structure
        The other structure is https://callink.berkeley.edu/organization/<club_name>/calendar/details/<event_id>'
        """
        if self.callink_event_id:
            return u'https://callink.berkeley.edu/events/details/%s' % self.callink_event_id

    @property
    def permalink(self):
        return unicode(self.soup.find('link').text)
    @property
    def callink_club_name_id(self):
        match = re.match('.*organization/(.*?)/.*', self.soup.find('link').text)
        if match : return match.group(1)

    @property
    def title(self):
        return unicode(self.soup.find('title').text)

    @property
    def link(self):
        return unicode(self.soup.find('link'))

    @property
    def description_soup(self):
        if self.soup.find('description'): return bs4.BeautifulSoup(self.soup.find('description').text)

    @property
    def description(self):
        return self.description_soup.text

    @property
    def alt_times(self):
        elements =  self.description_soup.select('.value')
        elements = map(lambda time : time.get('title'), elements)
        if len(elements) > 0 :
            return  elements
        elif not self.start_time:
            warnings.warn( u'Alternative Start times not found for %s' % unicodedata.normalize('NFKD', self.title).encode('ascii','ignore'))

    @property
    def start_time_soup(self):
        if not self.description_soup: return
        elements= self.description_soup.select('.dtstart')
        if len(elements) > 0 :
            return  elements[0]
        else :
            warnings.warn( u'Start time not found for %s' % unicodedata.normalize('NFKD', self.title).encode('ascii','ignore'))

    @property
    def display_start_time(self):
        if self.start_time_soup : return self.start_time_soup.text
    @property
    def raw_start_time(self):
        return self.start_time_soup.get('title')
    @property
    def start_time(self):
        if self.start_time_soup and self.start_time_soup.get('title') : 
            return parse(self.start_time_soup.get('title'))
        else:
           warnings.warn( u'Start time timestamp not found for %s' % unicodedata.normalize('NFKD', self.title).encode('ascii','ignore'))
           if self.alt_times and len(self.alt_times) > 0 : 
            if self.alt_times and len(self.alt_times) == 2 : 
                time = parse(self.alt_times[1]).time()
                return parse(self.alt_times[0]).replace(hour = time.hour, minute = time.minute)
            else:
                return parse(self.alt_times[0])
    @property
    def end_time_soup(self):
        if not self.description_soup: return
        elements= self.description_soup.select('.dtend')
        if len(elements) > 0 :
            return  elements[0]
        else :
            warnings.warn( u'End time not found for %s' % unicodedata.normalize('NFKD', self.title).encode('ascii','ignore'))

    @property
    def display_end_time(self):
        if self.end_time_soup : return self.end_time_soup.text
    @property
    def raw_end_time(self):
        return self.end_time_soup.get('title')
    @property
    def end_time(self):
        if self.end_time_soup and self.end_time_soup.get('title') : 

            
            time = parse(self.end_time_soup.get('title'))
            if time < self.start_time :
                return copy(self.start_time).replace(hour = time.hour, minute = time.minute)
            else :
                return time
        else:
           warnings.warn( u'End time timestamp not found for %s' % unicodedata.normalize('NFKD', self.title).encode('ascii','ignore'))
    @property
    def ical_link(self):
        return "https://callink.berkeley.edu/events/ical/%s" % self.callink_event_id
    @property
    def google_calendar_link(self):
        return "https://callink.berkeley.edu/events/publishtogoogle/%s" % self.callink_event_id

    @property
    def  as_dict(self):
        return { 
            'title' : self.title,
            'text'  : self.text,
            'alt_times' : self.alt_times,
            'start_time' : self.start_time,
            'raw_start_time' : self.raw_start_time,
            'end_time' : self.end_time,
            'raw_end_time' : self.raw_end_time,
            'description' : self.description,
            'location' : self.location,
            'callink_club_name_id' : self.callink_club_name_id,
            'permalink' : self.permalink,
            'event_id' : self.callink_event_id,
            'redirect_permalink' : self.redirect_permalink,
            'facebook_event_id' : self.facebook_event_id,
            'facebook_event_url' : self.facebook_event_url,
            'image_url' : self.image_url,
            'image_thumb_url' : self.image_thumb_url,
            'email' : self.email,
            'categories' : self.categories
            }
    CALLINK_EVENTS_RSS_URL = 'https://callink.berkeley.edu/EventRss/EventsRss'
    @classmethod
    def fetch(class_name):
        """
        Get events for current week
        """
        response = requests.get( CallinkEvent.CALLINK_EVENTS_RSS_URL )
        try:
            if response.status_code == 200:
                soup = bs4.BeautifulSoup( response.text )
                events = map(lambda event: CallinkEvent(event) , soup.select('item'))
                return events
            else :
                warnings.warn( u'Could not parse events from %s with status code %s' % (CallinkEvent.CALLINK_EVENTS_RSS_URL, response.status_code))
        except Exception, e:
            warnings.warn( u'Could not parse events from %s with message: %s ' % (CallinkEvent.CALLINK_EVENTS_RSS_URL, e.message))
            return []
