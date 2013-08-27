from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from clubreview.views import *
from clubreview.lookups import club_lookup
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from registration.views import register

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
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
    url(r'^clubs/([a-zA-Z0-9|-]+)/$', club_info_view, name='club_info_view'),
    url(r'^clubs/search/', club_lookup),
    url(r'^clubs/(\d+)/update', add_url_edit),
    url(r'^reviews/create/$', create_review, name='create_review'),
    url(r'^register/', register),
    url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.urls')),
    (r'^selectable/', include('selectable.urls')),
    #url(include('clubreview.urls'))

)
urlpatterns += staticfiles_urlpatterns()
