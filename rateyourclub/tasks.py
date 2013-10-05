from celery import task
from rateyourclub.management.commands import crawler, callink_crawler
from clubreview.models import *

@task
def import_clubs():
    crawler.main()
@task
def add_club_events(name="add_club_events"):
    for club in Club.objects.facebook():
        try:
            club.facebook_event_update()
        except:
            pass
@task
def import_callink_crawler_data():
    callink_crawler.main(callink_crawler.updateExistingClubs)
