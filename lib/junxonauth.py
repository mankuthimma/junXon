##
## junxonauth.py
## Author : <shekhar@inf.in>
## Started on  Fri May 14 11:28:18 2010 Shashishekhar S
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

from django.contrib.auth.models import User, check_password
from checkin.models import Subscriber
from django.http import HttpRequest

import sys

class JunxonBackend:

    def authenticate(self, username=None, password=None, request=None):

        try:
            subchk = Subscriber.objects.get(email=username)
            if (password == subchk.accesskey):
                passwd_valid = True
            else:
                passwd_valid = False

            rem_ipaddress = request.META.get('REMOTE_ADDR')
#	    if (subchk.ipaddress != rem_ipaddress):
#		passwd_valid = False
		
            print >>sys.stderr, "User authenticated: ", username
 
        except Subscriber.DoesNotExist:
            print >>sys.stderr, "User not found: ", username
            return None

        if passwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username, password=subchk.accesskey)
                user.is_staff = False
                user.is_superuser = False
                user.first_name = subchk.name
                user.is_active = True
                user.email = username
                user.save()

            return user
        return None
    
                
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        
        
        
