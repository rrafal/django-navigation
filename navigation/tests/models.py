

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
    
            
    
        
      