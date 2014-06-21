
from django.test import TestCase
from django.test.client import Client

from navigation.admin import MenuAdmin
from navigation.models import Menu, Sitemap

    

class MenuAdminTest(TestCase):
    fixtures = ['flatpages']
    
    def setUp(self):
        from navigation.utils import discover_sitemaps
        discover_sitemaps()

    def test_refresh_items(self):
        from navigation.admin import refresh_items
        queryset = Menu.objects.filter(id=1)
        refresh_items(None, None, queryset)
    
    def test_find_sitemap_items_by_term(self):
        client = self._get_admin_client()
        response = client.get('/admin/navigation/menu/find-sitemap-items/', {'term': 'Goldfish'})
        self.assertContains(response, '/fishes/goldfish/')
        self.assertNotContains(response, '/bubble/')
        
        response = client.get('/admin/navigation/menu/find-sitemap-items/', {'term': 'Bubble'})
        self.assertContains(response, '/bubble/')
    
    def test_find_sitemap_items_by_url(self):
        client = self._get_admin_client()
        response = client.get('/admin/navigation/menu/find-sitemap-items/', {'url': '/fishes/betta/'})
        self.assertContains(response, '/fishes/betta/')
        self.assertNotContains(response, '/fishes/goldfish/')
        
        response = client.get('/admin/navigation/menu/find-sitemap-items/', {'url': '/fishes/goldfish/'})
        self.assertContains(response, '/fishes/goldfish/')
        self.assertNotContains(response, '/fishes/betta/')

            
    def _get_admin_client(self):
        from django.contrib.auth.models import User
        
        if User.objects.filter(username='admin').count() == 0:
            user = User.objects.create_user(username='admin', email='admin@example.com', password='admin')
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
        
        client = Client()
        client.login(username='admin', password='admin')
        return client
    