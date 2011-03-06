from django.db import models
from django.forms import ModelForm
from django.forms import Textarea
from django.contrib.auth.models import User

TYPES = (
    ('SYSTEMS', 'Systems'), 
    ('STAFF', 'Staff'),
    ('VENDORS', 'Vendors'),
    ('GUESTS', 'Guests'),
    )

class Subscriber(models.Model):
    name        = models.CharField("Full Name", max_length=255)
    email       = models.EmailField("Email")
    mobile      = models.CharField("Mobile", max_length=12)
    company     = models.CharField("Company", max_length=255)
    remarks     = models.CharField("Project details with work order number / Remarks", max_length=255)
    accesskey   = models.CharField("Access Key", max_length=8, blank=True)
    ipaddress   = models.IPAddressField("IP Address", default="127.0.0.1", blank=True)
    macaddress  = models.CharField("MAC Address", max_length=18, blank=True)
    # Faced issues while using the ForeignKey with reco, approved
    recommended = models.CharField("Facilities Coordinator / Recommended by", max_length=255, editable=True)
    approved    = models.CharField("Approved by", max_length=255, editable=False) 
    active      = models.BooleanField("Active?", default=False)
    requested   = models.DateTimeField(auto_now=True, editable=False)
    starts      = models.DateTimeField("Starts on", blank=True, null=True)
    expires     = models.DateTimeField("Expires on", blank=True, null=True)
    

    def __unicode__(self):
        return self.name
    
class SubscriberForm(ModelForm):
    class Meta:
        model = Subscriber
        exclude = ('ipaddress', 'macaddress', 'approvedby', 'recommended')
        widgets = {
            'remarks': Textarea(attrs={'cols': 80, 'rows': 20}),
            }
