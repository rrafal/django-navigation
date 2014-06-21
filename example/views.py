
from django.db import transaction
from django.shortcuts import render
from cms.models import Page
from navigation.models import Menu, Sitemap

def home(request):
	return render(request, 'example/home.html', {}) 

@transaction.atomic
def setup(request):
	from django.contrib.sites.models import Site
	from navigation.utils import discover_sitemaps, refresh_all_menus
	
	discover_sitemaps()
	
	if Page.objects.count() == 0:
		home_page = _create_page("Life", None)
		animals_page = _create_page("Animals", None)
		plants_page = _create_page("Plants", None)
		fungi_page = _create_page("Fungi", None)
		bacteria_page = _create_page("Bacteria", None)
		
		birds_page = _create_page("Birds", animals_page)
		fishes_page = _create_page("Fishes", animals_page)
		insects_page = _create_page("Insects", animals_page)
		mammals = _create_page("Mammals", animals_page)
		
		_create_page("Cardinal", birds_page)
		_create_page("Crow", birds_page)
		_create_page("Dove", birds_page)
		_create_page("Ducks", birds_page)
		_create_page("Finch", birds_page)
		_create_page("Geese", birds_page)
		_create_page("Cardinal", birds_page)
		_create_page("Jay", birds_page)
		_create_page("Woodpecker", birds_page)
		
		_create_page("Bass", fishes_page)
		_create_page("Betta", fishes_page)
		_create_page("Cod", fishes_page)
		_create_page("Goldfish", fishes_page)
		
	
	if Menu.objects.filter(name='Main Menu').count() == 0:
		menu = Menu(name='Main Menu')
		menu.site = Site.objects.get_current()
		menu.sitemap = Sitemap.objects.get(slug='cms-pages')
		menu.save()
		
	
	refresh_all_menus()
	
	return render(request, 'example/setup.html', {}) 


def _create_page(title, parent):
	from cms.api import create_page
	from cms.constants import TEMPLATE_INHERITANCE_MAGIC
	from django.conf import settings
	
	language = settings.LANGUAGES[0][0]
	
	return create_page(title, TEMPLATE_INHERITANCE_MAGIC, language, parent=parent, in_navigation=True, published=True)
	