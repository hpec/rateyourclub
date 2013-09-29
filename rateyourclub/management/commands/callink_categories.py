from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
import urllib, requests

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
        self.results = []
    @property
    def qs(self):
        return urllib.urlencode({'SearchValue': self.name,
         'SearchType' : 'Category',
         'CurrentPage' : self._page,
         'SelectedCategoryId' : self.id
         })

    @property
    def url(self):
        return "https://callink.berkeley.edu/organizations?" + self.qs
    def next(self):
        if not self._done:
            response  = requests.get(self.url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text)
                result_soup = soup.select(".result h5")
                results = map(lambda r: (r.a.text, r.a.get("href")), result_soup)
                if results and results[0] in self.results:
                    self._done = True
                    return
                else:
                    self.results += results
                    self._page += 1
                    return results
    @property
    def clubs(self):
        import pprint
        next_result = self.next()
        while(next_result):
            pprint.pprint(next_result)
            next_result = self.next()
        return self.results



    def __repr__(self):
        return "<%s> %s #%s" %(self.__class__.__name__, self.name, self.id)

