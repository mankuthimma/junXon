from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       (r'^login', 'junxon.checkin.views.junxon_login'),
                       (r'^accounts/login', 'junxon.checkin.views.junxon_login'),                       
                       (r'^logout', 'junxon.checkin.views.junxon_logout'),
                       (r'^accounts/logout', 'junxon.checkin.views.junxon_logout'),                       
                       (r'^status', 'junxon.checkin.views.junxon_status'),
                       (r'^toggle', 'junxon.checkin.views.toggle_connection'),                                               
                       (r'^checkin/', 'junxon.checkin.views.register'),
                       (r'^admin/(.*)', admin.site.root),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/opt/junxon/media'}),
		       (r'^.*$', 'junxon.checkin.views.junxon_req'),
                       )


