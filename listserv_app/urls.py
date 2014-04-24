from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'emails.views.stats', name='stats'),
    url(r'^(?P<site>\w+)/$', 'emails.views.stats', name='stats'),
    url(r'^admin/', include(admin.site.urls)),
)
