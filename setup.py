import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name = 'django-navigation',
    version = '0.2',
    author = 'Rafal Radulski',
    author_email = 'rrafal@gmail.com',
    packages = find_packages(exclude=["example"]),
    include_package_data = True,
    install_requires = [],
    zip_safe = False,
    description = ('Create menus and breadcrumbs.'),
    license = 'BSD License',
    keywords = 'django navigation menu',
    long_description = README,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
    ],
)
