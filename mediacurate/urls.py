from django.conf.urls.defaults import *

urlpatterns = patterns('mediacurate.views',
    (r'^$', 'home'),
    (r'^latest/$', 'latest'),
    (r'^popular/$', 'popular'),
    (r'^add/$', 'add'),
    url(r'^view/(?P<id>[\d]+)/$', 'view_by_id',name='view_by_id'),
    url(r'^view/(?P<id>[\d]+)/(?P<slug>[\w-]+)/$', 'view_by_slug', name='view_by_slug'),
    (r'^search/$', 'search'),
    #(r'^assignment/add/', 'assignment_add'),
    
    #autocomplete urls
    (r'^tags/', include('tagging_autocomplete.urls')),
    url(r'^locations/list/$', 'location_autocomplete_list', name="location_autocomplete_list"),
)

urlpatterns += patterns('secretballot.views',
    url(r'^view/vote/(?P<object_id>[\d]+)/(?P<vote>[-\d]+)/$', 'vote', kwargs={'content_type':'mediacurate.media'}),
    url(r'^comment/vote/(?P<object_id>[\d]+)/(?P<vote>[-\d]+)/$', 'vote', kwargs={'content_type':'comments.comment'}),
)