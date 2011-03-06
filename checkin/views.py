from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from junxon.checkin.models import Subscriber, SubscriberForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from time import gmtime, strftime

from random import choice
import sys

import Pyro.naming, Pyro.core

def register(request):
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

    strings = 'abcdefghijklmnopqrstuvwxyz0123456789'
    try:
        name = request.POST['name']
    except (KeyError, Subscriber.DoesNotExist):
        return render_to_response('checkin/register.html')
    else:
        rem_ipaddress = request.META.get('REMOTE_ADDR')
        if (rem_ipaddress is not None):
            ip = rem_ipaddress
            mac = j.get_mac_address(ip)
        else:
            ip = "127.0.0.1"
        subscriber = Subscriber(ipaddress=ip, macaddress=mac)
        form = SubscriberForm(request.POST, instance=subscriber)
        if (form.is_valid()):
            form.save(commit=False)
            subscriber.accesskey = ''.join([choice(strings) for i in range(8)])
            subscriber.save()
            return render_to_response('checkin/acknowledgement.html', {'subscriber': subscriber, 'ip': ip, 'mac': mac})
        else:
            return render_to_response('checkin/register.html', {
                'form': form,
                }) 
    


def junxon_login(request):

    try:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password, request=request)
        if user is not None:
            login(request, user)
            #                 return render_to_response('checkin/status.html', {'login_status': True, 'message': "You're logged in"})
            return HttpResponseRedirect('/status/')
        else:
            return render_to_response('checkin/login.html', {'login_status': False, 'message': "Please enter correct information"}) 
    except KeyError:
            return render_to_response('checkin/login.html')         


def junxon_logout(request):
    logout(request)
    return HttpResponseRedirect('/status/')
    #return render_to_response('checkin/login.html')     


@login_required
def junxon_status(request):
    if (request.user is not None):
        user = Subscriber.objects.get(email=request.user)

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

        connected = False                            
        rem_ipaddress = request.META.get('REMOTE_ADDR')
        #rem_ipaddress = user.ipaddress
        if (rem_ipaddress is not None):
            ip = rem_ipaddress
            if (j.check_subscription(ip)):
                connected = True
		try:
			user.last_seen_online = strftime("%Y-%m-%d %H:%M:%S", gmtime())
			user.save()
            		print >>sys.stderr, "Able to update last_seen info: ", user.email
		except:
            		print >>sys.stderr, "Not able to update last_seen info: ", user.email
		
        return render_to_response('checkin/status.html', {'user': user, 'connected': connected})
    else:
        return render_to_response('checkin/login.html')                 


@login_required
def toggle_connection(request):
    if (request.user is not None):
        user = Subscriber.objects.get(email=request.user)

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

        connected = False                            
        rem_ipaddress = request.META.get('REMOTE_ADDR')
        #if (user.ipaddress is not None):
        if (rem_ipaddress is not None):
          #  ip = user.ipaddress
            ip = rem_ipaddress
            if (j.check_subscription(ip)):
                j.disable_subscription(ip, user.macaddress)
                return HttpResponse("disabled", mimetype='application/javascript')
            else:
                expiry = user.expires.strftime('%I:%M%p %b %d')
                j.enable_subscription(ip, user.macaddress, expiry)
                return HttpResponse("enabled", mimetype='application/javascript')                

        return HttpResponse("success", mimetype='application/javascript')                    
    else:
        return HttpResponse("failure", mimetype='application/javascript')                    
    
def junxon_req(request):
	#return HttpResponseRedirect('http://218.248.43.21/status/');
	return HttpResponseRedirect('http://192.168.9.254/status/');


def currentlyonline(request):
        return render_to_response('checkin/currentlyonline.html')                 
