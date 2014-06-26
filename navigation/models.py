
from django.core.exceptions import  ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext as _

from navigation.managers import MenuManager, SitemapManager

class Sitemap(models.Model):
    ''' Database representation of sitemap '''
    site = models.ForeignKey('sites.site', editable=False)
    slug = models.CharField(_('Slug'), max_length=255, editable=False)
    
    current_objects = SitemapManager('current')
    objects = SitemapManager()
    
    def _get_info(self):
        from .utils import get_sitemap_info_with_slug
        
        if not hasattr(self, '_info'):
            self._info = get_sitemap_info_with_slug(self.slug)
            
        if self._info is None:
            raise Exception("Sitemap is not available.")
        return self._info
    
    def get_items(self):
        info = self._get_info()
        
        for item in info.items():
            # get info about each item
            data = {}
            for attr_name in dir(info):
                if attr_name.startswith('item_'):
                    key = attr_name[5:]
                    data[ key ] = getattr(info, attr_name)(item)
            # return it
            yield data
            
    def has_item_parent(self):
        info = self._get_info()
        return hasattr(info, 'item_parent')
        
    def has_item_order(self):
        info = self._get_info()
        return hasattr(info, 'item_order')
    
    def is_available(self):
        ''' Checks if the sitemap is available/active. '''
        
        from .utils import get_sitemap_info_with_slug
        
        try:
            info = get_sitemap_info_with_slug(self.slug)
            if info:
                return True
            else:
                return False
        except:
            return False
        
    def __unicode__(self):
        return self.slug

class Menu(models.Model):
    ''' A custom menu controlled by administrator.
    
    All menu items are pre-loaded at the same time. If they change,
    you need to reload the menu to see the change.
    '''
    
    site = models.ForeignKey('sites.site')
    sitemap = models.ForeignKey(Sitemap, null=True, blank=True, related_name='menus')
    name = models.CharField(_('Name'), max_length=255)
    all_items = None
    
    current_objects = MenuManager('current')
    objects = MenuManager()
    
    class Meta:
        ordering = ['name']
    
    def list_all_items(self):
        self._load_items()
        return self.all_items
        
    def list_top_items(self):
        ''' Return all top-level items '''
        self._load_items()
        return [i for i in self.all_items if i.my_parent_id == None]
        
    def find_items(self, **kwargs):
        ''' Searches for items '''
        self._load_items()
        
        if 'id' in kwargs:
            return [i for i in self.all_items if i.id == kwargs['id']]
        if 'pk' in kwargs:
            return [i for i in self.all_items if i.pk == kwargs['pk']]
        if 'url' in kwargs:
            return [i for i in self.all_items if i.url == kwargs['url']]
        if 'parent' in kwargs:
            if kwargs['parent'] == None:
                return [i for i in self.all_items if i.my_parent_id == None]
            else:
                return [i for i in self.all_items if i.my_parent_id == kwargs['parent'].id]
    
    def get_item(self, **kwargs):
        ''' Returns specific item '''
        try:
            return self.find_items(**kwargs)[0]
        except IndexError:
            raise ObjectDoesNotExist()
    
    def _load_items(self):
        if self.all_items == None:
            self.all_items = []
            
            for i in self.menuitem_set.order_by('order').all():
                i.menu = self
                self.all_items.append(i)
    
    def clean_item_order(self):
        self.all_items = None
        
        # sort items in depth-first order
        def get_sorted_descendents(all_items, parent):
            for item in all_items:
                if item.my_parent_id == parent.id:
                    yield item
                    for descendent in get_sorted_descendents(all_items, item):
                        yield descendent
            pass
        def get_sorted(all_items):
            all_items = list(all_items)
            for item in all_items:
                if item.my_parent_id == None:
                    yield item
                    for descendent in get_sorted_descendents(all_items, item):
                        yield descendent
            pass

        all_items = self.menuitem_set.order_by('order').all()
        for index, item in enumerate(get_sorted(all_items)):
            item.order = index
            item.save()
        
    
    def save(self, *args, **kwargs):
        # Call the "real" save() method.
        super(Menu, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return self.name


class MenuItem(models.Model):
    ''' A menu item of a custom navigation menu '''
    
    STATUS_CHOICES = (
        ('auto', 'Auto'),
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
        )

    my_parent = models.ForeignKey('self', db_column='parent_id', verbose_name=_('Parent'), related_name='+', null=True, blank=True)
    
    menu = models.ForeignKey(Menu)
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    order = models.IntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='auto')
    
    # id to the underlying object, as returned by sitemap
    sitemap = models.ForeignKey(Sitemap, null=True, editable=False)
    sitemap_item_id = models.CharField(max_length=255, null=True, editable=False)
    sitemap_item_title = models.CharField(max_length=255, null=True, editable=False)
    sitemap_item_status = models.CharField(max_length=16, verbose_name=_('Page Status'), choices=STATUS_CHOICES, null=True, editable=False)
    
    class Meta:
        ordering = ['order']
                
    def is_enabled(self):
        if self.status == 'enabled':
            return True
        elif self.status == 'auto':
            if self.sitemap_item_status == None:
                return True
            elif self.sitemap_item_status == 'enabled':
                return True
            else:
                return False
        else:
            return False
    
    def list_children(self):
        return self.menu.find_items(parent=self)
    
    def list_active_children(self):
        return [c for c in self.list_children() if c.is_enabled()]
    
    def get_parent(self):
        if self.my_parent == None:
            return None
        else:
            return self.menu.get_item(id=self.my_parent_id)
            
    def set_parent(self, new_parent):
        self.my_parent = new_parent
        
        # make sure parent wasn't change to something illegal
        #if not self.__is_parent_valid():
        #    self.parent = None
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return self.url
        
    def __is_parent_valid(self):
        #  make sure there is a root
        visited = set([self])
        current = self.parent
        while current:
            if current in visited:
                return False
            visited.add(current)
            current = current.my_parent
        return True
        
    children = property(list_children)
    active_children = property(list_active_children)
    parent = property(get_parent, set_parent)
