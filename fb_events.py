import os, re, urllib2, urllib, cookielib, yaml
from dateutil.parser import parse
from datetime import datetime
import facebook, urllib
import pytz
import pdb
from bs4 import BeautifulSoup
from rateyourclub import settings

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
    def __init__(self, url, user_access_token = USER_ACCESS_TOKEN):
        try:
            self.user_access_token = user_access_token
            self.app_access_token = facebook.get_app_access_token(APP_ID, APP_SECRET)
            if os.path.isfile(settings.CONFIGURATION_YAML):
                data = yaml.safe_load(file(settings.CONFIGURATION_YAML))
                if set(('email','password')).issubset(data):
                  self.email = data['email']
                  self.password = data['password']
        except urllib2.HTTPError, e:
            response = _parse_json(e.read())
            raise facebook.GraphAPIError(response)
        self.url = url.strip()
        self.id = None
        self.events = []
    def login(self, email, password, next_url = None, callback = None):
      jar = cookielib.CookieJar()
      cookie = urllib2.HTTPCookieProcessor(jar)
      opener = urllib2.build_opener(cookie)

      headers = {
          "User-Agent" : "Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.8.1.14) Gecko/20080609 Firefox/2.0.0.14",
          "Accept" : "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,text/png,*/*;q=0.5",
          "Accept-Language" : "en-us,en;q=0.5",
          "Accept-Charset" : "ISO-8859-1",
          "Content-type": "application/x-www-form-urlencoded",
          "Host": "m.facebook.com"
      }

      try:
          params = urllib.urlencode({'email': email,
                                      'pass': password,
                                      'login':'Log+In',
                                      'next' : next_url})
          req = urllib2.Request('http://m.facebook.com/login.php?m=m&refsrc=m.facebook.com%2F', params, headers)
          res = opener.open(req)
          html = res.read()
          if callable(callback):
            callback(html)
      except urllib2.HTTPError, e:
          print e.msg
      except urllib2.URLError, e:
          print e.reason[1]
    def get_facebook_group_gid(self, group_url):
        """
        This method provides reverse lookup support for urls, by parsing the DOM for group id after authenticating as a user
        http://stackoverflow.com/questions/2030652/logging-into-facebook-with-python
        http://stackoverflow.com/a/3846516/1123985
        http://stackoverflow.com/a/11424765/1123985
        """

        def callback(html):
          soup = BeautifulSoup( html )
          gid = soup.select("input[name=target]")[0]['value'] if len(soup.select("input[name=target]")) > 0 else None
          if gid:
            self.id = gid

        if self.email and self.password:
            self.login(self.email, self.password, group_url, callback)

        return self.id

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
        2200089855
        >>> hb_alias = FacebookGroup('https://www.facebook.com/groups/hackberkeley')
        >>> hb_alias.get_id() #test get id by logging in
        276905079008757
        >>> hb = FacebookGroup('https://graph.facebook.com/276905079008757')
        >>> hb.get_id()
        276905079008757
        >>> bp = FacebookGroup('https://www.facebook.com/berkeleyproject')
        >>> bp.get_id()
        313228564146
        >>> zuck = FacebookGroup('https://www.facebook.com/zuck')
        >>> zuck.get_id()
        False
        >>> a2f = FacebookGroup("https://www.facebook.com/group.php?gid=110646618973618") #club no longer exists but link still stored in fb graph
        >>> a2f.get_id()
        110646618973618
        >>> armenian = FacebookGroup('http://www.facebook.com/group.php?gid=2200021660')
        >>> armenian.get_id()
        2200021660
        >>> aclu = FacebookGroup('https://www.facebook.com/group.php?gid=2200041910')
        >> aclu.get_id()
        2200041910

        '''
        #== intialize == #
        if re.match('https:\/\/graph\.facebook\.com\/\d+$', self.url): #if graph.facebook.com url is provided, just read from the url
            data = urllib2.urlopen(self.url).read()
        elif re.search(r'facebook\.com\/group\.php\?gid=(\d+)', self.url):
            self.id = int(re.findall(r'facebook\.com\/group\.php\?gid=(\d+)', self.url)[0])
            return self.id
        elif re.match('https:\/\/www\.facebook\.com\/groups/.*', self.url):
            gid = self.get_facebook_group_gid(self.url)
            if re.match('\d+', str(gid)):
              if not re.match('\d+', str(self.id)):
                  self.id = int(gid)
              return int(gid)
            else:
              return gid
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
    def get_events_by_fql(self):
        """
        This method allows us to get all events for facebook pages.

        The original idea was to get events from a group without authentication by selection all the events
        created by a group's administrator. Alas, it is only search by event creater based on the access_token given.
        SELECT uid, administrator FROM group_member WHERE gid= <gid>;
        SELECT eid FROM event WHERE creator = <id>; #can be page id or user id
        SELECT eid, creator FROM event WHERE eid= <event_id> ; #eid's are not guaranteed to be null
        make sure parent_group_id =gid
        https://developers.facebook.com/docs/reference/fql/group/
        https://developers.facebook.com/docs/technical-guides/fql/
        >>> bp = FacebookGroup('https://www.facebook.com/berkeleyproject')
        >>> len(bp.get_events_by_fql()) > 0 #can get past events of pages using fql
        True
        >>> hb = FacebookGroup('https://graph.facebook.com/276905079008757')
        >>> len(hb.get_events_by_fql()) == 0 #can't use fql to get group events
        True
        """
        #use this to get all facebook page events from past
        if self.id == None:
            self.get_id()

        try:

            url = 'https://graph.facebook.com/fql?'
            query = "SELECT eid, name, location, description, start_time, end_time, timezone FROM event where creator = %s" % self.id
            params = urllib.urlencode({ 'access_token' : self.app_access_token, 'q' : query })
            data = urllib2.urlopen(url+params).read()
            response = _parse_json(data)
            events = response['data']
            for event in events:
                event['id'] = event['eid']
                parsed_event =  self.parse_event(event)
                event.update(parsed_event)
            self.events.extend(events)
            return events

        except (urllib2.HTTPError, facebook.GraphAPIError), e:
            response = _parse_json(e.read())
            raise facebook.GraphAPIError(response)



    @property
    def extended_token_url(self):
        return "https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=fb_exchange_token&fb_exchange_token=%s" % (APP_ID, APP_SECRET, self.user_access_token)

    @property
    def login_url(self):
        return "https://graph.facebook.com/oauth/authorize?redirect_uri=http://www.berkeleyproject.org&client_id=%s" % (APP_ID)

    def parse_event(self, event_dict):
        #http://stackoverflow.com/questions/1302161/how-do-i-parse-timezones-with-utc-offsets-in-python
        event = event_dict.copy() #shallow copy
        times = 'end_time updated_time start_time'.split()
        for k in times:
            if k in event:
                if type(event[k]) == type(None):
                    del event[k]
                    continue
                elif type(event[k]) == int:
                    event[k] = datetime.fromtimestamp(event[k])
                else:
                    event[k] = parse(event[k])
                if 'timezone' in event and type(event['timezone']) != type(None):
                    #http://pytz.sourceforge.net/#localized-times-and-date-arithmetic
                    event[k] = event[k].replace(tzinfo =  pytz.utc)
                    event[k] = event[k].astimezone( pytz.timezone(event['timezone']) )
        return event

    def get_events(self):
        """
        We can get all events for facebook groups and future events for facebook pages
        Get a set of events for facebook page and facebook groups
        There are 3 cases: date-only, precise time and local time(deprecated)
        Timezone information is not stored for local time.
        TODO: handle invalid access token esp. for public vs. private groups like  hackers at berkeley
        http://developers.facebook.com/docs/reference/api/event/
        >>> coke = FacebookGroup('https://www.facebook.com/cocacola') # guaranteed to work for facebook page
        >>> print len(coke.get_events()) >= 0
        True
        """
        if type(self.id) == type(None):
            self.get_id()
        try:
            if self.id == None:
                self.get_id()
            try:
                #used to get group events
                data = urllib2.urlopen('https://graph.facebook.com/'+str(self.id)+'/events?access_token='+self.user_access_token).read()
            except (urllib2.HTTPError, facebook.GraphAPIError), e:
                #https://developers.facebook.com/docs/reference/api/page/ facebook page has events
                data = urllib2.urlopen('https://graph.facebook.com/'+str(self.id)+'/events?access_token='+self.app_access_token).read()
            response = _parse_json(data)
            events = response['data']
            for event in events:
                parsed_event =  self.parse_event(event)
                event.update(parsed_event)
            self.events.extend(events)
            return events
        except urllib2.HTTPError, e:
            response = _parse_json(e.read())
            raise facebook.GraphAPIError(response)

    def generate_event_url(event_id):
        return 'https://www.facebook.com/events/'+event_id

def main():
    import os
    os.system('python -m doctest %s' % __file__)
    #hb = FacebookGroup('https://graph.facebook.com/276905079008757')


if __name__ == "__main__":
    main()
