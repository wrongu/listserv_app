from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'charts.views.stats', name='stats'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<site>\w+)/$', 'charts.views.stats', name='stats'),
)
