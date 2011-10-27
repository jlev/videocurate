from django.db import models
#from django.contrib.gis.db import models as geo_models
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from embeds.models import SavedEmbed
from tagging.fields import TagField
import secretballot

from django.core.urlresolvers import reverse

class Location(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True) #for occupy locations derived by meetup feed
    
    def __unicode__(self):
        return self.name
    
    #if we want to use geodjango
#    latlon = geo_models.PointField(srid=4326)
#    objects = geo_models.GeoManager()   

LICENSE_CHOICES = (
    ('CC','Creative Commons'),
    ('NONE','No restrictions'),
    ('PROP','Proprietary, no reuse allowed'),
    ('UNK','Unknown'),
)

class Media(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    date_uploaded = models.DateTimeField()
    title = models.CharField(max_length=100) #youtube limits to 100 characters
    slug = models.SlugField()
    location = models.ForeignKey(Location)
    
    url = models.URLField()
    embed = models.ForeignKey(SavedEmbed)
    resolution = models.CharField(help_text="maximum resolution as widthXheight",blank=True, max_length=10)
    
    author_name = models.CharField(max_length=100)
    author_url = models.URLField()
    license = models.CharField(choices = LICENSE_CHOICES, max_length=10, default="UNK")
    views = models.IntegerField(help_text="views at original provider",blank=True,null=True)
    
    tags = TagField(blank=True)
    featured = models.BooleanField(default=False,help_text="make this appear on the homepage")
    
    class Meta:
        verbose_name_plural = "Media"
        get_latest_by = 'date_added'

    def get_total_upvotes(self):
        #covenience method for admin, not sure why I have to do the queryset
        return Media.objects.get(id=self.id).total_upvotes
    get_total_upvotes.short_description = "Upfists"

    def is_highres(self):
        if self.resolution:
            w,h = self.resolution.split('x')
            if w > 640 and h > 480:
                return True
        return False
    def __unicode__(self):
        return "%s - %s @ %s" % (self.author_name,self.slug,self.location)
    def get_absolute_url(self):
        return reverse('view_by_slug',kwargs={'id':self.id,'slug':self.slug})

secretballot.enable_voting_on(Media)
secretballot.enable_voting_on(Comment)
  
#class Assignment(models.Model):
#    date_added = models.DateTimeField(auto_now_add=True)
#    requester = models.ForeignKey(User) 
#    description = models.TextField()    
#    videos = models.ManyToManyField(Media)