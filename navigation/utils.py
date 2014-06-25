
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db import models
from django.utils.importlib import import_module
from django.utils.translation import pgettext
 

def discover_sitemaps():
    from django.contrib.sites.models import Site
    from navigation.models import Sitemap
    
    for info in get_sitemap_info_list():
        if Sitemap.current_objects.filter(slug=info.slug).count() == 0:
            sitemap = Sitemap()
            sitemap.site = Site.objects.get_current()
            sitemap.slug = info.slug
            sitemap.save()
    
def initialize_autorefresh():	
    def refresh(info):
        from navigation.models import Sitemap, Menu
        from django.contrib.sites.models import Site
        
        discover_sitemaps()
        for sitemap in Sitemap.current_objects.filter(slug=info.slug):
            for menu in Menu.current_objects.all():
                refresh_menu_from_sitemap(menu, sitemap)

    for info in get_sitemap_info_list():
        info.add_listener(refresh)

def _get_sitemap_classes():
    try:
        settings_list = settings.NAVIGATION_SITEMAPS
    except AttributeError:
        raise ImproperlyConfigured('Add NAVIGATION_SITEMAPS to your settings.py file.')
    
    
    info_list = []
    for full_name in settings_list:
        module_name, class_name = full_name.rsplit('.', 1)
        
        try:
            module = import_module(module_name)
            cls = getattr(module, class_name)
        except (ImportError, AttributeError):
            raise ImproperlyConfigured('Failed to load sitemap info: %s' % full_name)
            
        yield cls

def get_sitemap_info_with_slug(slug):
    candidate_classes = []
    
    for cls in _get_sitemap_classes():
        if cls.slug == slug:
            candidate_classes.append(cls)
            
    if len(candidate_classes) == 0:
        return None
    if len(candidate_classes) == 1:
        return candidate_classes[0]( settings.SITE_ID )
    if len(candidate_classes) > 1:
        raise Exception("Multiple sitemaps are registered with the same slug: " + slug)
    assert(False)
    
def get_sitemap_info_list():
    ''' Returns a list of SitemapInfo objects.
    
    NAVIGATION_SITEMAPS should be included in settings.py
    This should be a list of classes that implements SitemapInfo. 
    Those objects are loaded and returned.
    '''
    info_list = []
    for cls in _get_sitemap_classes():
        info_list.append( cls( settings.SITE_ID ) )
    return info_list
    
def refresh_all_menus():
    from .models import Menu, Sitemap
    
    for sitemap in Sitemap.current_objects.all():
        if sitemap.is_available():
            for menu in Menu.current_objects.all():
                if menu.sitemap == None or menu.sitemap == sitemap:
                    refresh_menu_from_sitemap(menu, sitemap)
    return
    
def refresh_menu_from_sitemap(menu, sitemap):
    ''' Refreshes menu items based on changes in sitemap. '''
    if menu.sitemap == sitemap:
        _refresh_menu_from_sitemap_full(menu, sitemap)
    else:
        _refresh_menu_from_sitemap_items(menu, sitemap)
    
def _refresh_menu_from_sitemap_items(menu, sitemap):
    ''' Refreshes items that belong to give sitemap '''
    
    def get_menu_items_for_sitemap_item(sitemap_item):
        return menu.menuitem_set.filter(sitemap=sitemap, sitemap_item_id=sitemap_item['uuid'])
    
    for sitemap_item in sitemap.get_items():
        for menu_item in get_menu_items_for_sitemap_item(sitemap_item):
            menu_item.sitemap_item_status = sitemap_item.get('status', 'active')
            
            if not menu_item.title or menu_item.sitemap_item_title == menu_item.title:
                menu_item.title = sitemap_item.get('title', '')
            
            menu_item.sitemap_item_title = sitemap_item.get('title', '')
            
            if 'location' in sitemap_item:
                menu_item.url = sitemap_item['location']
            
            menu_item.save()
    
def _refresh_menu_from_sitemap_full(menu, sitemap):
    ''' Refreshes entire menu based on a sitemap. '''
    from .models import MenuItem
    assert(menu.sitemap == sitemap)
    
    sitemap_items = list(sitemap.get_items())
    
    # check if menu should be empty
    if not sitemap_items:
        menu.menuitem_set.clear()
        return
    
    sitemap_has_tree = 'parent' in sitemap_items[0]
    sitemap_has_order = 'order' in sitemap_items[0]
    
            
    def find_parent_by_url(menu_item):
        ''' Finds parent menu item '''
        parent_url = get_parent_url(menu_item.url)

        while parent_url:
            try:
                canditate_url = parent_url
                if canditate_url != menu_item.url:
                    return menu.menuitem_set.filter(url=canditate_url).get()
            except ObjectDoesNotExist:
                pass

            try:
                canditate_url = parent_url + "/"
                if canditate_url != menu_item.url:
                    return menu.menuitem_set.filter(url=canditate_url).get()
            except ObjectDoesNotExist:
                pass

            parent_url = get_parent_url(parent_url)
        return None
    
    # flatten menu
    for menu_item in menu.menuitem_set.all():
        menu_item.parent = None
        menu_item.save()
    
    # create new items and update existing items
    current_menu_items = set()
    for s in sitemap_items:
        try:
            menu_item = menu.menuitem_set.filter(sitemap_item_id=s['uuid']).get()
        except ObjectDoesNotExist:
            menu_item = MenuItem()
            menu_item.menu = menu
            menu_item.status = 'auto'
            menu_item.sitemap_item_id = s['uuid']
        
        if not menu_item.title or menu_item.sitemap_item_title == menu_item.title:
            menu_item.title = s.get('title', '')
                
        menu_item.sitemap_item_title = s.get('title', '')
        menu_item.sitemap_item_status = s.get('status', 'active')
        menu_item.url = s.get('location', '')
        menu_item.order = s.get('order', 1)  
        menu_item.save()
        
        current_menu_items.add(menu_item)
    
    # remove old items
    for menu_item in menu.menuitem_set.all():
        if menu_item not in current_menu_items:
            menu_item.delete()
    
    # create hierarchy
    if sitemap_has_tree:
        for s in (s for s in sitemap_items if s['parent']):
            try:
                menu_item = menu.menuitem_set.filter(sitemap_item_id=s['uuid']).get()
                parent_item = menu.menuitem_set.filter(url=s['parent']).get()

                menu_item.parent = parent_item
                menu_item.save()
            except ObjectDoesNotExist:
                pass
    else:            
        for menu_item in menu.menuitem_set.all():
            menu_item.parent = find_parent_by_url(menu_item)
            menu_item.save()
            
    # create order
    if sitemap_has_order:
        for s in sitemap_items:        
            try:
                menu_item = menu.menuitem_set.filter(sitemap_item_id=s['uuid']).get()
                menu_item.order = s['order']
                menu_item.save()
            except ObjectDoesNotExist:
                pass
    else:
        for index, menu_item in enumerate(menu.menuitem_set.order_by('title')):
            menu_item.order = index
            menu_item.save()
            
    menu.clean_item_order()
    
def get_parent_url(url):
    from urlparse import urlsplit, urldefrag, urljoin
    from os.path import dirname

    url_parts = urlsplit(url)

    # try removing fragment
    if url_parts.fragment != '':
        parent_url = urldefrag(url)[0]

        if parent_url != url:
            return parent_url

    # try removing query
    if url_parts.query != '':
        parent_url = urljoin(url, url_parts.path)

        if parent_url != url:
            return parent_url

    # make the path shorter
    if url_parts.path != '' and url_parts.path != '/':
        path = dirname(url_parts.path)
 
        parent_url = urljoin(url, path)

        if parent_url != url:          
            return parent_url
    return None
    
