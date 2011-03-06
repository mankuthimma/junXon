##
## admin.py
## Author : <shashi@inf.in>
## Started on  Wed Feb 10 15:38:26 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA

from junxon.checkin.models import Subscriber
from junxon.actions import export_as_csv

from django.contrib import admin

from netfilter.rule import Rule, Match
from netfilter.table import Table

import Pyro.naming, Pyro.core
import re

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('name','email','mobile','active', 'expires', 'view_report')
    list_filter = ('active', 'macaddress', 'starts', 'expires')
    ordering = ['-requested']
    list_per_page = 50
    search_fields = ['name','email','mobile']
    actions = [export_as_csv]

    def save_model(self, request, obj, form, change):
        # Initialize Pyro parts
        group = ':Junxon.Server'
        
        # initialize the client and set the default namespace group
        Pyro.core.initClient()
        Pyro.config.PYRO_NS_DEFAULTGROUP=group

        # locate the NS
        locator = Pyro.naming.NameServerLocator()
        ns = locator.getNS()

        j = Pyro.core.getProxyForURI("PYRONAME://"+group)
        # j is our object proxy for junxonlib
        
        # If enabled, then check if already in DHCP
        if (obj.active == True):
            if ((obj.macaddress is not None) and (j.is_mac_dhcped(obj.macaddress))):
                pass
            elif ((obj.macaddress is not None)):
                expiry = obj.expires.strftime('%I:%M%p %b %d')
                # Add IP/Mac to DHCP                
                #j.gen_dhcpd_conf(obj.ipaddress, obj.macaddress)
                #j.enable_subscription(obj.ipaddress, obj.macaddress, expiry)
                # Add subscription to monitoring
                #pre = re.compile('(\W+)')
		#try:
	         #       _hostname = pre.sub('_', obj.name.lower())
        	 #       _hostname = str(obj.id) + '_' + _hostname
                 #	j.xr_addhost(obj.macaddress, _hostname, obj.ipaddress, str(obj.id))
		#except:
		#	pass
	

#        if (obj.active == False):
#            if ((obj.macaddress is not None) and (j.is_mac_dhcped(obj.macaddress))):
#                j.remove_dhcp_record_by_mac(obj.macaddress)
#                j.disable_subscription(obj.ipaddress, obj.macaddress)
#                j.xr_remhost(obj.ipaddress, str(obj.id))
#                

        #obj.approved = request.user
        obj.save()
        
    def view_report(self, obj):
        url_report =  '<a href="javascript:void(0)" onClick="window.open(\'/junxon/%d/daily.png\', \'view_report\', \'width=700,height=200,menubar=no,status=no\')">View Report</a>' % (obj.id)
        return url_report

    view_report.allow_tags = True
    view_report.short_description = 'Usage Report'
    

admin.site.register(Subscriber, SubscriberAdmin)
