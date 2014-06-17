

from django.test import TestCase
from navigation.utils import AbstractSitemapInfo

class SitemapInfoTest(TestCase):
    

    def test_custom_sitemap(self):
        sitemap_info = MySitemapInfo()
        sitemap_info.add_item({'location': '/', 'title':'Welcome'})
        sitemap_info.add_item({'location': '/offices', 'title':'Our Offices'})
        
        item = sitemap_info.items()[0]
        self.assertEqual('/', sitemap_info.item_location(item) )
        self.assertEqual('/', sitemap_info.item_attr(item, 'location') )
        
        self.assertEqual('Welcome', sitemap_info.item_title(item) )
        self.assertEqual('Welcome', sitemap_info.item_attr(item, 'title') )
        
        self.assertEqual(True, sitemap_info.item_enabled(item) )
        self.assertTrue(sitemap_info.item_uuid(item))
    
    def test_name(self):
        sitemap_info = MySitemapInfo()
        self.assertEqual('test', unicode(sitemap_info))
        
class MySitemapInfo(AbstractSitemapInfo):
    slug = "test"

    
    def __init__(self):
        AbstractSitemapInfo.__init__(self, None)
        self._items = []
        
    def items(self):
        return self._items
    
    def add_item(self, item):
        self._items.append(item)
        
    def item_title(self, item):
        if 'title' in item:
            return item['title']
        else:
            return self.location(item)
        
    def item_location(self, item):
        return item['location']
    
    def item_enabled(self, item):
        if 'enabled' in item:
            return item['enabled']
        else:
            return True
    
