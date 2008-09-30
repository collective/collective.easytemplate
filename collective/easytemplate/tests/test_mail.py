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

class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object

class DummySecureMailHost(SecureMailHost):
    meta_type = 'Dummy secure Mail Host'
    def __init__(self, id):
        self.id = id
        self.sent = []

    def _send(self, mfrom, mto, messageText, debug=False):
        self.sent.append(messageText)

class TestMailAction(EasyTemplateTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', 'target')
        self.folder.invokeFactory('Document', 'd1',
            title=unicode('Wälkommen', 'utf-8'))

    def testRegistered(self):
        element = getUtility(IRuleAction, name='collective.easytemplate.actions.Mail')
        self.assertEquals('collective.easytemplate.actions.Mail', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testExecute(self):
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailAction()
        e.source = "foo@bar.be"
        e.recipients = "bar@foo.be"
        e.message = u"Päge '${text}' with title ${title} created in ${object_url} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("bar@foo.be", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertEqual("P\xc3\xa4ge 'W\xc3\xa4lkommen' created in \
http://nohost/plone/Members/test_user_1_/d1 !",
                         mailSent.get_payload(decode=True))
        
    def testExecuteSyntaxError(self):
        pass

    def testExecuteNoSource(self):
        """ Template contains syntax errors, we should receive status messages. """
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailAction()
        e.recipients = 'bar@foo.be,foo@bar.be'
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        self.assertRaises(ValueError, ex)
        # if we provide a site mail address this won't fail anymore
        sm.manage_changeProperties({'email_from_address': 'manager@portal.be'})
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("bar@foo.be", mailSent.get('To'))
        self.assertEqual("Site Administrator <manager@portal.be>",
                         mailSent.get('From'))
        self.assertEqual("Document created !",
                         mailSent.get_payload(decode=True))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMailAction))
    return suite
