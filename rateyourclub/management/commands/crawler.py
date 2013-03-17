from django.core.management.base import BaseCommand, CommandError
from clubreview.models import *
from bs4 import BeautifulSoup
import urllib2
import re


def main():
    def parse(url):
        #print url
        soup = BeautifulSoup(urllib2.urlopen(url).read())
        main_content = soup.find(id='node-2810')
        clubname = main_content.find_all('b')[0].string
        clubname = re.sub('[\r|\t|\n]','',clubname)
        #print str(main_content)
        intro = re.search(r'Purpose: (.+?<p>)', str(main_content))
        if intro:
            intro = intro.group(0)[9:-3]


        abbrev = re.search(r'\((.+?)\)$', clubname)
        if abbrev:
            abbrev = abbrev.group(0)[1:-1]
        try:
            club = Club.objects.create(name=clubname, abbrev=abbrev, introduction=intro, school=school)
            #club.save()
        except:
            print url
            print clubname
        #print clubname
        #print intro
        #print

    GREEKS_BASE = 'http://lead.berkeley.edu/greek/recognized_chapters'
    GROUPS_BASE = 'http://students.berkeley.edu/osl/studentgroups/public/index.asp?todo=listgroups'
    GROUPS_BASE_URL = 'http://students.berkeley.edu'

    GROUP_INFO_BASE_URL = 'http://students.berkeley.edu/osl/studentgroups/public/index.asp?todo=getgroupinfo&SGID='

    soup = BeautifulSoup(urllib2.urlopen(GROUPS_BASE).read())
    main_content = soup.find(id='node-2810').prettify()
    main_content = main_content.replace('&amp;','&')
    gid_list = re.findall(r'SGID=(\d+)', main_content)
    url_list = list()
    school = School.objects.get(name='UC Berkeley')
    for gid in gid_list:
        #print gid
        parse(str(GROUP_INFO_BASE_URL+gid))

class Command(BaseCommand):
    def handle(self, *args, **options):
        main()

