django-navigation
=================

Creates navigation menus and breadcrumbs.

Features
--------

 - flatpages, and django-cms support out of the box
 - auto-generated menus
 - custom menus
 - auto-generated breadcrumbs
 - select current navigation item
 - display part of a menu


Example
--------

Bello is a sample template that you can use to display flatpages. 

    {% load navigation_tags %}
    <html>
        <head>
    		<title>{{ flatpage.title }}</title>
    	</head>
    	<body>
    		
    		<h1>{{ flatpage.title }}</h1>
    		<div>{% show_navigation_breadcrumbs with sitemap="flatpages" request_path=flatpage.url  %}</div>
    		<nav>
    			{% show_navigation_menu "Main Menu" %}
    		</nav>
    		<div>{{ flatpage.content }}</div>
    	</body>
    </html>


How to Use
----------

You can use two template tag in you templates:
 - show_navigation_breadcrumbs
 - show_navigation_menu


