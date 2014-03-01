from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from clubreview.views import *
from clubreview.models import *
from clubreview.lookups import club_lookup
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.sitemaps import GenericSitemap
from registration.views import register

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
sitemaps = {
    'club': GenericSitemap({'queryset': Club.objects.all()}, priority=0.8),
    'events': GenericSitemap({'queryset': Event.objects.all()}, priority=0.4),
}

admin.autodiscover()
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rateyourclub.views.home', name='home'),
    # url(r'^rateyourclub/', include('rateyourclub.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', landing, name='home'),
    url(r'^landing/$', landing, name='landing'),
    url(r'^clubs/$', club_list_view, name='club_list_view'),
    url(r'^clubs/search/', club_lookup),
    url(r'^clubs/([a-zA-Z0-9|-]+)/$', club_info_view, name='club_info_view'),
    url(r'^clubs/(\d+)/update/$', add_url_edit),
    url(r'^clubs/(\d+)/subscribe/$', subscribe_club),
    url(r'^clubs/(\d+)/unsubscribe/$', unsubscribe_club),
    url(r'^events/(\d+)/$', event_info_view, name='event_info_view'),
    url(r'^events/(\d+)/ical/$', event_ical_view, name='event_ical_view'),
    url(r'^reviews/$', review_list, name='review_list'),
    url(r'^reviews/create/$', create_review, name='create_review'),
    url(r'^reviews/delete/(\d+)/$',delete_review, name='delete_review'),
    url(r'^reviews/restore/(\d+)/$',undelete_review, name='undelete_review'),
    url(r'^register/', register),
    url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.urls')),
    (r'^selectable/', include('selectable.urls')),
    #url(include('clubreview.urls'))
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})

)
urlpatterns += staticfiles_urlpatterns()
