from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from junxon.checkin.models import Subscriber, SubscriberForm
from random import choice

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

    j = Pyro.core.getProxyForURI("PYRONAME://:junxon-service.Junxon")
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
        form.save(commit=False)
        subscriber.accesskey = ''.join([choice(strings) for i in range(8)])
        subscriber.save()
        return render_to_response('checkin/acknowledgement.html', {'subscriber': subscriber})
    

