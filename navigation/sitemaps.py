
class AbstractSitemapInfo(object):
    ''' Represents a collection of pages that can be displayed in navigation.
    
    When pages are temporarly disabled, the sitemap should still return them.
    
    Subclass must define "slug" attribute. Only one sitemap can be registered with give slug.
    
    Subclasses may define:
    - item_location - URL for the page; should be uniqueue
    - item_title - Title for the page
    - item_uuid - UUID value unique to this page; must be uniqueue
    - item_enabled - if the page is currently enabled
    - item_parent - URL of the parent page
    - item_order - number use for sorting of pages 
     '''
    
    def __init__(self, site_id):
        self.site_id = site_id
        
    def items(self):
        ''' Items of the sitemap '''
        return []
    
    def item_location(self, item):
        ''' URL for the item '''
        try:
            return item.get_absolute_url()
        except AttributeError:
            raise NotImplementedError("Cannot get location.")
        
    def item_title(self, item):
        ''' Title for the item'''
        return unicode(item)
    
    def item_uuid(self, item):
        ''' ID for the item. 
        Must be unique within the sitemap. Should be based on ID of underlying object.
        It can be a hexadecimal hash value, ex: SHA-512, MD.
        see:
        - hashlib.sha224
        
        If it is a string, it must be not longer than 255 characters.'''
        
        import hashlib
        from django.db import models
        
        if isinstance(item, models.Model):
            name = '/model/%s/%s' % (item.__class__.__name__, item.pk)
        else:
            name = '/url/%s' % self.item_location(item)
        
        return hashlib.sha512(name).hexdigest()
     
    def item_enabled(self, item):
        return True       
    
    def add_listener(self, callback):
        ''' Funcation callack should be called when sitemap changes. '''
        pass
    
    def __unicode__(self):
        return pgettext('navigation', self.slug)
    
    
class FlatPageSitemapInfo(AbstractSitemapInfo):
    ''' Sitemap for all pages in "django.contrib.flatpages". '''
    
    slug = 'flatpages'
    
    def items(self):
        from django.contrib.flatpages.models import FlatPage
        
        if self.site_id:
            return FlatPage.objects.filter(sites__id__exact=self.site_id)
        else:
            return FlatPage.objects.all()
        
    def item_title(self, item):
        return item.title

    
class CMSSitemapInfo(AbstractSitemapInfo):
    ''' Sitemap for Django CMS pages. '''
    
    slug = 'cms-pages'
    
    def items(self):
        from cms.models import Page
        return Page.objects.public()
    
    def item_parent(self, item):
        if item.parent:
            return self.item_location( item.parent )
        else:
            return None
    
    def item_order(self, item):
        if item.parent:
            return item.lft
        else:
            return item.tree_id
        
    def item_enabled(self, item):
        return item.is_published(None) and item.in_navigation
    
    def add_listener(self, callback):
        ''' Funcation callack should be called when sitemap changes. '''
        import cms.signals as cms_signals
        def receiver(sender, **kwargs):
            callback(self)
        cms_signals.post_publish.connect(receiver, weak=False)

