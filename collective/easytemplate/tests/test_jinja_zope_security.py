"""

    Test Zope security wrapped for Jinja 2

"""

__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'plaintext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

from Products.CMFCore.utils import getToolByName

from Products.statusmessages.interfaces import IStatusMessage

from collective.easytemplate.content.TemplatedDocument import ERROR_MESSAGE
from collective.easytemplate.tests.base import EasyTemplateTestCase

from zope.component import getUtility, getMultiAdapter, getSiteManager
from zope.component.interfaces import IObjectEvent
from zope.interface import implements

from collective.easytemplate import tagconfig, engine
from collective.templateengines.backends import jinja

class TestSecurity(EasyTemplateTestCase):
    
    def afterSetUp(self):        
        EasyTemplateTestCase.afterSetUp(self)
        self.createContent()
                    
    def test_00_assume_jinja(self):
        """ Only Jinja backend supports security.
        """
        self.assertTrue(isinstance(engine.getEngine(), jinja.Engine))

    def xxx_test_bad_attribute(self):
        """ Test attribute name which does not exist. """
        val = self.runSnippet("Test {{ context.foobar }}")
        print "Got val:" + str(val)
        raise RuntimeError("Undefined variables are not yet caught - remember to fix this please")
        
    def test_allowed_traverse(self):
        val = self.runSnippet("Test {{ context.aq_parent.doc_published.Title() }}")
        self.assertEqual(val, "Test Published Title")

    def test_unallowed_traverse(self):
        """ doc is unpublished object """
        
        from AccessControl.unauthorized import Unauthorized
        #unauthorized = AccessControl.Unauthorized
        
        try:
            val = self.runSnippet("Test {{ context.aq_parent.doc.Title() }}")
            self.assertTrue(False) # Shold not be reached
        except Unauthorized:
            pass
                        
    def test_allowed_attribute(self):
        val = self.runSnippet("Test {{ context.schema }}")

            
    def test_unallowed_attribute(self):
        
        from AccessControl.unauthorized import Unauthorized
                
        try:
            val = self.runSnippet("Test {{ context.__ac_roles__}}")
            self.assertTrue(False) # Shold not be reached
        except Unauthorized:
            pass
       
    def test_unallowed_method(self):
        """ Anonymous user should not be able to call setTitle """

        from AccessControl.unauthorized import Unauthorized
                
        try:
            val = self.runSnippet("Test {{ context.setTitle('abc') }}")
            self.assertTrue(False) # Shold not be reached
        except Unauthorized:
            pass
        
    def test_unallowed_traversed_method(self):
        """ Anonymous user should not be able to call setTitle on parent """

        from AccessControl.unauthorized import Unauthorized
                
        try:
            val = self.runSnippet("Test {{ context.aq_parent.setTitle('abc') }}")
            self.assertTrue(False) # Shold not be reached
        except Unauthorized:
            pass

    def test_access_private_as_admin(self):
        """ Template which prefers to unpublished content should be available as admin"""
        val = self.runSnippet("Test {{ context.aq_parent.doc.Title() }}", admin=True)        
        self.assertEqual(val, "Test Unpublished")
        
    def test_set_title_as_admin(self):
        """ Call a setter method when logged in as admin.
        
        This should be allowed, though not useful."""
        val = self.runSnippet("Test {{ context.aq_parent.setTitle('abc') }}", admin=True)                        
        self.assertEqual(val, "Test None")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSecurity))
    return suite
