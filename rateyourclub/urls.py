from django.conf.urls import patterns, include, url
from django.contrib import admin
from clubreview.views import *

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

    url(r'^$',
        club_list_view,
        name='club_list_view'),
    url(r'^admin/', include(admin.site.urls)),
    #url(include('clubreview.urls'))
    url(r'^clubs/$',
        club_list_view,
        name='club_list_view'),
    url(r'^clubs/(\d+)/*$',
        club_info_view,
        name='club_info_view'),
    url(r'^review/add/$',
        add_review,
        name='add_review'),
    (r'^selectable/', include('selectable.urls')),
)
