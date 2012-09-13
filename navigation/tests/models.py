

from django.test import TestCase
from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site

from navigation.models import *

class ModelTest(TestCase):
    fixtures = ['simple_menus', 'simple_site']
    

    def test_add_menu(self):
        menu = Menu()
        menu.site_id = 1
        menu.name = 'Sitebar'
        menu.save()
        
        self.assertTrue(menu.pk)
        
    def test_add_item(self):
        
        item = MenuItem()
        item.menu = Menu.objects.get(pk=1)
        item.title = "A"
        item.save()
        
        self.assertEquals(4, Menu.objects.get(pk=1).menuitem_set.count() )

    def test_add_subitem(self):
        menu = Menu.objects.get(name="Top")
        parent = menu.get_item(id=11)
        
        item = MenuItem()
        item.menu = menu
        item.title = "X"
        item.parent = parent
        item.save()
        
        self.assertTrue(item.id)
        
    def test_delete_item(self):
        # pre-test
        menu = Menu.objects.get(name="Top")
        item = menu.get_item(id=13)
        self.assertNotEqual(None, item)
        
        # delete
        item = menu.get_item(id=12)
        item.delete()
        
        # make sure item 13 was deleted
        menu = Menu.objects.get(name="Top")
        self.assertRaises(ObjectDoesNotExist, lambda: menu.get_item(id=13))
        
    def test_flatten(self):
        menu = Menu.objects.get(name="Top")
        initial = len(menu.list_top_items())
        
        menu.flatten()
        final = len(menu.list_top_items())
        self.assertTrue(initial < final)
        
    def test_is_enabled(self):
        menu = Menu.objects.get(name="Top")
        item = menu.get_item(id=12)
        
        item.status = 'enabled'
        self.assertTrue( item.is_enabled() )
        
        item.status = 'auto'
        self.assertTrue( item.is_enabled() )
        
        item.status = 'disabled'
        self.assertFalse( item.is_enabled() )

class SitemapTest(TestCase):
    fixtures = ['flatpages']
    
    def test_refresh_database(self):
        Sitemap.objects.all().delete()
        Sitemap.objects.refresh_current_site()
        self.assertNotEqual(0, len(SitemapItem.objects.all()))
        
        
    def test_menu_from_flatpages(self):
        Sitemap.objects.refresh_current_site()        
        
        menu = Menu.objects.get(pk=1)
        menu.refresh()

        
        top_items = menu.list_top_items()
        self.assertTrue(len(top_items) >= 3)
        self.assertEquals('aaa', top_items[0].title)
        self.assertEquals(2, len(top_items[0].children))
        
    def test_remove_page(self):        
        Sitemap.objects.refresh_current_site()
        sitemap = Sitemap.objects.get(slug='flatpages')
        menu = Menu.objects.get(pk=1)
        menu.refresh()
        
        # make sure the page exists
        self.assertEquals(1, len(sitemap.item_set.filter(url='/aaa/bbb/')) )
        self.assertEquals(1, len(menu.find_items(url='/aaa/bbb/')))
        
        # remove the page
        FlatPage.objects.filter(url='/aaa/bbb/').delete()
        Sitemap.objects.refresh_current_site()
        menu = Menu.objects.get(pk=1)
        
        # make sure the page doesn't exist
        self.assertEquals(0, len(sitemap.item_set.filter(url='/aaa/bbb/')) )
        
        # make sure menu item is disabled
        self.assertEquals(1, len(menu.find_items(url='/aaa/bbb/')))
        self.assertEquals(None, menu.get_item(url='/aaa/bbb/').sitemap_item)
        self.assertEquals(False, menu.get_item(url='/aaa/bbb/').is_enabled())
        
    def test_find_parent_for_url_query(self):        
        Sitemap.objects.refresh_current_site()
        sitemap = Sitemap.objects.get(slug='flatpages')
        
        sitemap_item = sitemap.find_parent_for_url('/aaa/bbb/text.html?query=1#hash')
        self.assertNotEqual(None, sitemap_item)
        self.assertEqual('/aaa/bbb/', sitemap_item.url)
    
    def test_find_parent_for_url_path(self):        
        Sitemap.objects.refresh_current_site()
        sitemap = Sitemap.objects.get(slug='flatpages')
        
        sitemap_item = sitemap.find_parent_for_url('/aaa/bbb/')
        self.assertNotEqual(None, sitemap_item)
        self.assertEqual('/aaa/', sitemap_item.url)

            
    
        
      