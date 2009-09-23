from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.easytemplate.browser.portlets import templated

from base import EasyTemplateTestCase

PORTLET_NAME="collective.easytemplate.TemplatedPortlet"

class TestPortlet(EasyTemplateTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name=PORTLET_NAME)
        self.assertEquals(portlet.addview, PORTLET_NAME)

    def testInterfaces(self):
        portlet = templated.TemplatedPortletAssignment(header=u"title", text="text")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name=PORTLET_NAME)
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'header' : u"test title", 'text' : u"test text"})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], templated.TemplatedPortletAssignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = templated.TemplatedPortletAssignment(header=u"title", text="text")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, templated.TemplatedPortletEditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = templated.TemplatedPortletAssignment(header=u"title", text="text")

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, templated.TemplatedPortletRenderer))

    def testExpression(self):
        """ Check that persistent expression object is created succesfully """
        
        assignment=templated.TemplatedPortletAssignment(header=u"title", text="<b>text</b>", expression="python:False")
        
        self.assertEqual(assignment.expression, "python:False")
        self.assertNotEqual(assignment._expression_object, None)
        

class TestRenderer(EasyTemplateTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or templated.TemplatedPortletAssignment(header=u"title", text="text")

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal, assignment=templated.TemplatedPortletAssignment(header=u"title", text="<b>text</b>"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('title' in output)
        self.failUnless('<b>text</b>' in output)
        
    def test_css_class(self):
        r = self.renderer(context=self.portal, 
                          assignment=templated.TemplatedPortletAssignment(header=u"Welcome text", text="<b>text</b>"))
        self.assertEquals('portlet-static-welcome-text', r.css_class())

    def test_expression_true(self):
        r = self.renderer(context=self.portal, assignment=templated.TemplatedPortletAssignment(header=u"title", text="<b>text</b>", expression="python:True"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('title' in output, "Got:" + output)
        self.failUnless('<b>text</b>' in output)

    def test_expression_empty(self):
        r = self.renderer(context=self.portal, assignment=templated.TemplatedPortletAssignment(header=u"title", text="<b>text</b>", expression=""))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('title' in output, "Got:" + output)
        self.failUnless('<b>text</b>' in output, "Got:" + output)

    def test_expression_unicode_strip(self):
        r = self.renderer(context=self.portal, assignment=templated.TemplatedPortletAssignment(header=u"title", text="<b>text</b>", expression=u"  "))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('title' in output, "Got:" + output)
        self.failUnless('<b>text</b>' in output, "Got:" + output)


    def test_expression_false(self):
        
        r = self.renderer(context=self.portal, assignment=templated.TemplatedPortletAssignment(header=u"title", text="<b>text</b>", expression="python:False"))
        r = r.__of__(self.folder)
        r.update()        
            
        output = r.render()
        self.assertEqual(output, "")
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
