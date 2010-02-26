from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       (r'^checkin/', 'junxon.checkin.views.register'), 
                       (r'^admin/(.*)', admin.site.root),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/opt/junxon/media'}),
                       )


