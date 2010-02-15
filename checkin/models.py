from django.db import models
from django.forms import ModelForm

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
    recommended = models.CharField(max_length=50, blank=True)    
    approved    = models.CharField(max_length=50, blank=True) 
    active      = models.BooleanField(default=False)
    requested   = models.DateTimeField(auto_now=True, editable=True)
    starts      = models.DateTimeField(blank=True, null=True)
    expires     = models.DateTimeField(blank=True, null=True)
    

    def __unicode__(self):
        return self.name
    
        

        
class SubscriberForm(ModelForm):
    class Meta:
        model = Subscriber
        exclude = ('ipaddress', 'macaddress', 'approvedby', 'recommended')
        


