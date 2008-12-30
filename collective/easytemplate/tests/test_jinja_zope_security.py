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

from Products.statusmessages.interfaces import IStatusMessage


class TestSecurity(EasyTemplateTestCase):
    
    def afterSetUp(self):
        self.createContent()
        
    def createContent(self):
        self.loginAsPortalOwner()
        
        # Published folder
        self.portal.invokeFactory("Folder", "folder")
                
        # Published doc
        self.portal.invokeFactory("Folder", "folder")
        
        # Unpublished doc
        doc = self.portal.doc        
        
        self.logout()
        
    def test_allowed_attribute(self):
        pass
    
        
    def test_unallowed_attribute(self):
       pass
       
    def test_unallowed_method(self):
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSecurity))
    return suite
