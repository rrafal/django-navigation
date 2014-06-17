
from django.test import TestCase
from django.test.client import Client

from navigation.admin import MenuAdmin
from navigation.models import Menu, Sitemap, SitemapItem

    

class MenuAdminTest(TestCase):
    fixtures = ['flatpages']
    


    def test_refresh_items(self):
        from navigation.admin import refresh_items
        queryset = Menu.objects.filter(id=1)
        refresh_items(None, None, queryset)
    
    def test_find_sitemap_items_by_term(self):
        Sitemap.objects.refresh_current_site()
        
        client = self._get_admin_client()
        response = client.get('/admin/navigation/menu/find-sitemap-items/', {'term': 'aaa bbb'})
        self.assertContains(response, '/aaa/bbb/')
        self.assertNotContains(response, 'ccc')
        
        response = client.get('/admin/navigation/menu/find-sitemap-items/', {'term': 'ccc'})
        self.assertContains(response, 'ccc')
    
    def test_find_sitemap_items_by_url(self):
        Sitemap.objects.refresh_current_site()
        
        client = self._get_admin_client()
        response = client.get('/admin/navigation/menu/find-sitemap-items/', {'url': '/aaa/bbb/'})
        self.assertContains(response, '/aaa/bbb/')
        self.assertNotContains(response, '/ccc/')
        
        response = client.get('/admin/navigation/menu/find-sitemap-items/', {'term': '/ccc/'})
        self.assertContains(response, '/ccc/')
        self.assertNotContains(response, '/aaa/bbb/')

            
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
    