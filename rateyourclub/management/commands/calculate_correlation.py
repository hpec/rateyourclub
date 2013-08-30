from django.core.management.base import BaseCommand, CommandError
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from clubreview.models import *
import operator
import re
import pdb
import nltk

nltk.data.path.append('./nltk_data/')

def sim(a,b):
    intersect = set(a).intersection(set(b))
    result = 0
    for x in intersect:
        result += min(a.count(x), b.count(x))
    return result

def tokenize(text):
    word_list = []
    if text:
        word_list = wordpunct_tokenize(text.lower())
        word_list = [w for w in word_list if w not in nltk.corpus.stopwords.words('english') and w not in common_words]
        word_list = nltk.pos_tag(word_list)
        word_list = [word for word, x in word_list if x == 'NN']
    return word_list


def main():
    common_words = ['berkeley', 'dwinelle', 'association', 'associations', 'club', 'clubs', 'students', 'student', 'organization', 'organizations']
    result = dict()
    clubs = list(Club.objects.all())
    clubs_with_intro = list()
    for club in clubs:
        intro = club.introduction
        name = club.name
        clubs_with_intro.append((club, tokenize(intro), tokenize(name)))

    for i in range(len(clubs_with_intro)):
        club_i, intro_i, name_i = clubs_with_intro[i]
        result = dict()
        for j in range(len(clubs_with_intro)):
            if i!=j:
                club_j, intro_j, name_j = clubs_with_intro[j]
                score = sim(intro_i, intro_j) * 1.0 # / len(intro_j)
                score += sim(name_i, name_j) * 2.0
                if club_i.category and club_i.category == club_j.category: score += 5
                result[club_j] = score
        result = sorted(result.iteritems(), key=operator.itemgetter(1), reverse=True)[:4]
        print club_i, result, '\n'
        club_i.related_clubs = ','.join([str(club.id) for club, score in result])
        club_i.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()


