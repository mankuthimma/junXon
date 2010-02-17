from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User

TYPES = (
    ('SYSTEMS', 'Systems'), 
    ('STAFF', 'Staff'),
    ('VENDORS', 'Vendors'),
    ('GUESTS', 'Guests'),
    )

class Subscriber(models.Model):
    name        = models.CharField(max_length=255)
    email       = models.EmailField()
    mobile      = models.CharField(max_length=12)
    remarks     = models.CharField(max_length=255)
    accesskey   = models.CharField(max_length=8, blank=True)
    ipaddress   = models.IPAddressField(blank=True)
    macaddress  = models.CharField(max_length=18, blank=True)
    # Faced issues while using the ForeignKey with reco, approved
    recommended = models.CharField(max_length=255, editable=True)
    approved    = models.CharField(max_length=255, editable=False) 
    active      = models.BooleanField(default=False)
    requested   = models.DateTimeField(auto_now=True, editable=False)
    starts      = models.DateTimeField(blank=True, null=True)
    expires     = models.DateTimeField(blank=True, null=True)
    

    def __unicode__(self):
        return self.name
    
class SubscriberForm(ModelForm):
    class Meta:
        model = Subscriber
        exclude = ('ipaddress', 'macaddress', 'approvedby', 'recommended')
        


