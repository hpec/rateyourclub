import os,re, urllib2

USER_ACCESS_TOKEN = ''

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
    Retrieve your access token here https://developers.facebook.com/tools/explorer/
    Inspiration from fbconsole and facebook-sdk
    '''
    def __init__(self, url, access_token = USER_ACCESS_TOKEN):
        self.url = url.strip()
        self.id = None
        self.events = []
        self.access_token = access_token
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
        TODO: complete parser
        """
        data = urllib2.urlopen('http://graph.facebook.com/'+self.id+'/events?access_token='+self.access_token).read()
        response = _parse_json(data)
        pass
    def generate_event_url(event_id):
        return 'https://www.facebook.com/events/'+event_id

def main():
    import os
    os.system('python -m doctest %s' % __file__)

if __name__ == "__main__":
    main()
