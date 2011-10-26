from django import forms
from form_utils.forms import BetterForm
from tagging_autocomplete.widgets import TagAutocomplete
from mediacurate.widgets import LocationAutocomplete
from mediacurate.models import Media

class AddForm(BetterForm):
    '''Used on the add page. Includes first review.'''
    url = forms.URLField()
    title = forms.CharField()
    location = forms.CharField(widget=LocationAutocomplete)
    author_name = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}))
    #author_url = forms.CharField(widget=forms.widgets.HiddenInput())
    author_url = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}))
    
    name = forms.CharField(required=True)
    review = forms.CharField(widget=forms.widgets.Textarea(),required=True)
    tags = forms.CharField(widget=TagAutocomplete,required=False)
    
    date_uploaded = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    resolution = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    views = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    license = forms.CharField(widget=forms.widgets.TextInput(attrs={'readonly':True}),required=False)
    class Meta:
        fieldsets = (
            ('URL',{'fields':('url',),
                    'description':'Paste the URL to preview',
                    'classes':['']}
            ),
            ('Info',{'fields':('title','location','author_name','author_url'),
                    'description':"These fields are required",
                    'classes':['']}
            ),
            ('More',{'fields':('name','review','tags',),
                    'description':"Enter your review. This helps us categorize the content.",
                    'classes':['review']}
            ),
            ('Hidden',{'fields':('resolution','views','license','date_uploaded'),
                    'description':"These fields are hidden",
                    'classes':['hidden']}
            ),
        )