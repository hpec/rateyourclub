from django.core.management.base import BaseCommand, CommandError
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from clubreview.models import *
import operator
import re
import pdb
import nltk

def sim(a,b):
    # intro_a = a.introduction
    # intro_b = b.introduction
    # if intro_a and intro_b:
    #     intro_a = intro_a.lower()
    #     intro_b = intro_b.lower()
    #     word_list_a = wordpunct_tokenize(intro_a)
    #     word_list_a = set([w for w in word_list_a if not w in nltk.corpus.stopwords.words('english')])
    #     word_list_b = wordpunct_tokenize(intro_b)
    #     word_list_b = set([w for w in word_list_b if not w in nltk.corpus.stopwords.words('english')])
    #     return len(word_list_a.intersection(word_list_b))
    # else:
    #     return 0
    intersect = set(a).intersection(set(b))
    result = 0
    for x in intersect:
        result += min(a.count(x), b.count(x))
    return result

def main():
    common_words = ['berkeley', 'dwinelle', 'association', 'associations', 'club', 'clubs', 'students', 'student']
    # related_words = {
    #     'art':['art', 'arts', , 'op art', 'pop art', 'art deco', 'art form', 'art house', 'art-house', 'clip art', 'fine art', 'art gallery', 'art nouveau', 'art therapy',  'kinetic art', 'martial art', 'art director', 'conceptual art', "objet d'art", 'performance art', 'work of art', 'state-of-the-art', 'the black art', 'thou art', 'noble art', 'craft', 'craftsmanship', 'ingenuity', 'mastery', 'artistry', 'imagination', 'Biedermeier', 'Parian', 'Queen Anne', 'annulate', 'anomphalous', 'banded', 'chryselephantine', 'aperture', 'collared', 'artificial', 'condensed', 'camera', 'copied'],

    #     'sport':['athletcis', 'recreation', 'candidacy', 'championship', 'clash', 'contention', 'event', 'fight', 'game', 'match', 'race', 'rivalry', 'run', 'sport', 'sports', 'struggle', 'tournament', 'trial', 'basketball', 'football', 'soccer', 'badminton', 'archery', 'tennis', 'swim']
    # }
    result = dict()
    clubs = list(Club.objects.all())
    clubs_with_intro = list()
    for club in clubs:
        intro = club.introduction
        if intro:
            word_list = wordpunct_tokenize(intro.lower())
            word_list = [w for w in word_list if not w in nltk.corpus.stopwords.words('english') and not w in common_words]
            word_list = nltk.pos_tag(word_list)
            word_list = [word for word, x in word_list if x == 'NN']
            clubs_with_intro.append((club, word_list))

    for i in range(len(clubs_with_intro)):
        club_i, intro_i = clubs_with_intro[i]
        max_relation = 0
        max_club = None
        result = dict()
        for j in range(len(clubs_with_intro)):
            if i!=j:
                club_j, intro_j = clubs_with_intro[j]
                score = sim(intro_i, intro_j) * 1.0 # / len(intro_j)
                if club_i.category and club_i.category == club_j.category: score += 5
                result[club_j] = score
                # if tmp > max_relation:
                #     max_relation = tmp
                #     max_club = club_j
        result = sorted(result.iteritems(), key=operator.itemgetter(1), reverse=True)[:4]
        print club_i, result, '\n'
        club_i.related_clubs = ','.join([str(club.id) for club, score in result])
        club_i.save()
        # print club_i, ",", max_club
            # correlation = Correlation.get_or_create(club_a=clubs[i], club_b=clubs[j])
            # correlation.value = sim(clubs[i], clubs[j])
            # correlation.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()




