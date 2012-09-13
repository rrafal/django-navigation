
from django.utils.translation import pgettext
from django.db import models

import hashlib 


class SitemapInfo(object):
    ''' Represents a collection of pages that can be displayed in navigation.
    
    When pages are temporarly disabled, the sitemap should still return them.
    
    Subclasses may define:
    - item_location - URL for the page; should be uniqueue
    - item_title - Title for the page
    - item_uuid - UUID value unique to this page; must be uniqueue
    - item_enabled - if the page is currently enabled
    - item_parent - URL of the parent page
    - item_order - number use for sorting of pages 
     '''
    
    def __init__(self, slug):
        self.slug = slug
        
    def items(self):
        ''' Items of the sitemap '''
        return []
    
    def item_location(self, item):
        ''' URL for the item '''
        try:
            return item.get_absolute_url()
        except:
            raise NotImplementedError()
        
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
        if isinstance(item, models.Model):
            name = '/model/%s/%s' % (item.__class__.__name__, item.pk)
        else:
            name = '/url/%s' % self.item_location(item)
            
        return hashlib.sha512(name).hexdigest()
     
    def item_enabled(self, item):
        return True       
   
    def item_attr(self, item, name, default=None):
        try:
            attr = getattr(self, 'item_'+name)
        except AttributeError:
            return default
        if callable(attr):
            return attr(item)
        return attr
    
    def __unicode__(self):
        return pgettext('navigation', self.slug)
    
    
class FlatPageSitemapInfo(SitemapInfo):
    ''' SitemapInfo for all pages in "django.contrib.flatpages". '''
    
    def __init__(self, slug, site_id=None):
        super(FlatPageSitemapInfo, self).__init__(slug)
        self.site_id = site_id

    
    def items(self):
        from django.contrib.flatpages.models import FlatPage
        
        if self.site_id:
            return FlatPage.objects.filter(sites__id__exact=self.site_id)
        else:
            return FlatPage.objects.all()
        
    def item_title(self, item):
        return item.title

    
class CMSSitemapInfo(SitemapInfo):
    def items(self):
        from cms.utils.moderator import get_page_queryset
        page_queryset = get_page_queryset(None)
        return page_queryset.all()
    
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
        return item.published and item.in_navigation
    
    
class SiteInfo(object):
    def __init__(self):
        self.sitemaps = {}
        self.__initialized = False

    def register_sitemap(self, sitemap):
        self.sitemaps[ sitemap.slug ] = sitemap
        
    def list_sitemaps(self):
        return self.sitemaps.values()
        
    def get_sitemap(self, name):
        return self.sitemaps[ name ]
    
    def autodiscover(self):
        from django.conf import settings
        
        if 'django.contrib.flatpages' in settings.INSTALLED_APPS:
            sitemap = FlatPageSitemapInfo('flatpages', settings.SITE_ID)
            self.register_sitemap(sitemap)
    
        if 'cms' in settings.INSTALLED_APPS:
            sitemap = CMSSitemapInfo('cms-pages')
            self.register_sitemap(sitemap)
            
        pass
    

site = SiteInfo()
site.autodiscover()


