from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from junxon.checkin.models import Subscriber, SubscriberForm
from random import choice


def register(request):
    strings = 'abcdefghijklmnopqrstuvwxyz0123456789'
    try:
        name = request.POST['name']
    except (KeyError, Subscriber.DoesNotExist):
        return render_to_response('checkin/register.html')
    else:
        subscriber = Subscriber(ipaddress='0.0.0.0')
        form = SubscriberForm(request.POST, instance=subscriber)
        form.save(commit=False)
        subscriber.accesskey = ''.join([choice(strings) for i in range(8)])
        subscriber.save()
        return render_to_response('checkin/acknowledgement.html', {'subscriber': subscriber})
    

