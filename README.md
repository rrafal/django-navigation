# django-navigation


django-navigation is a dedicated app for creating menus and breadcrumbs. I believe that Django needs and deserves a dedicated navigation app such as this one. It is independent of other apps that generate your website pages, it works across app boundaries and it's easily customizable (using templates). Read [our wiki](github.com/rrafal/django-navigation/wiki) to learn more how django-navigation can help you.

### Features

 - flatpages, and django-cms support out of the box
 - auto-generated menus
 - custom menus
 - auto-generated breadcrumbs
 - select current navigation item
 - display part of a menu


### Example

![ScreenShot](https://raw.githubusercontent.com/rrafal/django-navigation/master/screenshots/website-menu.png)

Bellow is a sample template that you can use to display flatpages. 

    {% load navigation_tags %}
    <html>
        <head>
    		<title>{{ flatpage.title }}</title>
    	</head>
    	<body>
    		
    		<h1>{{ flatpage.title }}</h1>
    		<div>{% show_navigation_breadcrumbs with sitemap="flatpages"  %}</div>
    		<nav>
    			{% show_navigation_menu "Main Menu" %}
    		</nav>
    		<div>{{ flatpage.content }}</div>
    	</body>
    </html>
    

### Authors
 - [Rafal Radulski](http://www.radulski.net/)


## Installation

1. Edit settings.py
2. Add 'navigation' to INSTALLED_APPS
3. Add NAVIGATION_SITEMAPS. You can add following entries:
  - 'navigation.base.FlatPageSitemapInfo'
  - 'navigation.base.CMSSitemapInfo'

Example:

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.flatpages',
        'south',    
        'navigation',
    )

    NAVIGATION_SITEMAPS = (
        'navigation.base.FlatPageSitemapInfo',
    )

### How to Use


You will find a new section in you Django Admin. It allows you to create menus.

When you change pages, menus need to be refreshed. Go to a menu that needs to be 
updated and click "Refresh". You can also select all menus and update them all at once.

Once you create a menu, you need to add it to template. Use **show_navigation_menu** to do it.
You need to give it menu name. You can also tell it to display only a part of the menu. 

    {% show_navigation_menu "Main Menu" with root="/accounts/"  %}


If *django.core.context_processors.request* is not enabled, or *RequestContext* is not used,
you can pass current URL directly. For example:

    {% show_navigation_menu "Main Menu" with request_path=flatpage.url  %}
    
To customize the HTML of the output, copy and edit this template file: **navigation/templates/navigation/menu.html**
You can also specify your own template in the tag:

    {% show_navigation_menu "Main Menu" with template="nav/simple_menu.html"  %}

You can add breadcrumbs using **show_navigation_breadcrumbs** template tab. You need to tell it what sitemap to use:

    {% show_navigation_breadcrumbs with sitemap="flatpages"  %}
    
If you rather use menu to generate sitemaps, you can do that too:

    {% show_navigation_breadcrumbs with menu="Main Menu"  %}

Sitemap support *request_path* and *tempalate* arguments as well:

    {% show_navigation_breadcrumbs with sitemap="flatpages", request_path=flatpage.url, template="nav/simple_crumbs.html"  %}


### Help


If you don't know how to do something. Check the wiki first:
https://github.com/rrafal/django-navigation/wiki

django-navigation is a very new project. It surely has some bugs. If you find any, please report.
There are some features that I'd like to add to the project. If you have any too, make a request.

I'm rather new to django. If you have any suggestions for this project, please submit them to me.



