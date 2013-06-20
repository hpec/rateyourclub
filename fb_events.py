import os,re, urllib2
from dateutil.parser import parse
from datetime import datetime
import facebook
import pdb

"""
simple library for retrieving events from facebook groups
include the following in local_settings.py in your project directory
https://developers.facebook.com/tools/explorer/
APP_ID = ''
APP_SECRET = ''
USER_ACCESS_TOKEN = ''
"""
APP_ID = None
APP_SECRET = None
USER_ACCESS_TOKEN = None



if os.path.exists(os.path.normpath(os.path.join(os.path.dirname(__file__), 'local_settings.py'))):
  from local_settings import *

#json parser from facebook-sdk package
try:
    import simplejson as json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import json
_parse_json = json.loads


class FacebookGroup(object):
    '''
    An abstraction for facebook groups and pages.
    Both facebook group and pages can have events.
    The object is meant only for publicly available groups and pages.
    Read more at https://developers.facebook.com/
    TODO: handle invalid access token better
    Retrieve your access token here https://developers.facebook.com/tools/explorer/
    Inspiration from fbconsole and facebook-sdk
    '''
    def __init__(self, url, access_token = USER_ACCESS_TOKEN):
        import urllib2
        try:
            self.user_access_token = access_token
            print self.user_access_token
            self.access_token = self.user_access_token if self.user_access_token != None else facebook.get_app_access_token(APP_ID, APP_SECRET)
        except urllib2.HTTPError, e:
            response = _parse_json(e.read())
            raise facebook.GraphAPIError(response)
        self.url = url.strip()
        self.id = None
        self.events = []
    def get_id(self):
        '''
        Method to retrieve names from facebook pages and groups.
        This works for all facebook pages but is not guaranteed for facebook groups.
        There is currently only one known way to resolve all facebook group aliases:
        Currently known 3rd party url alias -> group id resolver is http://www.wallflux.com/facebook_id/

        >>> innod = FacebookGroup('https://www.facebook.com/InnovativeDesignUCB')
        >>> innod.get_id()
        118333034872164
        >>> csua = FacebookGroup('https://www.facebook.com/groups/csuahosers/')
        >>> csua.get_id()
        182992048515852
        >>> hb_alias = FacebookGroup('https://www.facebook.com/groups/hackberkeley')
        >>> hb_alias.get_id()
        False
        >>> hb = FacebookGroup('https://graph.facebook.com/276905079008757')
        >>> hb.get_id()
        276905079008757
        >>> bp = FacebookGroup('https://www.facebook.com/berkeleyproject')
        >>> bp.get_id()
        313228564146
        >>> zuck = FacebookGroup('https://www.facebook.com/zuck')
        >>> zuck.get_id()
        False
        '''
        #== intialize == #
        if re.match('https:\/\/graph\.facebook\.com\/\d+$', self.url): #if graph.facebook.com url is provided, just read from the url
            data = urllib2.urlopen(self.url).read()
        else:
            data = urllib2.urlopen('https://graph.facebook.com/?ids='+ self.url).read() #resolve group id from url

        #== parse == #
        response = _parse_json(data)

        if re.match('https:\/\/graph\.facebook\.com\/\d+$', self.url):
            gid = int(re.search('\d+', self.url).group())
            if 'id' in response and not 'first_name' in response:
                self.id = int(response['id'])
                if int(gid) == self.id:
                    return self.id
                else:
                    self.id = None
                    return False
        elif self.url in response and not 'first_name' in response[self.url] and 'id' in response[self.url]:  #filter out profiles
            if re.match('\d+$', str(response[self.url]['id']) ):
                self.id = int(response[self.url]['id'])
                return self.id
            else: #when the id returned is just a url
                return False
        else:
            return False

    def get_events(self):
        """
        Get a set of events for facebook page and facebook groups
        There are 3 cases: date-only, precise time and local time(deprecated)
        TODO: handle invalid access token esp. for public vs. private groups like  hackers at berkeley
        http://developers.facebook.com/docs/reference/api/event/
        """
        try:
            data = urllib2.urlopen('https://graph.facebook.com/'+str(self.id)+'/events?access_token='+self.access_token).read()
            response = _parse_json(data)
            self.events = response['data']
            for event in self.events:
                event['start_time'] = parse(event['start_time'])
                if 'end_time' in event:
                    event['end_time'] = parse(event['end_time'])
                if 'updated_time' in event:
                    event['updated_time'] = parse(event['updated_time'])
            return self.events
        except urllib2.HTTPError, e:
            response = _parse_json(e.read())
            raise facebook.GraphAPIError(response)

    def generate_event_url(event_id):
        return 'https://www.facebook.com/events/'+event_id

def main():
    import os
    #os.system('python -m doctest %s' % __file__)
    hb = FacebookGroup('https://graph.facebook.com/276905079008757')
    #http://stackoverflow.com/questions/1302161/how-do-i-parse-timezones-with-utc-offsets-in-python


if __name__ == "__main__":
    main()
