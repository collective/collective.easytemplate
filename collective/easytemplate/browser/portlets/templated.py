"""

    Kupu editable HTML portlet which takes in template tags.
    
    http://www.redinnovation.com
    
"""
__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'epytext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"


import logging

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

# TODO: Fix to use own message factory
from plone.portlet.static.static import _

logger = logging.getLogger("Plone")

class TemplatedPortletRenderer(static.Renderer):
    """ Overrides static.pt in the rendering of the portlet. """
    
    def getTemplateContext(self):
        return getTemplateContext(self.context)
    
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
            return "Errors"
        else:
            logger.debug("Got:" + text)
            return text
            
    render = ViewPageTemplateFile('templated_portlet.pt')
    
class TemplatedPortletAssignment(static.Assignment):
    """ Assigner for templated portlet. """
    implements(ITemplatedPortlet)
    
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

    
    