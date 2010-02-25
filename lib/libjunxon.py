##
## junxon.py
## Author : <shashi@inf.in>
## Started on  Mon Feb 15 13:10:21 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA TECHNOLOGIES (MYSORE) PRIVATE LIMITED
##

import re, sys, time, datetime
from scapy import srp, ARP, Ether, conf
from subprocess import call

from netfilter.rule import Rule,Match
from netfilter.table import Table, IptablesError

from atset import AtSet
from libxroad import XRoad

from junxon.checkin.models import Subscriber

conf.verb = 0                           # Turn off verbose reporting by Scapy

class Junxon:
    """ The Junxon helper library. Provides a set of utilities to manage connection requests
        and connections itself. Has to run as root. """
    
    def __init__(self):
        """ TODO: Move configuration params to a configfile """
        self._dhcpd_conf = "/opt/junxon/cache/dhcpd.conf"
        self._dhcpd_init = "/etc/init.d/dhcp3-server"
        self.ip_pool = "192.168.1."

    def get_mac_address(self, ip):
        # TODO: interface should be configured in settings
        ans,unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),timeout=3,iface="eth0")
        macaddress = ""
        for s,r in ans:
            macaddress = r.sprintf("%Ether.src%")
        return macaddress

    def get_online_addresses(self, pool):
        ans,unans=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=pool),timeout=2,iface="eth1")
        hosts = []
        for s,r in ans:
            host_ip = r.sprintf("%ARP.psrc%")
            host_mac = r.sprintf("%Ether.src%")
            hosts.append((host_ip, host_mac))
        return hosts


    def gen_dhcpd_conf(self, ip, mac):
        if ((not self.is_ip_dhcped(ip)) and (not self.is_mac_dhcped(mac))):
            dh_line = "host "+ip+" {  hardware ethernet "+mac+";  fixed-address "+ip+"; }\n"
        else:
            return False
        f = open(self._dhcpd_conf,'a+')
        f.write(dh_line)
        f.close()
        self.restart_dhcpd()
        return True    

    def is_ip_dhcped(self, ip):
        expr = re.compile(ip)
        f= open(self._dhcpd_conf,'r')
        ll = f.readlines()
        for l in ll:
            match = expr.search(l)
            if match != None:
                return True
        return False

    def is_mac_dhcped(self, mac):
        expr = re.compile(mac)
        f= open(self._dhcpd_conf,'r')
        ll = f.readlines()
        for l in ll:
            match = expr.search(l)
            if match != None:
                return True
        return False

    def remove_dhcp_record_by_ip(self, ip):
        expr = re.compile(ip)
        f= open(self._dhcpd_conf,'r')
        ll = f.readlines()
        f.close()
        dh_lines = ""
        for l in ll:
            match = expr.search(l)
            if match == None:
                dh_lines += l
            nf = open(self._dhcpd_conf,'w+')
            nf.write(dh_lines)
            nf.close()
        self.restart_dhcpd()    
        return True

    def remove_dhcp_record_by_mac(self, mac):
        expr = re.compile(mac)
        f=open(self._dhcpd_conf,'r')
        ll = f.readlines()
        f.close()
        dh_lines = ""
        for l in ll:
            match = expr.search(l)
            if match == None:
                dh_lines += l
        nf = open(self._dhcpd_conf,'w+')
        nf.write(dh_lines)
        nf.close()
        self.restart_dhcpd()
        return True

    def restart_dhcpd(self):
        """ TODO: Add DHCP Config Checking """ 
        try:
            retcode = call(self._dhcpd_init + " restart", shell=True)
            if retcode < 0:
                print >>sys.stderr, "Was terminated by signal ", -retcode
                return False
            else:
                print >>sys.stderr, "Returned ", -retcode
                return True
        except OSError, e:
            print >>sys.stderr, "Execution failed: ", e
            return False

    def next_ip_address(self):
        expr = r'fixed-address (.*);'
        f=open(self._dhcpd_conf,'r')
        ll = f.readlines()
        ip_addresses = []
        for l in ll:
            m = re.findall(expr, l)
            if m[0] is not None:
                lq = int(m[0].split('.')[3])
                ip_addresses.append(lq)
        f.close()
        ip_addresses.sort()
        lq = ip_addresses.pop()
        next_ip = self.ip_pool+repr(lq+1)
        return next_ip

    def enable_subscription(self, ipaddress, macaddress, expiry=None):
        rule_masquerade = Rule(
            source = ipaddress,
            jump = 'MASQUERADE')

        rule_restrict = Rule(
            source = ipaddress,
            matches = [Match('mac', '--mac-source '+macaddress)],
            jump = 'ACCEPT')

        table = Table('nat')
        table.prepend_rule('POSTROUTING', rule_masquerade)
        table.prepend_rule('PREROUTING', rule_restrict)
        table.commit()
        sys.stderr.write("Enabling "+ipaddress+", Mac "+macaddress)
        time.sleep(3)                   # Pause

        if (expiry is not None):
            self.call_at(expiry, ipaddress, macaddress)
            
        return True

    def disable_subscription(self, ipaddress, macaddress):
        rule_masquerade = Rule(
            source = ipaddress,
            jump = 'MASQUERADE')

        rule_restrict = Rule(
            source = ipaddress,
            matches = [Match('mac', '--mac-source '+macaddress)],
            jump = 'ACCEPT')

        table = Table('nat')
        try:
            table.delete_rule('POSTROUTING', rule_masquerade)
            table.delete_rule('PREROUTING', rule_restrict)
        except IptablesError, e:
            sys.stdout.write("Ignoring non-existant rule")
        except Exception, e:
            sys.stdout.write("Unknown Error: ")            
        sys.stdout.write("Disabling "+ipaddress+", Mac "+macaddress) 
        return True

    def call_at(self, when, ipaddress, macaddress):
        a = AtSet()
        a.at(when, ipaddress, macaddress)
        return True

    def init_active(self):
        allsubs = Subscriber.objects.all()
        for eachsub in allsubs:
            # Ignore disabled
            if (eachsub.active == False):
                continue
            
            cur_time = datetime.datetime.today()
            if ((cur_time >= eachsub.starts) and (cur_time < eachsub.expires)):
                self.disable_subscription(eachsub.ipaddress, eachsub.macaddress)
                self.enable_subscription(eachsub.ipaddress, eachsub.macaddress, eachsub.expires.strftime('%I:%M%p %b %d'))
            else:
                eachsub.active=False
                eachsub.save()
        

    def xr_addhost(self, macaddress, hostname, ipaddress, oid=None):

        xrd = XRoad()
        xrd.addhost(macaddress, hostname, ipaddress, oid)
        if (oid is not None):
            xrd.markhost(str(oid), ipaddress)
        
        return True
        
        
    
if __name__=='__main__':
    
    j = Junxon()
#     j.xr_addhost("aa:bb:cc:dd:ee:ff", "16_pradeep_m", "192.168.1.17")
#     j.init_active()
#     print j.remove_subscription("192.168.1.9","aa:bb:cc:dd:ee:ee")
#     j.gen_dhcpd_conf("192.168.1.9","aa:bb:cc:dd:ee:ee")
#     print j.next_ip_address()

