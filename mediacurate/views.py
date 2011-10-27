from django.http import HttpResponse,HttpResponseRedirect,HttpResponseServerError
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from datetime import datetime
import dateutil.parser

from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from embeds.models import SavedEmbed
from mediacurate.models import Media,Location
from mediacurate.forms import AddForm

def home(request):
    if Media.objects.filter(featured=True).count() > 0:
        main = Media.objects.filter(featured=True).latest()
    else:
        main = Media.objects.order_by('total_upvotes','date_added')[0]
    latest = Media.objects.order_by('date_added').exclude(id=main.id)[:5]
    popular = Media.objects.order_by('total_upvotes').exclude(id=main.id)[:5]
    
    return render_to_response('view.html',
        {'title':'The best source for #occupy videos',
        'media':main,'popular':popular,'latest':latest},
        context_instance=RequestContext(request))
    
def latest(request,offset=None):
    return HttpResponse("latest not yet implemented")

def popular(request,offset=None):
    return HttpResponse("popular not yet implemented")

def view_by_id(request,id):
    media = get_object_or_404(Media,id=id)
    return HttpResponseRedirect(media.get_absolute_url())

def view_by_slug(request,id,slug):
    try:
        media = Media.objects.get(id=id,slug=slug)
    except Media.DoesNotExist:
        media = get_object_or_404(Media,id=id)
    return render_to_response('view.html',
        {'media':media},
        context_instance=RequestContext(request))
    
def search(request,slug):
    return HttpResponse("search not yet implemented")

def location_autocomplete_list(request):
    #return list of locations in db, #occupy first
    try:
        locations = Location.objects.filter(name__istartswith=request.GET['q']).values_list('name', flat=True)
    except MultiValueDictKeyError:
        pass	
    return HttpResponse('\n'.join(locations), mimetype='text/plain')
    
def add(request):
    form = AddForm()
    message = None
    if request.method == "POST":
        form = AddForm(request.POST)
        if form.is_valid():
            #create the objects with form.cleaned_data
            #can't use form.save() here, because it's not a modelform...
            print "form.cleaned_data",form.cleaned_data
            
            location,new = Location.objects.get_or_create(name=form.cleaned_data['location'])
            embed = SavedEmbed.objects.get(url=form.cleaned_data['url'])
            
            #TODO: convert date_uploaded to consistent format
            provider_name = embed.response['provider_name']
            try:
                date_uploaded = dateutil.parser.parse(form.cleaned_data['date_uploaded']) #TEMP, may fail
            except ValueError,e:
                return HttpResponseServerError("I don't know how to parse this date:",form.cleaned_data['date_uploaded'],"from",provider_name)
                
            #could start with copy of form.cleaned_data, but that would pull in shared form fields
            media_dict = {
                'date_uploaded':date_uploaded,
                'title':form.cleaned_data['title'],
                'slug':slugify(form.cleaned_data['title']),
                'location':location,
                'url':form.cleaned_data['url'],
                'embed':embed,
                'resolution':form.cleaned_data['resolution'],
                'author_name':form.cleaned_data['author_name'],
                'author_url':form.cleaned_data['author_url'],
                'license':form.cleaned_data['license'],
                'views':form.cleaned_data['views'],
                'tags':form.cleaned_data['tags'],
            }
            print "media_dict",media_dict
            media = Media(**media_dict)
            print "media obj",media
            media.save()
            
            comment_dict = {
                'user_name':form.cleaned_data['name'],
                'comment':form.cleaned_data['review'],
                'submit_date':datetime.now(),
                'ip_address':request.META['REMOTE_ADDR'],
                'content_type':ContentType.objects.get(app_label="mediacurate",model="media"),
                'object_pk':media.pk,
                'site_id':1 #assuming we're only using one site
            }
            print "comment_dict",comment_dict
            review = Comment(**comment_dict)
            review.save()
            message = "Thanks for adding <a href='%s'>%s</a>. Want to add another?" % (media.get_absolute_url(), media.title)
            #give the user a new form
            form = AddForm()
    return render_to_response('add.html',
                            {'form':form,
                            'message':message},
                            context_instance=RequestContext(request))