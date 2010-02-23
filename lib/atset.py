##
## atset.py
## Author : <shashi@inf.in>
## Started on  Mon Feb 22 17:13:56 2010 Shashishekhar S
## $Id$
## 
## Copyright (C) 2010 INFORMEDIA TECHNOLOGIES (MYSORE) PRIVATE LIMITED
##

import os, sys, re
from subprocess import Popen, PIPE

class AtSet:

    def __init__(self):
        self.junxon_util = "/opt/junxon/utils/junxon-tool.py" # HACK-ALERT!!! Move into config
        self.atcmd = "/usr/bin/at"

    def at(self, when, ipaddress, macaddress):
        """ what = (ipaddress, macaddress) """
        
        _cmd = [self.junxon_util, "--ipaddress="+ipaddress, "--mac-address="+macaddress]
        _echo = ["echo", ' '.join(_cmd)]
        sys.stderr.write("cmd: "+' '.join(_echo))
        _at = [self.atcmd, when]
        sys.stderr.write("at: "+' '.join(_at))        
        bef = Popen(_echo, stdout=PIPE)
        aft = Popen(_at, stdin=bef.stdout, stdout=PIPE)

        out = aft.communicate()
        return out
    
