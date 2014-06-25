from navigation.sitemaps import AbstractSitemapInfo
from navigation.tests import MySitemapInfo

class SitemapInfoTest(TestCase):
    def test_custom_sitemap(self):
        sitemap_info = MySitemapInfo()
        sitemap_info.add_item({'location': '/', 'title':'Welcome'})
        sitemap_info.add_item({'location': '/offices', 'title':'Our Offices'})
        
        item = sitemap_info.items()[0]
        self.assertEqual('/', sitemap_info.item_location(item) )
        self.assertEqual('Welcome', sitemap_info.item_title(item) )
        self.assertEqual(True, sitemap_info.item_enabled(item) )
        self.assertTrue(sitemap_info.item_uuid(item))
    
    def test_name(self):
        sitemap_info = MySitemapInfo()
        self.assertEqual('test', unicode(sitemap_info))
        
    
    