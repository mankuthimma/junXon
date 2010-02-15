##
## junxon.py
## Author : <shashi@inf.in>
## Started on  Mon Feb 15 13:10:21 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

import re, sys
from scapy import srp, ARP, Ether, conf
from subprocess import call

conf.verb = 0                           # Turn off verbose reporting by Scapy



class Junxon:
    """ The Junxon helper library. Provides a set of utilities to manage connection requests
        and connections itself. Has to run as root. """

    _dhcpd_conf = "/opt/junxon/cache/dhcpd.conf"
    _dhcpd_init = "/etc/init.d/dhcp3-server"
    
    def __init__(self):
        """ TODO: Move configuration params to a configfile """
        self._dhcpd_conf = "/opt/junxon/cache/dhcpd.conf"
        self._dhcpd_init = "/etc/init.d/dhcp3-server"

    def get_mac_address(self, ip):
        ans,unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),timeout=3)
        macaddress = ""
        for s,r in ans:
            macaddress = r.sprintf("%Ether.src%")
        return macaddress

    def get_online_addresses(self, pool):
        ans,unans=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=pool),timeout=2)
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
        self.restart_dhcpd()        
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
        f=open(self._dhcpd_conf,'r')
        ll = f.readlines()
        f.close()
    

        
