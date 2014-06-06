
from django.contrib import admin
from django.conf.urls import patterns
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST, require_safe
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.core.urlresolvers import reverse

from navigation.models import Sitemap, Menu, MenuItem

from django.conf import settings

def refresh_items(modeladmin, request, queryset):
    Sitemap.objects.refresh_current_site()
    for menu in queryset.all():
        menu.refresh()
    
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
        self._check_sitemap()
        return super(MenuAdmin, self).changelist_view(*args, **kw)
    
    def change_view(self, *args, **kw):
        self._check_sitemap()
        return super(MenuAdmin, self).change_view(*args, **kw)
    
    def add_view(self, *args, **kw):
        self._check_sitemap()
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
                    item.save()

                    id_map[my_id] = item

                    if item in old_items:
                        old_items.remove(item)

            # assign parent
            for i in range(0, int(request.POST.get('menuitem-max')) + 1):
                my_id = request.POST.get('menuitem-%d-id' % (i,))
                parent_id = request.POST.get('menuitem-%s-parent' % (i,))

                if my_id:
                    item = id_map.get(my_id)
                    item.parent = id_map.get(parent_id)
                    item.save()


            # remove old items
            for item in old_items:
                item.delete()
        
        # done
        obj.refresh()
        

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
            data['items'].append( self._serialize_item(item))
        
        return HttpResponse(simplejson.dumps(data), mimetype="application/json")

    def refresh_view(self, request, menu_id):
        
        Sitemap.objects.refresh_current_site()
        menu = Menu.objects.get(pk=menu_id)
        menu.refresh()
        
        url = request.build_absolute_uri( reverse('admin:navigation_menu_change', args=[menu.id]) )
        return HttpResponseRedirect(url)
        
    
    def _serialize_item(self, item):
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
        
        if item.sitemap_item:
            data['sitemap_item_id'] = item.sitemap_item.id
            data['sitemap_item_title'] = item.sitemap_item.title
            data['sitemap_item_status'] = item.sitemap_item.status
            
        return data
    
    def _check_sitemap(self):
        ''' Discover sitemaps if there are none yet,
        If sitemap already exists, user has to request refresh manually '''
        if Sitemap.current_objects.count() == 0:
            Sitemap.current_objects.refresh_current_site()
            
   
admin.site.register(Menu, MenuAdmin)

