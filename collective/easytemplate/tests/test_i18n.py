# -*- coding: utf-8 -*-
"""

    Test internationalization tags.
    
    Running these tests needs Products.LinguaPlone installed.
    
    

"""

__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'plaintext'
__copyright__ = "2008-2011 mFabrik Research Oy"
__license__ = "GPL"

import os, sys

from zope.interface import alsoProvides

from collective.easytemplate.tests.base import EasyTemplateTestCase

class TestI18N(EasyTemplateTestCase):
    """ Test i18n functions in the templates """
    
    def afterSetUp(self):        
        EasyTemplateTestCase.afterSetUp(self)
        self.createContent()
        self.loadPOT()
        
    def loadPOT(self):
        """ Load dummy po file to plone domain for testing """

        from Products.PlacelessTranslationService import pts_globals
        from Products.PlacelessTranslationService import PlacelessTranslationService as PTS

        file = sys.modules[__name__].__file__
        path = os.path.abspath(os.path.join(os.path.dirname(file), "i18n_data", "i18n"))

        # Note: This was Plone 2 (!) compatibility or something...
        #service = self.app.Control_Panel.TranslationService
        #service._load_catalog_file(os.path.join(path, "plone-fi.po"), path, language="fi", domain="plone")
                                    
    def test_get_current_language(self):
        """ Test arbitary portal queries. """
            
        val = self.runSnippet('Test {{ current_language() }}')
        self.assertEqual(val, "Test en")
        
    def test_translate(self):
        """ Test arbitary portal queries. """

        # We need to fake the interface here for PTS check        
        # See PTSTranslationDomain.translate
        from zope.publisher.interfaces.browser import IBrowserRequest
        context = self.portal.folder.easy_template
        alsoProvides(context.REQUEST, IBrowserRequest)
        context.REQUEST["PARENTS"] = [self.app]

        val = self.runSnippet('Test {{ translate("box_more_news_link", "plone", "fi")  }}')

        self.assertEqual(val, "Test Lisää uutisia...")

    def test_translate_default(self):
        """ Test translating a missing catalog entry, defaulting to given english string. """

        # We need to fake the interface here for PTS check        
        # See PTSTranslationDomain.translate
        from zope.publisher.interfaces.browser import IBrowserRequest
        context = self.portal.folder.easy_template
        alsoProvides(context.REQUEST, IBrowserRequest)
        context.REQUEST["PARENTS"] = [self.app]

        val = self.runSnippet('Test {{ translate("missing_id", default="Foobar")  }}')

        self.assertEqual(val, "Test Foobar")


def test_suite():
    from unittest import TestSuite, makeSuite
    
    suite = TestSuite()
    
    try:
        import Products.LinguaPlone
    except ImportError:
        # CAn't run without LinguaPlone
        return suite
    
    suite.addTest(makeSuite(TestI18N))
    return suite
