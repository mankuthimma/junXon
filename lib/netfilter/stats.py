##
## stats.py
## Author : <shashi@inf.in>
## Started on  Fri Feb 19 10:16:38 2010 Shashishekhar S
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

import os
import popen2
import sys
import re
import subprocess

from netfilter.rule import Rule,Match,Target
from netfilter.table import Table, IptablesError

class Readings:

    def __init__(self):
        self.chain = "FORWARD"
        self.zero  = True
        self._iptables = 'iptables'
        self.table = "mangle"

    def getstats(self, dirn="in"):
        if (dirn == "out"):
            rules = self._listrules_out()
        else:
            rules = self._listrules_in()            
        #         expr = re.compile("^\s+\d+\s+(\d+).*MAC\s+([\d\w:]+).*set\s+.*$")
        # 441   518186 CONNMARK   all  --  *      *       0.0.0.0/0            192.168.1.17        CONNMARK xset 0x16/0xffffffff 
        # 463    46097 CONNMARK   all  --  *      *       192.168.1.17         0.0.0.0/0           CONNMARK xset 0x16/0xffffffff 
        expr = re.compile("^\s+\d+\s+(\d+)\s+CONNMARK\s+.*?CONNMARK\s+xset\s+(0x\d+)/.*$")
        readings = {}
        for r in rules:
            if ((r.find("Chain") >= 0) or (r.find("pkts") >= 0) or (r.find("Zeroing") >= 0)):
                continue
            else:
                m = re.findall(expr, r)
                if ((len(m) == 1) and (len(m[0]) == 2)):
                    match = m[0]
                    readings[int(match[1], 0)] = int(match[0])
        return readings

    def _listrules_in(self):
        _cmd = [self._iptables, "-t", self.table]
        if (self.zero is True):
            _cmd.append("-Z")
        _cmd.extend(("-L", "in_traffic"))
        _cmd.extend(("-n","-v","-x"))
        result = self.__run(_cmd)
        return result

    def _listrules_out(self):
        _cmd = [self._iptables, "-t", self.table]
        if (self.zero is True):
            _cmd.append("-Z")
        _cmd.extend(("-L", "out_traffic"))
        _cmd.extend(("-n","-v","-x"))
        result = self.__run(_cmd)
        return result

    def __run(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        out, err = p.communicate()
        status = p.wait()
        # check exit status
        if not os.WIFEXITED(status) or os.WEXITSTATUS(status):
            if not re.match(r'iptables: Chain already exists', err):
                raise IptablesError(cmd, err)
        return out.splitlines(True)


if __name__ == "__main__":
    r = Readings()
    print r.getstats("out")
