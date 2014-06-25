
from navigation.tests.utils import *
from navigation.tests.models import *
from navigation.tests.admin import *
from navigation.tests.templatetags import *



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

