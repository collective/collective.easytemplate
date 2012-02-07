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
from Products.statusmessages.interfaces import IStatusMessage

from collective.templateengines.utils import log_messages
from collective.easytemplate.utils import outputTemplateErrors, applyTemplate
from collective.easytemplate.engine import getEngine, getTemplateContext

logger = logging.getLogger("Plone")

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
want to mail."),
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

    element = 'collective.easytemplate.actions.Mail'

    @property
    def summary(self):
        return _(u"Email report to ${recipients}",
                 mapping=dict(recipients=self.recipients))


class MailActionExecutor(object):
    """The executor for this action.
    
    If there are template errors the execution is aborted before send mail is called.
    """
    implements(IExecutable)
    adapts(Interface, IMailAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event
        self.templateErrors = False
        
        
    def sanify_encoding(self, string):
        """ Make suret that if we have utf-8 strings as unicode they will be properly decoded.
        
        If you put unicode letters to GenericSetup XML they are not necessarily properly translated
        to unicode characters, but broken encoding ensures::
        
            u"Uusi diagnoosi t\xe4ytett\xe4v\xe4ksi: {{ title }}"
        
        """
        try:
            string = string.decode("utf-8")
            return string
        except:
            return string
                
    def __call__(self):
                        
        context = obj = self.event.object
        templateContext = getTemplateContext(context)
        
        # Flag if we have errors from any template formatter
        any_errors = False
            
        recipients, errors = applyTemplate(templateContext, self.element.recipients, logger=logger)
        any_errors |= errors
        if recipients == None:
            raise ValueError("Bad recipients value:" + str(self.element.recipients.encode("utf-8")))
            
        emails = recipients.strip().split(",")
        emails = [ email for email in emails if (email != None and email != '')]                
        recipients = [str(email.strip()) for email in emails]
        
        mailhost = getToolByName(aq_inner(self.context), "MailHost")
        if not mailhost:
            raise ComponentLookupError('You must have a Mailhost utility to execute this action')
        
        source = self.element.source
        source, errors = applyTemplate(templateContext, source, logger=logger)
        any_errors |= errors        
        
        urltool = getToolByName(aq_inner(self.context), "portal_url")
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')
        
        if not source or len(source) == 0:
            # no source provided, looking for the site wide from email
            # address
            from_address = portal.getProperty('email_from_address')
            if not from_address:
                raise ValueError, 'You must provide a source address for this \
action or enter an email in the portal properties'
            from_name = portal.getProperty('email_from_name')
            source = "%s <%s>" % (from_name, from_address)

        message, errors = applyTemplate(templateContext, self.element.message, logger=logger)
        any_errors |= errors
        
        #subject_source = self.sanify_encoding(self.element.subject)
        subject_source = self.element.subject

        subject, errors = applyTemplate(templateContext, subject_source, logger=logger)
        any_errors |= errors
        

        
        # TODO: Should these to be added to status messaegs
        if len(recipients) == 0:
            raise ValueError("Recipients could not be defined from template:" + self.element.recipients.encode("utf-8"))

        if subject == None or len(subject) == 0:            
            raise ValueError("Subject could not be defined from template:" + self.element.subject.encode("utf-8"))

        if source == None or len(source) == 0:
            raise ValueError("Source could not be defined from template:" + self.element.source.encode("utf-8"))

        if any_errors:
            # These has been outputted already above
            return
        
        for email_recipient in recipients:
            
            assert len(email_recipient.strip()) > 0, "Email recipient is empty, all recipients:" + str(recipients)

            mailhost.secureSend(message, email_recipient, source,
                                subject=subject, subtype='plain',
                                charset=email_charset, debug=False)

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
