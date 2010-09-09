# -*- coding: utf-8 -*-
"""

    Content rule action test case.

"""

__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'plaintext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

from Products.CMFCore.utils import getToolByName

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import User

from Products.statusmessages.interfaces import IStatusMessage

from collective.easytemplate.content.TemplatedDocument import ERROR_MESSAGE
from collective.easytemplate.tests.base import EasyTemplateTestCase

from email.MIMEText import MIMEText
from zope.component import getUtility, getMultiAdapter, getSiteManager
from zope.component.interfaces import IObjectEvent
from zope.interface import implements

from plone.app.contentrules.rule import Rule
from collective.easytemplate.actions.mail import MailAction, MailEditForm, MailAddForm
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction, IExecutable

from Products.MailHost.interfaces import IMailHost
from Products.SecureMailHost.SecureMailHost import SecureMailHost
from Products.statusmessages.interfaces import IStatusMessage

from collective.easytemplate import tagconfig, engine

class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object

class DummySecureMailHost(SecureMailHost):
    meta_type = 'Dummy secure Mail Host'
    def __init__(self, id):
        self.id = id
        self.sent = []
        
        self.mto = None

    def _send(self, mfrom, mto, messageText, debug=False):
        self.sent.append(messageText)
        
        self.mto = mto

class TestMailAction(EasyTemplateTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', 'target')
        self.folder.invokeFactory('Document', 'd1',
            title=unicode('Wälkommen', 'utf-8'))
        
        # old tests - were written  for cheetah
        #engine.setupEngine(cheetah.Engine())
                

    def testRegistered(self):
        element = getUtility(IRuleAction, name='collective.easytemplate.actions.Mail')
        self.assertEquals('collective.easytemplate.actions.Mail', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testExecute(self):
        
        # Put in stub email sender
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        
        # Create an action
        e = MailAction()
        e.source = "foo@bar.be"
        e.recipients = "bar@foo.be"
        e.subject = "Test mail"
        e.message = u"Päge  {{ text }}' with title {{ title }} created in {{ object_url }} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        
        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()        
        
        if messages:
            for m in messages: print str(m.message)
            
        # No template error messages
        self.assertEqual(len(messages), 0)         
        
        self.assertEqual(len(dummyMailHost.sent), 1)
        
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("bar@foo.be", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        
        # TODO: Compare title/body in mail
                            
    def testExecuteTemplatedEmail(self):
        """ Create recipients email using a template variable exposed from AT. """
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailAction()
        
        # Snatch email receiver from AT content title 
        # Ugly but goes for a test
        self.folder.d1.setTitle("bar@foo.be")
        e.source = "foo@bar.be"
        e.recipients = "{{ title }}"
        e.subject = "Test mail"
        e.message = u"Päge '{{ text }}' with title {{ title }} created in {{ object_url }} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("bar@foo.be", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        
        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()        
        
        if messages:
            for m in messages: print str(m.message)
            
        # No template error messages
        self.assertEqual(len(messages), 0)               
    

    def xxx_testExecuteMissingVar(self):
        """ Template contains syntax errors, we should receive status messages. """
        
        #
        # TODO: Jinja backend doesn't support missing variable catching - used to be Cheetah test case
        #
        
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailAction()
        e.recipients = 'bar@foo.be,foo@bar.be'
        e.subject = "Test mail"
        e.message = 'Missing template variable {{ missing }}'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        self.assertRaises(ValueError, ex)
        # if we provide a site mail address this won't fail anymore
        sm.manage_changeProperties({'email_from_address': 'manager@portal.be'})
        ex()

        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()        
        
        if messages:
            for m in messages: print str(m.message)
                        
        self.assertEqual(len(dummyMailHost.sent), 0)
                            
        # No template error messages
        self.assertEqual(len(messages), 1)             

    def testExecuteTemplatedEmailUnicode(self):
        """ Create recipients email using a template variable exposed from AT. """
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailAction()
        
        # Snatch email receiver from AT content title 
        # Ugly but goes for a test
        self.folder.d1.setTitle(u"ÅÄÖ")
        e.source = "foo@bar.be"
        e.recipients = "bar@foo.be"
        e.subject = u"Testing åäö {{ title }}"
        e.message = u"Päge '{{ text }}' with title {{ title }} created in {{ object_url }} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("bar@foo.be", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        
        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()        
        
        if messages:
            for m in messages: print str(m.message)
            
        # No template error messages
        self.assertEqual(len(messages), 0)          

    def testExecuteTemplatedEmailBrokenEncoding(self):
        """ Test utf-8 literals in unicode string.
        
        """
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailAction()
        
        # Snatch email receiver from AT content title 
        # Ugly but goes for a test
        self.folder.d1.setTitle(u"ÅÄÖ")
        e.source = "foo@bar.be"
        e.recipients = "bar@foo.be"
        
        # Create some broken encodeness
        e.subject = u'Uusi diagnoosi t\xe4ytett\xe4v\xe4ksi: {{ title }}'
                        
        e.message = u"Päge '{{ text }}' with title {{ title }} created in {{ object_url }} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("bar@foo.be", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        
        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()        
        
        if messages:
            for m in messages: print str(m.message)
            
        # No template error messages
        self.assertEqual(len(messages), 0)          


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMailAction))
    return suite
