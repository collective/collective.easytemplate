"""

    Templated content rule email send action for Plone.
    
"""
__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'plaintext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

import logging

from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, implements
from zope.formlib import form
from zope import schema

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode

from collective.easytemplate.config import *
from collective.easytemplate import interfaces
from collective.easytemplate.engine import getEngine, getTemplateContext


class IMailAction(Interface):
    """Definition of the configuration available for a mail action
    """
    subject = schema.TextLine(title=_(u"Subject"),
                              description=_(u"Subject of the message"),
                              required=True)
    source = schema.TextLine(title=_(u"Email source"),
                             description=_("The email address that sends the \
email. If no email is provided here, it will use the portal from address."),
                             required=False)
    recipients = schema.TextLine(title=_(u"Email recipients"),
                                description=_("The email where you want to \
send this message. To send it to different email addresses, just separate them\
 with ,"),
                                required=True)
    message = schema.Text(title=_(u"Message"),
                          description=_(u"Type in here the message that you \
want to mail. Some defined content can be replaced: ${title} will be replaced \
by the title of the item. ${url} will be replaced by the URL of the item."),
                          required=True)

class MailAction(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IMailAction, IRuleElementData)

    subject = u''
    source = u''
    recipients = u''
    message = u''

    element = 'plone.actions.TemplatedMail'

    @property
    def summary(self):
        return _(u"Email report to ${recipients}",
                 mapping=dict(recipients=self.recipients))


class MailActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IMailAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event
        
    def outputTemplateErrors(self, messages):
        """ Write template errors to the user and the log output. """
        
        logger = logging.getLogger("Plone")
            
        for msg in messages:            
            IStatusMessage(self.REQUEST).addStatusMessage(msg.getMessage(), type="error")
            
        log_messages(logger, messages)        
        
    def applyTemplate(self, context, string):
        """  Shortcut to run a string through our template engine.
        """
        engine  = getEngine()
        logger = logging.getLogger("Plone")
                
        # TODO: Compile template only if the context has been changed           
        t, messages = engine.loadString(text, False)
        self.outputTemplateErrors(messages)
            
        output, messages = t.evaluate(context)
        self.outputTemplateErrors(messages)
        
        return  output
        

    def __call__(self):
                
        context = obj = self.event.object
        templateContext = getTemplateContext(context)
                
        recipents = self.applyTemplate(templateContext, self.element.recipents)
        
        recipients = [str(mail.strip()) for mail in \
                      self.element.recipients.split(',')]
        
        mailhost = getToolByName(aq_inner(self.context), "MailHost")
        if not mailhost:
            raise ComponentLookupError, 'You must have a Mailhost utility to \
execute this action'

        source = self.element.source
        urltool = getToolByName(aq_inner(self.context), "portal_url")
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')
        if not source:
            # no source provided, looking for the site wide from email
            # address
            from_address = portal.getProperty('email_from_address')
            if not from_address:
                raise ValueError, 'You must provide a source address for this \
action or enter an email in the portal properties'
            from_name = portal.getProperty('email_from_name')
            source = "%s <%s>" % (from_name, from_address)
            
        source = self.applyTemplate(templateContext, self.element.recipents)
        message = self.applyTemplate(templateContext, self.element.message)
        subject = self.applyTemplate(templateContext, self.element.subject)
        
        for email_recipient in recipients:
            mailhost.secureSend(message, email_recipient, source,
                                subject=subject, subtype='plain',
                                charset=email_charset, debug=False,
                                From=source)
        return True

class MailAddForm(AddForm):
    """
    An add form for the mail action
    """
    form_fields = form.FormFields(IMailAction)
    label = _(u"Add Templated Mail Action")
    description = _(u"Email using template variables.")
    form_name = _(u"Configure element")

    def create(self, data):
        a = MailAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class MailEditForm(EditForm):
    """
    An edit form for the mail action
    """
    form_fields = form.FormFields(IMailAction)
    label = _(u"Edit Templated Mail Action")
    description = _(u"Email using template variables.")
    form_name = _(u"Configure element")
