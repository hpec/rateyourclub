from bs4 import BeautifulSoup
import urllib2, urllib, requests, urlparse, re

def main():
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

        if last_links == links:
            break

        for link in links:
            link = str(link)
            relative_link = re.findall(r'href="(.*?)"', link)[0]
            name =  re.findall(r'<a.*>(.*?)</a>', link)[0]
            full_url = urlparse.urljoin( BASE_URL, relative_link )
            link_dict = parse( full_url )

        last_links = links

        params['CurrentPage'] += 1
        r = requests.get(ORGANIZATION_URL, params = params)


if __name__ == "__main__":
    main()
