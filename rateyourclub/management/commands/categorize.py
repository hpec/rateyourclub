from django.core.management.base import BaseCommand, CommandError
from clubreview.models import *
import operator
import re
import pdb

def find(word1, word2):
    return re.search(r'\b' + word1 + r'\b', word2, re.IGNORECASE)

def main():
    related_words = {
        'art':['art', 'arts', 'artistic', 'op art', 'pop art', 'art deco', 'art form', 'art house', 'art-house', 'clip art', 'fine art', 'art gallery', 'art nouveau', 'art therapy',  'kinetic art', 'martial art', 'art director', 'conceptual art', "objet d'art", 'performance art', 'work of art', 'state-of-the-art', 'the black art', 'thou art', 'noble art', 'craft', 'craftsmanship', 'ingenuity', 'mastery', 'artistry', 'imagination', 'Biedermeier', 'Parian', 'Queen Anne', 'annulate', 'anomphalous', 'banded', 'chryselephantine', 'aperture', 'collared', 'artificial', 'condensed', 'camera', 'copied'],

        'sport':['athletcis', 'recreation', 'candidacy', 'championship', 'clash', 'contention', 'event', 'fight', 'game', 'match', 'race', 'rivalry', 'run', 'sport', 'sports', 'struggle', 'tournament', 'trial', 'basketball', 'football', 'soccer', 'badminton', 'archery', 'tennis', 'swim']
    }
    result = dict()
    clubs = list(Club.objects.all())
    print len(clubs)

    for club in clubs:
        score = 0
        try:
            intro = club.introduction
            name = club.name
            for word in related_words['sport']:
                if find(word, intro) or find(word, name):
                    score += 1
        except:
            continue
        result[club.name] = score

    sorted_result = reversed(sorted(result.iteritems(), key=operator.itemgetter(1)))
    # pdb.set_trace()
    # print sorted_result
    for item in sorted_result:
        print item



class Command(BaseCommand):
    def handle(self, *args, **options):
        main()