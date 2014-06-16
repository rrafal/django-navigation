
from django.test import TestCase
from django.test.client import RequestFactory

from navigation.admin import MenuAdmin
from navigation.models import Menu



class MenuAdminTest(TestCase):
    fixtures = ['simple_menus', 'simple_site']
    
    def setUp(self):
        self.factory = RequestFactory()


        
    def test_refresh_items(self):
        from navigation.admin import refresh_items
        queryset = Menu.objects.filter(id=1)
        refresh_items(None, None, queryset)
        

            
    