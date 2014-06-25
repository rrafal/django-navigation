from django.test import TestCase
from navigation.sitemaps import AbstractSitemapInfo
    

    
class RefreshTest(TestCase):
    fixtures = ['flatpages']
    
    def setUp(self):
        from navigation.utils import discover_sitemaps
        discover_sitemaps()

    def test_refresh_menu_from_sitemap__with_flatpages(self):
        from navigation.models import Menu, Sitemap
        from navigation.utils import refresh_menu_from_sitemap
        
        sitemap = Sitemap.objects.get(slug='flatpages')
        menu = Menu.objects.get(sitemap=sitemap)
        
        # refresh
        refresh_menu_from_sitemap(menu, sitemap)

        # check if items were added
        self.assertEquals(6, len(menu.list_all_items()) )
        self.assertEquals(3, len(menu.list_top_items()) )
        
        # check if item was initialized
        birds_item = filter(lambda i: i.sitemap_item_title == 'Birds', menu.list_all_items())[0]
        self.assertEquals('Birds', birds_item.title)
        self.assertEquals('/birds/', birds_item.url)
        self.assertEquals('enabled', birds_item.sitemap_item_status)
        self.assertIsNotNone(birds_item.sitemap_item_id)
        
    def test_refresh_menu_from_sitemap__update_page(self):
        from navigation.models import Menu, MenuItem, Sitemap
        from django.contrib.flatpages.models import FlatPage
        from navigation.utils import refresh_menu_from_sitemap
        
        sitemap = Sitemap.objects.get(slug='flatpages')
        menu = Menu.objects.get(sitemap=sitemap)
        
        # initialize
        refresh_menu_from_sitemap(menu, sitemap)
        
        # modify
        page = FlatPage.objects.get(title="Birds")
        page.title = "Nice Birds"
        page.url = "/nice-birds/"
        page.save()
        
        # refresh
        refresh_menu_from_sitemap(menu, sitemap)
        
        # check
        self.assertEquals(0, MenuItem.objects.filter(title='Birds').count())
        self.assertEquals(1, MenuItem.objects.filter(title='Nice Birds').count())
        self.assertEquals(0, MenuItem.objects.filter(url='/birds/').count())
        self.assertEquals(1, MenuItem.objects.filter(url='/nice-birds/').count())
    
    def test_refresh_menu_from_sitemap__update_page_parent(self):        
        from navigation.models import Menu, MenuItem, Sitemap
        from navigation.utils import refresh_menu_from_sitemap
        from mock import MagicMock

        sitemap = Sitemap.objects.get(slug='flatpages')
        menu = Menu.objects.get(sitemap=sitemap)
        
        # initialize
        items = [
            {'uuid' : 'home', 'title': 'Home', 'location':'/', 'parent': None},
            {'uuid' : 'child', 'title': 'Child', 'location':'/child/', 'parent': '/'},
            ]
        sitemap.get_items = MagicMock(return_value=items)
        refresh_menu_from_sitemap(menu, sitemap)
        
        # check
        menu_item = MenuItem.objects.filter(title='Child').get()
        self.assertNotEquals(None, menu_item.parent)
        
        # modify
        items[1]['parent'] = None
        sitemap.get_items = MagicMock(return_value=items)
        
        # refresh
        refresh_menu_from_sitemap(menu, sitemap)
        
        # check
        menu_item = MenuItem.objects.filter(title='Child').get()
        self.assertEquals(None, menu_item.parent)
        
    
    def test_refresh_menu_from_sitemap__empty_menu(self):        
        from navigation.models import Menu, MenuItem, Sitemap
        from navigation.utils import refresh_menu_from_sitemap
        from mock import MagicMock

        sitemap = Sitemap.objects.get(slug='flatpages')
        menu = Menu.objects.get(sitemap=sitemap)
        
        # initialize
        items = [
            {'uuid' : 'home', 'title': 'Home', 'location':'/', 'parent': None},
            {'uuid' : 'child', 'title': 'Child', 'location':'/child/', 'parent': '/'},
            ]
        sitemap.get_items = MagicMock(return_value=items)
        refresh_menu_from_sitemap(menu, sitemap)
        
        # modify
        items[1]['parent'] = None
        sitemap.get_items = MagicMock(return_value=[])
        
        # refresh
        refresh_menu_from_sitemap(menu, sitemap)
        
        # check
        self.assertEquals(0, MenuItem.objects.filter(title='Child').count())
