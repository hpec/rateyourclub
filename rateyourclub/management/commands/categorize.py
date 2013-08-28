from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, IntegrityError
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from clubreview.models import *
import operator
import re
import pdb

determinstic_words = {
    'Academic':['academic',],
    'Profession':['professional', 'professionals', 'financial', 'profession','entrepreneurship', 'entrepreneurs'],
    'Service':['service', 'services', 'communities', 'community', 'welfare', 'volunteer', 'volunteers'],
    'Cultural':['cultural', 'china', 'chinese', 'japan', 'japanese', 'african', 'afghan'],
    'Religious':['jewish', 'christian', 'christ'],
    'Arts':['art', 'performance', 'artistic'],
    'Sport':['sport', 'athletics', 'athletic', 'tournament', 'basketball', 'football', 'soccer', 'badminton', 'archery', 'tennis', 'swim'],
    'Political':['polictics', 'politic', 'Polictical'],
}

CATEGORIES = determinstic_words.keys()

def find(word1, word2):
    return len(re.findall(r'\b' + word1 + r'\b', word2, re.IGNORECASE))

def main():

    # related_words = {
    #     'art':['art', 'arts', , 'op art', 'pop art', 'art deco', 'art form', 'art house', 'art-house', 'clip art', 'fine art', 'art gallery', 'art nouveau', 'art therapy',  'kinetic art', 'martial art', 'art director', 'conceptual art', "objet d'art", 'performance art', 'work of art', 'state-of-the-art', 'the black art', 'thou art', 'noble art', 'craft', 'craftsmanship', 'ingenuity', 'mastery', 'artistry', 'imagination', 'Biedermeier', 'Parian', 'Queen Anne', 'annulate', 'anomphalous', 'banded', 'chryselephantine', 'aperture', 'collared', 'artificial', 'condensed', 'camera', 'copied'],

    #     'sport':['athletcis', 'recreation', 'candidacy', 'championship', 'clash', 'contention', 'event', 'fight', 'game', 'match', 'race', 'rivalry', 'run', 'sport', 'sports', 'struggle', 'tournament', 'trial', 'basketball', 'football', 'soccer', 'badminton', 'archery', 'tennis', 'swim']
    # }
    result = dict()
    clubs = list(Club.objects.all())
    print len(clubs)

    for club in clubs:
        score = 0
        # try:
        if club.introduction:
            intro = club.introduction
        else:
            intro = ''
        name = club.name
        max_score = 0
        max_cat = None
        for category in CATEGORIES:
            all_words = wordpunct_tokenize(intro.lower())
            all_name_words = wordpunct_tokenize(name.lower())
            score = 0
            for word in determinstic_words[category]:
                score += all_words.count(word) * 2
                score += all_name_words.count(word) * 10
            if score > max_score:
                max_cat = category
                max_score = score

        if max_cat and max_score > 2:
            category = Category.objects.get(name=max_cat)
            club.category = category
            club.save()

            try:
                # print name, max_cat, max_score
                result[max_cat].append(name)
            except KeyError:
                result[max_cat] = [name, ]

    for category in CATEGORIES:
        print category
        try:
            for club in result[category]: print club
        except:
            pass
        print '\n'

def show_word_stats():
    clubs = list(Club.objects.all())
    stats = {}
    for club in clubs:
        try:
            tmp = wordpunct_tokenize(club.name.lower())
            for word in tmp:
                try:
                    stats[word] += 1
                except KeyError:
                    stats[word] = 1
        except:
            continue

    sorted_x = sorted(stats.iteritems(), key=operator.itemgetter(1))
    for a, b in sorted_x:
        print a, b


def create_categories():
    print "Creating Category ..."
    for category_name in CATEGORIES:
        try:
            category = Category.objects.create(name=category_name)
        except IntegrityError:
            print "Category Already Exists:", category_name
            transaction.rollback()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # create_categories()
        main()
        # show_word_stats()




