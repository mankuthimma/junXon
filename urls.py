from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^junxon/', include('junxon.foo.urls')),
    (r'^checkin/', 'junxon.checkin.views.register'), 

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
