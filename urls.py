from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^simple/', include('simple.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.urls')),
)
