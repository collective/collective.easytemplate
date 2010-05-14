"""

    Kupu editable HTML portlet which takes in template tags.
    
    http://www.redinnovation.com
    
"""
__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'epytext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"


import logging
import types

from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getUtility
from zope import schema
from zope.formlib import form


from plone.app.portlets.portlets import base

from plone.portlet.static import static 
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

from interfaces import ITemplatedPortlet
from collective.easytemplate.utils import applyTemplate
from collective.easytemplate.engine import getEngine, getTemplateContext

from collective.easytemplate.utils import outputTemplateErrors 

from collective.templateengines.utils import Message

# TODO: Fix to use own message factory
from plone.portlet.static.static import _

from Products.CMFCore.Expression import Expression, getExprContext

logger = logging.getLogger("Plone")

class TemplatedPortletRenderer(static.Renderer):
    """ Overrides static.pt in the rendering of the portlet. """
    
    template = ViewPageTemplateFile('templated_portlet.pt')
    
    def outputTemplateErrors(self, messages):
        """ Write template errors to the user and the log output. """    
        
        logTemplateErrors(self, messages)
        
    def getTemplateContext(self):
        
        # Portlet might be assigned to non
        return getTemplateContext(self.context, expose_schema=False)
    
    def getHeader(self):
        """ Get cooked portlet title.
        """
        context = self.getTemplateContext()
        header = self.data.header
        header, errors = applyTemplate(context, header, logger)
        
        if errors:
            return "Errors"
        else:
            return header
        
    def getBody(self):
        """ Get cooked portlet body. """
        context = self.getTemplateContext()
        text = self.data.text
        text, errors = applyTemplate(context, text, logger)
        
        if errors:
            # TODO: Handle errors gracefully
            return "Template contains errors. Please see the log."
        else:
            logger.debug("Got:" + text)
            return text
        
    def render(self):
        """ Render the portlet if expression is evaluated succesfully.
        
        """
        
        #context = aq_inner(self.context)
        context = self.context
        expression_context = getExprContext(context)
        
        condition_value = True
        
        # Determine expression value in backwards compatible
        # manner    
        expression = self.data._expression_object
        
        if expression:
            
            try:        
                condition_value = expression(expression_context)
                
                if type(condition_value) in types.StringTypes:
                    if condition_value.strip() == u"":
                        # Emptry value evaluates to true
                        condition_value = True
                
            except Exception, e:
                # Log and output exception in user friendly
                # manner without interrupting the page rendering
                foobar, messages = Message.wrapCurrentException()
                outputTemplateErrors(messages, request=self.request, logger=logger, context=context)
                condition_value = False
                
        else:            
            # Migrated TemplatedPortlet assignment which has been never save
            # after upgrading to version 0.7.4
            condition_value = True
            
        if condition_value:
            return self.template()
        else:
            # Hide portlet
            return ""
        
        
    
class TemplatedPortletAssignment(static.Assignment):
    """ Assigner for templated portlet. """
    implements(ITemplatedPortlet)
    
    # Store compiled expression persistently with
    # the portlet to optimize the expression evaluation speed
    _expression_object = None
    
    # Backwards compatibility support -
    # if object lacks expression attribute this one is used
    expression = None
    
    def __init__(self, header=u"", text=u"", omit_border=False, footer=u"",
                 more_url='', hide=False, expression=""):
        self.header = header
        self.text = text
        self.omit_border = omit_border
        self.footer = footer
        self.more_url = more_url
        self.hide = hide
        self.expression = expression
                    
    def _set_expression(self, value):
        
        # Set the user editable text
        self._expression = value
        
        # Create Expression object based on this text
        self._expression_object = value and Expression(value)
        
    def _get_expression(self):
        return self._expression
            
    # expression accessor which manages Expression objects as well
    expression = property(_get_expression, _set_expression) 
    
class TemplatedPortletAddForm(static.AddForm):
    """ Make sure that add form creates instances of our custom portlet instead of the base class portlet. """
    
    label = _(u"title_add_templated_portlet",
              default=u"Add templated text portlet")
    
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display HTML text with dynamic tags")
    
    
    def create(self, data):
        return TemplatedPortletAssignment(**data)    
    
class TemplatedPortletEditForm(static.EditForm):
    """ Edit view for templated portlet. """
    form_fields = form.Fields(ITemplatedPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    label = _(u"title_edit_static_portlet",
              default=u"Edit templated text portlet")
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display HTML text with dynamic tags.")

    
    