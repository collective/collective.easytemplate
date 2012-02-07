# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.easytemplate
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read().decode("utf-8")

version = '0.7.10'

long_description = read('docs', 'Introduction.txt') + \
    read('docs', 'TemplateEngine.txt') + \
    read('docs', 'Objects.txt') + \
    read('docs', 'Security.txt') + \
    read('docs', 'Authoring.txt') + \
    read('docs', 'Context.txt') + \
    read('docs', 'Tags.txt') + \
    read('docs', 'RegisteringTags.txt')

tests_require=['zope.testing']

setup(name='collective.easytemplate',
      version=version,
      description="Dynamic HTML generation and scripting of pages, content rules, portlets and emails",
      long_description=long_description.encode("utf-8"),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone cheetah jinja template kupu scripting dynamic page html',
      author='mFabrik Research Oy',
      author_email='info@mfabrik.com',
      url='http://plone.org/products/easy-template',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'Jinja2',
                        'plone.portlet.static',
                        'collective.templateengines',
                        'feedparser' # needed by RSS tag, could be soft dependency
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'collective.easytemplate.tests',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      paster_plugins = ["ZopeSkel"],
      )
