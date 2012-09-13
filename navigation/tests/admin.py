
from django.test import TestCase
from django.test.client import RequestFactory

from navigation.admin import MenuAdmin
from navigation.models import Menu



class MenuAdminTest(TestCase):
    fixtures = ['simple_menus', 'simple_site']
    
    def setUp(self):
        self.factory = RequestFactory()

    def test_delete_item(self):
        request = self.factory.post('/admin/navigation/menu/1/delete_item', {'id': 11})
        
        admin = MenuAdmin(Menu, None)
        response = admin.delete_item_view(request, 1)
        self.assertNotEqual(None, response)
        
    def test_update_item(self):
        request = self.factory.post('/admin/navigation/menu/1/update_item', {'id': 11, 'title': 'new title', 'parent' : ''})
        
        admin = MenuAdmin(Menu, None)
        response = admin.update_item_view(request, 1)
        self.assertNotEqual(None, response)
        
    def test_refresh_items(self):
        from navigation.admin import refresh_items
        queryset = Menu.objects.filter(id=1)
        refresh_items(None, None, queryset)
        
    def test_add_item_performance(self):
        request = self.factory.post('/admin/navigation/menu/1/add_item', {})
        
        admin = MenuAdmin(Menu, None)
        for i in range(30):
            admin.add_item_view(request, 1)
            
    