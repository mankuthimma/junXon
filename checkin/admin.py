##
## admin.py
## Author : <shashi@inf.in>
## Started on  Wed Feb 10 15:38:26 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA

from junxon.checkin.models import Subscriber
from django.contrib import admin
from netfilter.rule import Rule, Match
from netfilter.table import Table

import Pyro.naming, Pyro.core

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('name','email','mobile','active', 'expires')
    ordering = ['name']
    list_per_page = 50
    search_fields = ['name','email']
    #     fields = ('accesskey', 'ipaddress')

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
            elif ((obj.macaddress is not None) and (obj.ipaddress is not None)):
                # Add IP/Mac to DHCP                
                j.gen_dhcpd_conf(obj.ipaddress, obj.macaddress)
                # Add a Masquerade rule to the set
                # TODO: move function to junxonlib                
                rule_masquerade = Rule(
                    source = obj.ipaddress,
                    jump = 'MASQUERADE')
                
                rule_restrict = Rule(
                    source = obj.ipaddress,
                    matches = [Match('mac', '--mac-source '+obj.macaddress)],
                    jump = 'ACCEPT')

                table = Table('nat')
                table.prepend_rule('POSTROUTING', rule_masquerade)
                table.prepend_rule('PREROUTING', rule_restrict) 

        if (obj.active == False):
            if ((obj.macaddress is not None) and (j.is_mac_dhcped(obj.macaddress))):
                j.remove_dhcp_record_by_mac(obj.macaddress)
                # Add a Masquerade rule to the set
                # TODO: move function to junxonlib
                rule_masquerade = Rule(
                    source = obj.ipaddress,
                    jump = 'MASQUERADE')
                
                rule_restrict = Rule(
                    source = obj.ipaddress,
                    matches = [Match('mac', '--mac-source '+obj.macaddress)],
                    jump = 'ACCEPT')

                table = Table('nat')
                table.delete_rule('POSTROUTING', rule_masquerade)
                table.delete_rule('PREROUTING', rule_restrict) 

            
                
        obj.approved = request.user
        obj.save()
        


admin.site.register(Subscriber, SubscriberAdmin)
