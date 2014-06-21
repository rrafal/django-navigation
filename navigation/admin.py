
from django.contrib import admin
from django.conf.urls import patterns
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST, require_safe
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.core.urlresolvers import reverse

from navigation.models import Sitemap, Menu, MenuItem

from django.conf import settings

class SitemapAdmin(admin.ModelAdmin):
    readonly_fields=('site', 'slug')

@transaction.atomic
def refresh_items(modeladmin, request, queryset):
    from .utils import refresh_menu_from_sitemap
    
    for sitemap in Sitemap.current_objects.all():
        if sitemap.is_available():
            for menu in queryset.all():
                if menu.sitemap == None or menu.sitemap == sitemap:
                    refresh_menu_from_sitemap(menu, sitemap)
    pass
    
refresh_items.short_description = "Refresh menu items"


class MenuAdmin(admin.ModelAdmin):
    class Meta:
        pass
    
    actions = [refresh_items]
    
    fieldsets = (
        (None, {
            'fields': ( 'name', 'sitemap')
        }),
        ('Hidden', {
            'classes': ('hidden',),
            'fields': ('site', )
        }),
    )
    
    hidden_fields = ['site']
    
    def changelist_view(self, *args, **kw):
        self._refresh_sitemaps()
        return super(MenuAdmin, self).changelist_view(*args, **kw)
    
    def change_view(self, *args, **kw):
        self._refresh_sitemaps()
        return super(MenuAdmin, self).change_view(*args, **kw)
    
    def add_view(self, *args, **kw):
        self._refresh_sitemaps()
        return super(MenuAdmin, self).add_view(*args, **kw)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(MenuAdmin, self).get_form(request, obj, **kwargs)
        
        # initialize the form with default values
        if obj == None:
            if form.base_fields['site'].initial is None:
                form.base_fields['site'].initial = settings.SITE_ID
        
        return form
    
    def get_urls(self):
        urls = super(MenuAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^(\d)/view/', self.admin_site.admin_view(self.show_view)),
            (r'^(\d)/refresh/', self.admin_site.admin_view(self.refresh_view)),
            (r'^find-sitemap-items/', self.admin_site.admin_view(self.find_sitemap_items)),
        )
        return my_urls + urls
   
    def save_model(self, request, obj, form, change):
        super(MenuAdmin, self).save_model(request, obj, form, change)

        old_items = obj.list_all_items()
        
        id_map = {}

        # update each item
        if request.POST.get('menuitem-max') is not None:
            for i in range(0, int(request.POST.get('menuitem-max')) + 1):
                my_id = request.POST.get('menuitem-%d-id' % (i,))
                my_order = request.POST.get('menuitem-%d-order' % (i,))
                my_url = request.POST.get('menuitem-%d-url' % (i,))
                my_title = request.POST.get('menuitem-%d-title' % (i,))
                my_status = request.POST.get('menuitem-%d-status' % (i,))
                my_sitemap_item_id = request.POST.get('menuitem-%d-sitemap-item-id' % (i,))

                if my_id:
                    try:
                        item = obj.get_item(id=int(my_id))
                    except Exception as e:
                        item = MenuItem()
                    item.menu = obj
                    item.title = my_title
                    item.url = my_url
                    item.order = my_order
                    item.parent = None
                    item.sitemap_item_id = my_sitemap_item_id
                    item.save()

                    id_map[my_id] = item

                    if item in old_items:
                        old_items.remove(item)

            # assign parent
            for i in range(0, int(request.POST.get('menuitem-max')) + 1):
                my_id = request.POST.get('menuitem-%d-id' % (i,))
                parent_id = request.POST.get('menuitem-%s-parent-id' % (i,))

                if my_id:
                    item = id_map.get(my_id)
                    item.parent = id_map.get(parent_id)
                    item.save()


            # remove old items
            for item in old_items:
                item.delete()
        
        # done
        

    def show_view(self, request, menu_id):
        menu = Menu.current_objects.get(pk=menu_id)
        data = { 
            'id' : menu.id,
            'name' : menu.name,
            'sitemap_id' : None,
            'items': [], 
            }
        
        if menu.sitemap:
            data['sitemap_id'] = menu.sitemap.id
        
        
        
        for item in menu.list_all_items():
            data['items'].append( self._serialize_menu_item(item))
        
        import json
        return HttpResponse(json.dumps(data), content_type="application/json")

    @transaction.atomic
    def refresh_view(self, request, menu_id):
        from .utils import refresh_menu_from_sitemap
    
        menu = Menu.objects.get(pk=menu_id)
        
        if menu.sitemap:
            refresh_menu_from_sitemap(menu, menu.sitemap)
        else:
            for sitemap in Sitemap.current_objects.all():
                if sitemap.is_available():
                    refresh_menu_from_sitemap(menu, sitemap)
        
        url = request.build_absolute_uri( reverse('admin:navigation_menu_change', args=[menu.id]) )
        return HttpResponseRedirect(url)    
    
    def find_sitemap_items(self, request):
        import json
        from .models import Sitemap
        
        matches = []
        
        sitemap_items = []
        for sitemap in Sitemap.current_objects.all():
            if sitemap.is_available():
                for sitemap_item in sitemap.get_items():
                    sitemap_items.append(sitemap_item)
                    
        
        if request.GET.get('url') != None:
            url_1 = request.GET.get('url').lower()
            
            for item in sitemap_items:
                if item['location'].lower().startswith( url_1 ):
                    matches.append( item )
        
        if request.GET.get('term') != None:
            title_1 = request.GET.get('term').lower()
            url_1 = request.GET.get('term').lower()
            url_2 = "/" + request.GET.get('term').lower()
            
            for item in sitemap_items:
                if item['title'].lower().startswith( title_1 ):
                    matches.append( item )
                elif item['location'].lower().startswith( url_1 ):
                    matches.append( item )
                elif item['location'].lower().startswith( url_2 ):
                    matches.append( item )
            
            if not matches:
                for item in sitemap_items:
                    if title_1 in item['title'].lower():
                        matches.append( item )
                    elif url_1 in item['url'].lower():
                        matches.append( item )
            
        data = matches[:100]
        
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def _serialize_menu_item(self, item):
        data = {
            'id': item.id,
            'title' : item.title,
            'url' : item.url,
            'status' : item.status,
            'parent_id' : None,
            'sitemap_item_id' : None,
            'sitemap_item_title' : None,
            'sitemap_item_status' : None,
        }
        
        if item.parent:
            data['parent_id'] = item.parent.id
        
        if item.sitemap_item_id:
            data['sitemap_item_id'] = item.sitemap_item_id
            data['sitemap_item_title'] = item.sitemap_item_title
            data['sitemap_item_status'] = item.sitemap_item_status
            
        return data
    
    def _refresh_sitemaps(self):
        ''' Discover sitemaps if there are none yet,
        If sitemap already exists, user has to request refresh manually '''
        from .utils import discover_sitemaps
        discover_sitemaps()
            
   
admin.site.register(Menu, MenuAdmin)
admin.site.register(Sitemap, SitemapAdmin)


if getattr(settings, 'NAVIGATION_AUTO_REFRESH', False):
    from .utils import initialize_autorefresh
    initialize_autorefresh()

