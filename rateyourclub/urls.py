from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from clubreview.views import *
from clubreview.lookups import club_lookup

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
    url(r'^clubs/(\d+)/update', add_url_edit),
    url(r'^reviews/create/$',
        create_review,
        name='create_review'),
    url(r'^clubs/search/', club_lookup),
    # url(r'^base$',
    #     TemplateView.as_view(template_name='base.html')),
    (r'^selectable/', include('selectable.urls')),
    url(r'^clubs/([a-zA-Z0-9|-]+)/$',
        club_info_view,
        name='club_info_view'),
)
