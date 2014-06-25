
from django.db import transaction
from django.shortcuts import render
from cms.models import Page
from navigation.models import Menu, Sitemap

def home(request):
	return render(request, 'example/home.html', {}) 

@transaction.atomic
def setup(request):
	from django.conf import settings
	from django.contrib.sites.models import Site
	from navigation.utils import discover_sitemaps, refresh_all_menus
	
	
	discover_sitemaps()
	
	# disable autorefresh because will be publishing many pages
	settings.NAVIGATION_AUTO_REFRESH = False
	
	if Page.objects.count() == 0:
		_create_page("Home", None)
		_setup_life_tree()
		_setup_calendar()
		
	if Menu.objects.filter(name='Main Menu').count() == 0:
		menu = Menu(name='Main Menu')
		menu.site = Site.objects.get_current()
		menu.sitemap = Sitemap.objects.get(slug='cms-pages')
		menu.save()
		
	refresh_all_menus()
	
	return render(request, 'example/setup.html', {}) 
	
def _setup_calendar():
	from datetime import date, timedelta
	
	calendar_page = _create_page("Calendar", None)
	
	current_date = date(2000, 1, 1) # must start from January 1st
	delta = timedelta(days=1)
	
	month_page = None
	year_page = None
	for i in range(0, 500):
		if current_date.day == 1:
			if current_date.month == 1:
				year_page = _create_page(current_date.strftime('%Y'), calendar_page)
			month_page = _create_page(current_date.strftime('%B %Y'), year_page)
		
		# add weekends
		if current_date.isoweekday() >= 6:
			day_page = _create_page(current_date.isoformat(), month_page)
		
		current_date += delta
	return
	
def _setup_life_tree():
	life_page = _create_page("Life", None)
	animals_page = _create_page("Animals", life_page)
	plants_page = _create_page("Plants", life_page)
	fungi_page = _create_page("Fungi", life_page)
	bacteria_page = _create_page("Bacteria", life_page)

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


def _create_page(title, parent):
	from cms.api import create_page
	from cms.constants import TEMPLATE_INHERITANCE_MAGIC
	from django.conf import settings
	
	language = settings.LANGUAGES[0][0]
	
	return create_page(title, TEMPLATE_INHERITANCE_MAGIC, language, parent=parent, in_navigation=True, published=True)
	