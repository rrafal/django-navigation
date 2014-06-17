
from django.core.exceptions import  ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext as _

from navigation.managers import *



class Sitemap(models.Model):
    ''' Database representation of sitemap '''
    site = models.ForeignKey('sites.site')
    slug = models.CharField(_('Slug'), max_length=255)
    
    current_objects = SitemapManager('current')
    objects = SitemapManager()
    
    def refresh(self):
        source_sitemap = self._get_source()
        source_has_tree = hasattr(source_sitemap, 'item_parent')
        source_has_order = hasattr(source_sitemap, 'item_order')
        
        # create and remove items
        items_to_delete = set(self.item_set.all())
        
        for s in source_sitemap.items():
            s_uuid = source_sitemap.item_uuid(s)
            s_title = source_sitemap.item_title(s)
            s_url = source_sitemap.item_location(s)
            
            try:
                sitemap_item = self.item_set.filter(uuid=s_uuid).get()
                items_to_delete.remove(sitemap_item)
            except ObjectDoesNotExist:
                sitemap_item = SitemapItem()
                sitemap_item.sitemap = self
                sitemap_item.uuid = s_uuid
                sitemap_item.title = s_title
                sitemap_item.url = s_url
                sitemap_item.save()
                
        for item in items_to_delete:
            # make sure children are not deleted
            for child in item.children.all():
                child.parent = None
                child.save()
            
            # disconnect menu items
            for menu_item in item.menuitem_set.all():
                menu_item.status = 'disabled'
                menu_item.sitemap_item = None
                menu_item.sitemap_item_status = None
                menu_item.save()
            
            # delete self
            item.delete()
        
        # update all items
        for s in source_sitemap.items():
            s_uuid = source_sitemap.item_uuid(s)
            s_title = source_sitemap.item_title(s)
            s_url = source_sitemap.item_location(s)
            s_enabled = source_sitemap.item_enabled(s)
            s_order = source_sitemap.item_attr(s, 'order', 0)
            s_parent = source_sitemap.item_attr(s, 'parent', None)
            
            # update sitemap item
            try:
                sitemap_item = self.item_set.filter(uuid=s_uuid).get()
            except ObjectDoesNotExist:
                return  # some new unexpected object
            
            sitemap_item.title = s_title
            sitemap_item.url = s_url
            sitemap_item.uuid = s_uuid
            sitemap_item.order = s_order
            
            if s_enabled:
                sitemap_item.status = 'enabled'
            else:
                sitemap_item.status = 'disabled'
            
            if s_parent == None:
                sitemap_item.parent = None
            else:
                candidates = self.item_set.filter(url=s_parent)
                if len(candidates) > 0:
                    sitemap_item.parent = candidates[0]                    
                else:
                    sitemap_item.parent = None
            
            sitemap_item.save()
        
        if not source_has_tree:
            self.calculate_parents_from_url()
        
        if not source_has_order:
            self.calculate_order_from_title()
    
    def calculate_parents_from_url(self):
        for item in self.item_set.all():
            item.parent = self.find_parent_for_url(item.url)
            item.save()
            
    def calculate_order_from_title(self):
        count = self.item_set.count()
        for index, item in zip(range(count), self.item_set.order_by('title')):
            item.order = index + 1     
            item.save()   
            
    def find_parent_for_url(self, url):
        from urlparse import urlsplit, urldefrag, urljoin
        from os.path import dirname
        
        url_parts = urlsplit(url)
        parent_url = url
        
        # try removing fragment
        if url_parts.fragment != '':
            parent_url = urldefrag(url)[0]
            
            if parent_url != url:
                try:
                    return self.item_set.get(url=parent_url)
                except ObjectDoesNotExist:
                    pass
        
        # try removing query
        if url_parts.query != '':
            parent_url = urljoin(parent_url, url_parts.path)
            
            if parent_url != url:
                try:
                    return self.item_set.get(url=parent_url)
                except ObjectDoesNotExist:
                    pass
        
 
        
        # make the path shorter
        path = url_parts.path
        while path != '' and path != '/':
            path = dirname(path)
            
            # try with "/" at the end  
            parent_url = urljoin(parent_url, path) + "/"

            if parent_url != url:          
                try:
                    return self.item_set.get(url=parent_url)
                except ObjectDoesNotExist:
                    pass
            
            # try without "/" at the end
            parent_url = urljoin(parent_url, path)
            
            if parent_url != url:   
                try:
                    return self.item_set.get(url=parent_url)
                except ObjectDoesNotExist:
                    pass
        
                
        return None
    
    def _get_source(self):
        from .utils import get_sitemap_info_list
        
        for info in get_sitemap_info_list():
            if info.slug == self.slug:
                return info
        raise ObjectDoesNotExist("Sitemap Info not found.")    
    
    def __unicode__(self):
        return _(self.slug)



class SitemapItem(models.Model):
    sitemap = models.ForeignKey(Sitemap, related_name='item_set')
    parent = models.ForeignKey('self', verbose_name=_('Parent'), related_name='children', on_delete=models.SET_NULL, null=True, blank=True)
    
    uuid = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    order = models.IntegerField(default=1)
    status = models.CharField(max_length=16, default='enabled')
    
    def save(self, *args, **kwargs):
        # update menu-item status values
        for menu_item in self.menuitem_set.all():
            menu_item.sitemap_item_status = self.status
            menu_item.save()
            
        # Call the "real" save() method.
        super(SitemapItem, self).save(*args, **kwargs) 

    def get_absolute_url(self):
        return self.url
    
    def __unicode__(self):
        return self.title



class Menu(models.Model):
    ''' A custom menu controlled by administrator.
    
    All menu items are pre-loaded at the same time. If they change,
    you need to reload the menu to see the change.
    '''
    site = models.ForeignKey('sites.site')
    sitemap = models.ForeignKey(Sitemap,
        verbose_name=_('Sitemap'),
        help_text="Select source sitemap to automatically configure menu items",
        related_name='menu_set', null=True, blank=True)
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
        if 'sitemap_item' in kwargs:
            return [i for i in self.all_items if i.sitemap_item_id == kwargs['sitemap_item'].id]
    
    def get_item(self, **kwargs):
        ''' Returns specific item '''
        try:
            return self.find_items(**kwargs)[0]
        except IndexError:
            raise ObjectDoesNotExist()
        
    def refresh(self):
        # make sure we are starting with correct items
        self.all_items = None
        self._load_items()
        
        if self.sitemap:
            self._refresh_tree()
            self.all_items = None
            self.refresh_order()
            self.all_items = None
        else:
            self._refresh_items()
            self.all_items = None
            self.all_items = None
        
        self._load_items()
    
    def _refresh_items(self):
        for menu_item in self.all_items:
            menu_item.refresh()
    
    def _refresh_tree(self):
        if not self.sitemap:
            return
        
        # flatten first before removing items
        for menu_item in self.all_items:
            menu_item.parent = None
        
        # add missing items and update existing info
        for sitemap_item in self.sitemap.item_set.all():

            try:
                menu_item = self.get_item(sitemap_item=sitemap_item)
                menu_item.refresh()
                
            except ObjectDoesNotExist:
                menu_item = MenuItem()
                menu_item.menu = self
                menu_item.title = sitemap_item.title
                menu_item.sync_title = True
                menu_item.url = sitemap_item.url
                menu_item.order = sitemap_item.order
                menu_item.sitemap_item = sitemap_item
                menu_item.sitemap_item_status = sitemap_item.status
                menu_item.save()
                
        # remove old items
        for menu_item in self.all_items:
            if menu_item.sitemap_item_id == None:
                menu_item.delete()
        
                
        # reload from database after adding and deleting items
        self.all_items = None
        self._load_items()
        
        
        # create hierarchy
        for sitemap_item in self.sitemap.item_set.all():
            menu_item = self.get_item(sitemap_item=sitemap_item)
            
            if sitemap_item.parent:
                menu_item.parent = self.get_item(sitemap_item=sitemap_item.parent)
            else:
                menu_item.parent = None
            menu_item.save()
                
        # make sure everything is ok
        self.all_items = None
                
    def refresh_order(self):
        ''' Refreshes sorting index so that "pre-order" traversal is astablished '''
        
        def visit(item):
            if item.order != visit.index:
                item.order = visit.index
                item.save()
            visit.index += 1
            
            for c in item.children:
                visit(c)
        visit.index = 1
        
        for item in self.list_top_items():
            visit(item)
        
        self.all_items = None
        
    def flatten(self):
        for item in self.all_items:
            item.parent = None
            item.save()

    def _load_items(self):
        if self.all_items == None:
            self.all_items = []
            
            for i in self.menuitem_set.order_by('order').all():
                i.menu = self
                self.all_items.append(i)
    
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

    my_parent = models.ForeignKey('self', db_column='parent_id', verbose_name=_('Parent'), null=True, blank=True)
    
    menu = models.ForeignKey(Menu)
    title = models.CharField(max_length=255)
    sync_title = models.BooleanField(editable=False, default=True)
    url = models.CharField(max_length=255)
    order = models.IntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='auto')
    
    # id to the underlying object, as returned by sitemap
    sitemap_item = models.ForeignKey(SitemapItem, verbose_name=_('Page'), null=True, blank=True)
    sitemap_item_status = models.CharField(max_length=16, verbose_name=_('Page Status'), choices=STATUS_CHOICES, null=True, editable=False)
    
    class Meta:
        ordering = ['order']
    
    def refresh(self):
        if not self.sitemap_item:
            return
        
        self.url = self.sitemap_item.url
        self.order = self.sitemap_item.order
        self.sitemap_item_status = self.sitemap_item.status
        
        if self.sync_title:
            self.title = self.sitemap_item.title
        elif self.title == self.sitemap_item.title:
            self.sync_title = True
        
        self.save()
        
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
            return self.menu.get_item(id=self.my_parent.id)
            
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
