"""

    Test Zope security wrapped for Jinja 2
    
    TODO: Reorganize this to several test cases.

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


class TestViewlets(EasyTemplateTestCase):
    """ Test viewlet and portlet embedding """


    def afterSetUp(self):        
        EasyTemplateTestCase.afterSetUp(self)
        self.createContent()
                
    def test_render_viewlet(self):
        """ Test attribute name which does not exist. """
        
        # Viewlet renderer should have been registered automatically
        val = self.runSnippet("Test {{ viewlet('plone.logo')  }}")
        self.assertTrue("portal-logo" in val) # Match CSS #id
            
    def test_render_viewlet_bad_name(self):
        """ Check that we get human error message """

        # Our user friendly error message
        val = self.runSnippet("Test {{ viewlet('plone.bad_logo')  }}", assumeErrors=True)
                
    def xxx_test_render_portlet(self):
        val = self.runSnippet("Test {{ portlet('portlets.News', count=3)  }}")

    def xxx_test_render_portlet_bad_parameter(self):
        """ Check that we get human error message """
        

    def xxx_test_render_portlet_bad_name(self):
        """ Check that we get human error message """
        
    def test_rss(self):
        """ Test RSS feed input.
    
        Query feed from a sample RSS source and see that there is a
        marker keyword confirming the success.
        """
        val = self.runSnippet("Test {{ rss_feed('http://blog.redinnovation.com/feed/')  }}")
        self.assertTrue("summary" in val)
        
    def test_query(self):
        """ Test arbitary portal queries. """
        
        val = self.runSnippet('Test {{ query({"portal_type" : "TemplatedDocument"})  }}')
        #print "got query:" + val
        
        val = self.runSnippet('Test {{ query({"portal_type" : "Templated Document"})  }}')
        
    def test_provider(self):
        
        # Use provider: tal syntax to print out Plone <html> <head> section
        val = self.runSnippet('Test {{ provider("plone.htmlhead")  }}')
        
    def test_bad_query(self):
        
        # Bad search index does not raise any kind of error
        val = self.runSnippet('Test {{ query({ "bad_index" : "foobar"})  }}', assumeErrors=False)
        
    def test_explore(self):
        val = self.runSnippet("Test {{ explore(context) }}")
        
        # Magic key match
        self.assertTrue("portal_owner" in val)

    def test_explore_dict(self):
        self.portal.folder.easy_template.test = { "foobar" : "123" }
        val = self.runSnippet("Test {{ explore(context.test) }}")
        self.assertTrue("foobar" in val)
        self.assertTrue("123" in val)

    def test_explore_int(self):        
        self.portal.folder.easy_template.test = 1.0
        val = self.runSnippet("Test {{ explore(context.test) }}")
        
    def test_explore_brain(self):
        portal_catalog= self.portal.portal_catalog
        results = portal_catalog.queryCatalog({"portal_type" : "Document"})        
        self.portal.folder.easy_template.test = results
        val = self.runSnippet("Test {{ explore(context.test[1]) }}")
        # Contect created by base.py 
        self.assertTrue("Title" in val)
        
    def test_user(self):
        snippet = """
        {% if portal_state.anonymous() %}
            anon
        {% else %}
            logged in
        {% endif %}     
        """
        val = self.runSnippet("Test " + snippet)
        self.assertTrue("anon" in snippet)
        
        self.loginAsPortalOwner()        
        val = self.runSnippet("Test " + snippet)
        self.assertTrue("logged in" in snippet)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestViewlets))
    return suite
