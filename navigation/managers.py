
from django.db import models, transaction
from django.core.exceptions import  ObjectDoesNotExist
from django.contrib.sites.models import Site

from navigation.utils import get_sitemap_info_list


class SiteModelManager(models.Manager):
    ''' A manager for models that are assigned to a site.
    It's to be ONLY used internally 
    '''
    def __init__(self, site=None, *args, **kwargs):
        super(SiteModelManager, self).__init__(*args, **kwargs)
        self.site = site
        
    def get_query_set(self):
        site_id = self.get_site_id()
        
        if site_id == None:
            return super(SiteModelManager, self).get_query_set()
        else:
            return super(SiteModelManager, self).get_query_set().filter(site_id=site_id)

            
    
    def get_site_id(self):
        if self.site == None:
            return None
        elif self.site == 'current':
            return Site.objects.get_current().id
        else:
            return self.site


class SitemapManager(SiteModelManager):
    pass
        
class MenuManager(SiteModelManager):
    pass



