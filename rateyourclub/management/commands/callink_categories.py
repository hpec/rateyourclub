from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
import urllib, requests, re

class CallinkClub(object):
    def __init__(self, name, permalink, abbrev = None):
        self.name = name
        self.permalink = permalink
        self.abbrev = abbrev
    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__, unicode(self.name.encode('utf8'), errors='ignore'))


class CallinkCategory(object):
    categories = [(5098,"Academic Student Organizations"),
    (5100,"Arts Student Organizations"),
    (2687,"ASUC Government Offices"),
    (5102,"ASUC Government Programs"),
    (2692,"ASUC Publication Groups"),
    (2693,"ASUC Student Activity Groups"),
    (2694,"ASUC Student Initiated Service Groups"),
    (2688,"Berkeley Public Service Center Designated"),
    (5101,"Campus Departments"),
    (5104,"Cultural & Identity Student Organizations"),
    (5105,"Departmental Student Organizations"),
    (5107,"Environmental & Sustainability Student Organizations"),
    (2689,"ES - Ethnic Studies"),
    (5108,"Fraternity & Sorority Support Organizations"),
    (2690,"GA Government Offices"),
    (5103,"GA Government Projects"),
    (2691,"GSG - Graduate Student Groups"),
    (5109,"Health & Wellness Student Organizations"),
    (5110,"Interfraternity Council (IFC) Fraternities"),
    (5111,"Media & Film Student Organizations"),
    (5112,"Multicultural Greek Council (MCGC) Fraternities & Sororities"),
    (5137,"National Pan-Hellenic Council (NPHC) Fraternities & Sororities"),
    (5138,"Panhellenic Council (PHC) Sororities"),
    (5113,"Performing Arts Student Organizations"),
    (5114,"Political & Advocacy Student Organizations"),
    (5115,"Professional Student Organizations"),
    (5116,"Publication Student Organizations"),
    (5117,"Recreational Student Organizations"),
    (5118,"Service Student Organizations"),
    (5119,"Spiritual Student Organizations"),
    (5120,"Technology Student Organizations"),]
    @classmethod
    def all(self):
        return map( lambda meta : CallinkCategory(id=meta[0], name=meta[1]), CallinkCategory.categories)
    def __init__(self, **kwargs):
        kwargs.setdefault('page', 1)
        kwargs.setdefault('name', None)
        kwargs.setdefault('id', None)
        self.name = kwargs['name']
        self.id = kwargs['id']
        self._page = kwargs['page']
        self._last_result = []
        self._done = False
        self._results = []

    @property
    def qs(self):
        return qs_at_page()

    def qs_at_page(self, page = None):
        return urllib.urlencode(self.params(page = page or self._page))

    def params(self, page = None):
        return {'SearchValue': self.name,
         'SearchType' : 'Category',
         'CurrentPage' : page or self._page,
         'SelectedCategoryId' : self.id }

    def url_at_page(self, page = None):
        return "https://callink.berkeley.edu/organizations?" + self.qs_at_page(page or self._page)
    
    @property
    def url(self):
        return self.url_at_page()

    def get_abbrev(self, name):
        res  = re.findall(r'\(([^\(^\)]*)\)', name)
        if len(res) > 0:  return res[-1]

    def get(self, page = None):
        response  = requests.get(self.url_at_page(page or self._page))
        if response.status_code == 200:
            soup = BeautifulSoup(response.text)
            result_soup = soup.select(".result h5")
            return  map(lambda r: CallinkClub(r.a.text, r.a.get("href").replace('/organization/',''), self.get_abbrev(r.a.text)), result_soup)

    @property
    def clubs(self):
        if len(self._results) == 0:
            for club in self.club_iterator:
                self._results.append(club)
        return self._results

    @property
    def club_iterator(self):
        page = 1
        results = []
        last_result = []
        club = None
        just_parsed = False

        while(not club in results) :
            if club : results.append(club)

            if len(last_result) == 0:
                last_result  = self.get( page = page )
                page += 1

            club = last_result.pop(0)

            yield club



    def __repr__(self):
        return "<%s> %s #%s" % (self.__class__.__name__, unicode(self.name.encode('utf-8'), errors='ignore'), self.id)

def main():
    for category in CallinkCategory.all():
        for i, club in enumerate(category.club_iterator):
            #TODO store into database
            print club

class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
