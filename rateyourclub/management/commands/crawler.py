from django.core.management.base import BaseCommand, CommandError
from clubreview.models import *
from bs4 import BeautifulSoup
import urllib2
import re
import pdb


def main():
    def parse(url):
        print url
        soup = BeautifulSoup(urllib2.urlopen(url).read())
        content = soup.find(id='node-2810')
        clubname = content.find_all('b')[0].string
        clubname = re.sub('[\r|\t|\n]','',clubname)
        print clubname
        abbrev = re.search(r'\((.+?)\)$', clubname)
        if abbrev:
            abbrev = abbrev.group(0)[1:-1]
        #content = str(content.findAll(text=True))
        #content = content.replace(u'\r', '').replace(u'\t', '').replace(u'\n', '')
        intro = re.search(r'Purpose: (.+?<p>)', str(content))
        #print intro
        if intro:

            content_str = str(content).replace('\t','').replace('\n','').replace('\r','')
            start = content_str.index('Purpose')
            end = content_str.index('This group has been viewed')
            content_str = content_str[start:end]
            content_str = content_str.replace(str(intro.group(0)), '')

            website = BeautifulSoup(content_str.replace('<p>','').replace('</p>',''))
            
            #pdb.set_trace()
            website = website.findAll('a', href=True)
            if website:
                website = website[0].get('href')
                #print 'Website:', website

            #website = re.search(r'http://[\w.-~/]+', content_str)
            #if website:
            #    website = website.group(0)
            #    print 'Website: ', website
            email = re.search(r'Email: [^@<>]+@[^@<>]+\.[^@<>]+', content_str)
            if email:
                email = email.group(0)[7:]
                #print 'Email:', email
            


            #cut_length = 
            #content_str = content.get_text().encode('ascii','ignore').replace('\t','').replace('\n','').replace('\r','')
            #start = content_str.index('Purpose')
            #end = content_str.index('This group has been viewed')
            #content_str = content_str[start:end]
            #content_str = content_str.replace(str(intro.group(0)), '')
            #content_str = re.sub(r'Purpose: (.+?)','', content_str)
            intro = intro.group(0)[9:-3]
            additional = content_str.replace(str(website), '').replace(str(email), '').split('<br/>')
            #if url == 'http://students.berkeley.edu/osl/studentgroups/public/index.asp?todo=getgroupinfo&SGID=15133':
            #    pdb.set_trace()

            for i in additional:
                if not ('URL' in i or 'Email' in i):
                    tmp = i.split('<p></p>')
                    for j in tmp[:]:
                        if j == '' or j == '<i>':
                            tmp.remove(j)
                    if tmp != ['</p>'] and tmp != []:
                        print tmp

            #content = content.
            #print 'Addition content', content

            
        try:
            pass
            #school = School.objects.get(name='UC Berkeley')
            #club = Club.objects.create(name=clubname, abbrev=abbrev, introduction=intro, school=school)
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
    content = soup.find(id='node-2810').prettify()
    content = content.replace('&amp;','&')
    gid_list = re.findall(r'SGID=(\d+)', content)
    url_list = list()
    
    for gid in gid_list:
        #print gid
        parse(str(GROUP_INFO_BASE_URL+gid))

class Command(BaseCommand):
    def handle(self, *args, **options):
        main()

