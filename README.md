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
    		<div>{% show_navigation_breadcrumbs with sitemap="flatpages"  %}</div>
    		<nav>
    			{% show_navigation_menu "Main Menu" %}
    		</nav>
    		<div>{{ flatpage.content }}</div>
    	</body>
    </html>


How to Use
----------

You will find a new section in you Django Admin. It allows you to create menus.

When you change pages, menus need to be refreshed. Go to a menu that needs to be 
updated and click "Refresh". You can also select all menus and update them all at once.

Once you create a menu, you need to add it to template. Use *show_navigation_menu* to do it.
You need to give it menu name. You can also intruct it to display only a part of the menu. 

    {% show_navigation_menu "Main Menu" with root="/accounts/"  %}


If *django.core.context_processors.request* is not enabled, or *RequestContext* is not used,
you can pass current URL directly. For example:

    {% show_navigation_menu "Main Menu" with request_path=flatpage.url  %}
    
To customize the HTML of the output, copy and edit this template file: *navigation/templates/navigation/menu.html*
You can also specify your own template in the tag:

    {% show_navigation_menu "Main Menu" with template="nav/simple_menu.html"  %}



