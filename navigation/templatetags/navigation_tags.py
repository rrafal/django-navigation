


from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template
from django.template.context import Context as TemplateContext
from django.utils.translation import pgettext

from navigation.models import Sitemap, Menu, MenuItem


register = template.Library()


@register.simple_tag(takes_context=True)
def show_navigation_menu(context, menu, request_path=None, root=None, template='navigation/menu.html'):
	""" Displays a navigation menu with given name 
	
	Passes the following information to template:
	depth -- 0 if rendering the first level of menu
	menu -- complete menu being rendered
	parent -- parent of items that are rendered
	items -- items being rendered
	current_item -- item that visitor is currently viewing
	current_parent_item -- parent of current_item
	current_ancestors_items -- all ancestors of current_item
	
	
	Arguments:
	menu -- name of the menu or menu item
	root -- url of the root menu item
	style -- style of the menu
	"""

	# get the menu
	try:
		data = get_navigation_menu(menu, root)
	except ObjectDoesNotExist:
		return show_missing_menu(context, menu, 'navigation/menu-missing.html')
	
	if isinstance(context, Context):
		data['depth'] = context['depth'] + 1
	else:
		data['depth'] = 0
	

	
	# are we rendering empty submenu
	if len(data['items']) == 0 and data['depth'] > 0:
		return '';

	# get info on where we are in the menu
	if isinstance(context, Context):
		data['depth'] = context['depth'] + 1
		data['current_item'] = context['current_item']
		data['current_parent_item'] = context['current_parent_item']
		data['current_ancestor_items'] = context['current_ancestor_items']
	else:
		data['depth'] = 0;
		data['current_item'] = None
		data['current_parent_item'] = None
		data['current_ancestor_items'] = []
	
		the_path = None
		if request_path != None:
			the_path = request_path
		elif 'request' in context:
			the_path = context['request'].path
		
		if the_path != None:
			for k, v in get_current_items(data['menu'], the_path).items():
				data[k] = v
	
	# render
	new_context = Context(data, *{
	    'autoescape': context.autoescape,
	    'current_app': context.current_app,
	    'use_l10n': context.use_l10n,
	    'use_tz': context.use_tz,
		})
	
	return get_template(template).render(new_context)

def get_navigation_menu(menu, root=None):
	this = None # currently display element; Menu or MenuItem
	the_menu = None # complete menu; Menu
	the_items = [] # current items; list of MenuItem
	the_parent = None # current element; MenuItem
	
	# get the menu
	if isinstance(menu, Menu):
		the_menu = menu
		this = menu
	elif isinstance(menu, MenuItem):
		the_menu = menu.menu
		this = menu
	else:
		the_menu = Menu.objects.get(name=menu)
		this = the_menu
	
	# if root specified, get it now
	if root:
		root_items = the_menu.find_items(url=root)
		if len(root_items) > 0:
			this = root_items[0]
		else:
			this = None
	
	# get items
	if this == None:
		pass
	elif isinstance(this, Menu):
		the_items = this.list_top_items()
	else:
		the_parent = this
		the_items = this.children
		
	the_items = [item for item in the_items if item.is_enabled()]
		
	# done
	return {
		'items' : the_items,
		'parent' : the_parent,
		'menu' : the_menu,
		}


def get_current_items(menu, current_url):
	''' Get info about where we are in the menu. '''
	result = {
		'current_item': None,
		'current_parent_item': None,
		'current_ancestor_items': [],
		}
	
	the_menu = None
	if isinstance(menu, Menu):
		the_menu = menu
	else:
		the_menu = Menu.objects.get(name=menu)
		
	current_items = the_menu.find_items(url=current_url)
	if len(current_items):
		result['current_item'] = current_items[0]
		result['current_parent_item'] = result['current_item'].parent
	
		ancestor = result['current_parent_item']
		while ancestor:
			result['current_ancestor_items'].append(ancestor)
			ancestor = ancestor.get_parent()
	return result


@register.simple_tag(takes_context=True)
def show_navigation_breadcrumbs(context, menu=None, sitemap=None, request_path=None, template='navigation/breadcrumbs.html'):
	""" Displays breadcrumbs for current page.
	
	It may use pages to figure out the page hierarchy. If you are using
	custom model to implement pages, and the model has "parent" attribute,
	pass the current model-object as "page".
	
	Example:
	show_navigation_breadcrumbs with page=current_page
	
	If you want to have breadcrumbs to some page that doesn't fit above
	assumptions, don't use this tag. 
	
	
	Arguments:
	menu -- menu to use to figure out the hierarchy of pages
	sitemap -- slug of sitemap to use
	"""
	
	the_path = None
	if request_path != None:
		the_path = request_path
	elif 'request' in context:
		the_path = context['request'].path
	
	if the_path == None:
		return ''
	
	try:
		items = get_navigation_breadcrumbs(the_path, menu, sitemap)
	except ObjectDoesNotExist:
		name = menu or sitemap or '--'
		return show_missing_menu(context, name, 'navigation/breadcrumbs-missing.html')
	
	data = {'items': items }
	new_context = Context(data, *{
		'autoescape': context.autoescape,
		'current_app': context.current_app,
		'use_l10n': context.use_l10n,
		'use_tz': context.use_tz,
		})
	return get_template(template).render(new_context)

		

def get_navigation_breadcrumbs(current_path, menu=None, sitemap=None):

	items = False
	
	# create breadcrumbs from menu
	if not items and menu != None:
		try:
			items = get_breadcrumbs_from_menu(current_path, menu)
		except ObjectDoesNotExist:
			pass
	
	# create breadcrubs from sitemap
	if not items and sitemap != None:
		try:
			items = get_breadcrumbs_from_sitemap(current_path, sitemap)
		except ObjectDoesNotExist:
			pass

	# we must have the menu by now			
	if items == False:
		raise ObjectDoesNotExist()
	
	if not items:
		return None
	
	# add home item if needed
	from urlparse import urlparse
	top_url = urlparse(items[-1].url)
	
		
	if top_url.path != '' and top_url.path != '/':
		home_item = MenuItem()
		home_item.title = pgettext('navigation', 'Home')
		home_item.url = '/'
		items.append(home_item)
		
	items.reverse()
	return items

def get_breadcrumbs_from_menu(current_path, menu):
	the_menu = None
	if isinstance(menu, Menu):
		the_menu = menu
	elif isinstance(menu, MenuItem):
		the_menu = menu.menu
	else:
		the_menu = Menu.objects.get(name=menu)
		
	current_items = the_menu.find_items(url=current_path)

	if len(current_items):
		breadcrumbs = []
		item = current_items[0]
		while item:
			breadcrumbs.append(item)
			item = item.parent
		return breadcrumbs
	else:
		return None

def get_breadcrumbs_from_sitemap(current_path, sitemap):
	if isinstance(sitemap, Sitemap):
		the_sitemap = sitemap
	else:
		the_sitemap = Sitemap.current_objects.get(slug=sitemap)
		
	current_items = the_sitemap.item_set.filter(url=current_path)
	
	if len(current_items):
		breadcrumbs = []
		sitemap_item = current_items[0]
		while sitemap_item:
			menu_item = MenuItem()
			menu_item.title = sitemap_item.title
			menu_item.url = sitemap_item.url
			menu_item.status = sitemap_item.status
			breadcrumbs.append(menu_item)
			
			sitemap_item = sitemap_item.parent
		return breadcrumbs
	else:
		return None


def show_missing_menu(context, menu, template):
	if menu:
		data = {'name': menu }
		new_context = Context(data, *{
			'autoescape': context.autoescape,
			'current_app': context.current_app,
			'use_l10n': context.use_l10n,
			'use_tz': context.use_tz,
			})
		return get_template(template).render(new_context)
	else:
		return ''

class Context(TemplateContext):
	''' Context used for rendering menus.
	
	Allows to efficiently render submenus.
	'''
	pass
        


