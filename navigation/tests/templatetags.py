

from django.conf import settings
from django.db import connection
from django.http import HttpRequest
from django.test import TestCase
from django.template import TemplateDoesNotExist
from django.template import Context as TemplateContext
from django.template import RequestContext


from navigation.models import Menu, MenuItem, SitemapManager
from navigation.templatetags.navigation_tags import *



class MenuTagTest(TestCase):
    fixtures = ['simple_menus', 'simple_site']

    def test_show_menu(self):
        context = TemplateContext({})
        show_navigation_menu(context, 'Top')
    
    def test_show_menu_missing(self):
        context = TemplateContext({})
        menu = show_navigation_menu(context, 'Missing')
        self.assertNotEqual('', menu)
        self.assertTrue('navigation-menu-missing' in menu)
        
    def test_show_menu_template(self):
        context = TemplateContext({})
        show_navigation_menu(context, 'Top', template='navigation/flat-menu.html')
        
    def test_show_menu_missing_template(self):
        def test():
            context = TemplateContext({})
            show_navigation_menu(context, 'Top', template='navigation/missing.html')
        self.assertRaises(TemplateDoesNotExist, test)

    def test_show_menu_root(self):
        context = TemplateContext({})
        show_navigation_menu(context, 'Top', root='second')
    
    def test_show_menu_missing_root(self):
        context = TemplateContext({})
        show_navigation_menu(context, 'Top', root='missing')
    
        
    def test_get_menu(self):
        info = get_navigation_menu('Top')
        self.assertEquals(2, len(info['items']))
        self.assertEquals(None, info['parent'])
        self.assertEquals('Top', info['menu'].name)
        
    def test_get_menu_with_disabled_items(self):
        for item in MenuItem.objects.all():
            item.status = "disabled"
            item.save()
        
        info = get_navigation_menu('Top')
        self.assertEquals(0, len(info['items']))

    def test_get_menu_root(self):
        info = get_navigation_menu( 'Top', root='/second/a.html')
        
        self.assertEqual(0, len(info['items']))
        self.assertNotEqual(None, info['parent'])
        self.assertEqual('Top', info['menu'].name)
        
    def test_get_current_items(self):
        info = get_current_items('Top', '/second')
        self.assertEqual('Second', info['current_item'].title)
        self.assertEqual(None, info['current_parent_item'])
        
    def test_get_current_items_ancestors(self):
        info = get_current_items('Top', '/second/a.html')
        
        self.assertEqual('Second A', info['current_item'].title)
        self.assertNotEqual(None, info['current_parent_item'])
        self.assertEqual('Second', info['current_parent_item'].title)
        self.assertEqual(1, len(info['current_ancestor_items']))
    
class BreadcrumbsTagTest(TestCase):
    fixtures = ['simple_menus', 'simple_site']
    

    def test_show(self):
        request = HttpRequest()
        request.path = 'second/a.html'
        
        context = TemplateContext({'request': request})
        
        
        menu = show_navigation_breadcrumbs(context, menu='Top')
        self.assertNotEqual('', menu)
        
    def test_show_missing(self):
        request = HttpRequest()
        request.path = 'second/a.html'
        
        context = TemplateContext({'request': request})
        
        menu = show_navigation_breadcrumbs(context, menu='Not Configured')
        self.assertNotEqual('', menu)
        self.assertTrue('navigation-breadcrumbs-missing' in menu)
        
    def test_get_breadcrumbs_from_menu(self):
        request_path = '/second/a.html'
        
        crumbs = get_navigation_breadcrumbs(request_path, menu='Top')
        self.assertTrue(crumbs)
        self.assertEqual('Home', crumbs[0].title)
        self.assertEqual(3, len(crumbs))
        
    def test_get_breadcrumbs_from_sitemap(self):
        manager = SitemapManager(1)
        manager.refresh_current_site()
        
        request_path = '/about_us'
        
        crumbs = get_navigation_breadcrumbs(request_path, sitemap='flatpages')
        self.assertTrue(crumbs)
        self.assertEqual('Home', crumbs[0].title)
        self.assertEqual(2, len(crumbs))
   
           
