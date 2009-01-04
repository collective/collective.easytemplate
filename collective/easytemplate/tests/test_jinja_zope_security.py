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

from Products.statusmessages.interfaces import IStatusMessage


class TestSecurity(EasyTemplateTestCase):
    
    def afterSetUp(self):
        engine.setDefaultEngine()
        self.createContent()
        
    def createContent(self):
        self.loginAsPortalOwner()
        
        # Published folder
        self.portal.invokeFactory("Folder", "folder")
                
        # Published doc
        self.portal.folder.invokeFactory("Document", "doc")
        self.portal.folder.invokeFactory("Document", "doc_published")
        
        self.portal.folder.invokeFactory("TemplatedDocument", "easy_template")
        
        self.portal.folder.easy_template.setCatchErrors(True)
        
        self.portal.folder.doc_published.setTitle("Published Title")
        self.portal.folder.doc.setTitle("Unpublished")                
                
        self.portal.portal_workflow.doActionFor(self.portal.folder.doc_published, "publish")
        self.portal.portal_workflow.doActionFor(self.portal.folder.easy_template, "publish")
        self.portal.portal_workflow.doActionFor(self.portal.folder, "publish")
        self.logout()
        
    def runSnippet(self, str, admin=False, assumeErrors=False):
        """ Execute Jinja snippet in a secure context. 
        
        @param assumeErrors: There should be error output
        """
        doc = self.portal.folder.easy_template
        self.loginAsPortalOwner()
        doc.setText(str)
        
        if not admin:        
            self.logout()
            
        output = doc.getTemplatedText()
        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()        
        
        if messages:            
            for m in messages: 
                print "Template error:" + m.message
            
        if assumeErrors:
            # There should be no error messages
            self.assertNotEqual(len(messages), 0)
        else:
            self.assertEqual(len(messages), 0)
            
        return output
    
    def test_00_assume_jinja(self):
        """ Only Jinja backend supports security.
        """
        self.assertTrue(isinstance(engine.getEngine(), jinja.Engine))

    def test_bad_attribute(self):
        """ Test attribute name which does not exist. """
        val = self.runSnippet("Test {{ context.foobar }}")
        print "Got val:" + str(val)
        raise RuntimeError("Undefined variables are not yet caught - remember to fix this please")
        
    def test_allowed_traverse(self):
        val = self.runSnippet("Test {{ context.aq_parent.doc_published.Title() }}")
        self.assertEqual(val, "<p>Test Published Title</p>")

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
        self.assertEqual(val, "<p>Test Unpublished</p>")
        
    def test_set_title_as_admin(self):
        """ Call a setter method when logged in as admin.
        
        This should be allowed, though not useful."""
        val = self.runSnippet("Test {{ context.aq_parent.setTitle('abc') }}", admin=True)                        
        self.assertEqual(val, "<p>Test None</p>")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSecurity))
    return suite
