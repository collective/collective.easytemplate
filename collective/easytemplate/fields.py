"""
    Field definitions.
    
    http://www.twinapex.com
                
"""

__author__  = 'Mikko Ohtamaa <mikko@redinnovation.com>'
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__licence__ = "GPL v2"

# Python imports
import logging
from types import DictType, FileType, StringType, UnicodeType, ListType, TupleType

# Zope imports
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent

# Plone imports
from Products.Archetypes.Widget import SelectionWidget
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.debug import log
from Products.Archetypes.utils import className, unique, capitalize
from Products.Archetypes.Field import TextField, ObjectField, encode, decode, registerField

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression, createExprContext
from Products.generator.widget import macrowidget

from collective.easytemplate.config import *
from collective.easytemplate import interfaces
from collective.easytemplate.engine import getEngine, getTemplateContext
from collective.easytemplate.utils import outputTemplateErrors, logTemplateErrors
from collective.easytemplate.messages import easytemplateMessageFactory as _

logger = logging.getLogger("EasyTemplate")

ERROR_MESSAGE = _("The page template code contains errors. Please see the error message from site setup -> error log.")

class TemplatedTextField(TextField):
    """ Field which does not store any value. Can be used as a place holder.
    """
    _properties = TextField._properties.copy()
    
    security = ClassSecurityInfo()

    def outputTemplateErrors(self, instance, messages):
        """ Write template errors to the user and the log output. """            
        outputTemplateErrors(messages, request=instance.REQUEST, logger=logger, context=instance)        
        
    def compile(self, text):
        """ Compile the template. """
        engine = getEngine()
        
        if text == None:
            text = ""
                                             
        # TODO: Compile template only if the context has been changed           
        t, messages = engine.loadString(text, False)
        return t, messages
                  
    def _getCooked(self, instance, text):
        """ Cook the view mode output. """
        
        
        # Convert all template code to unicode first
        if type(text) == str:
            text = text.decode("utf-8")
        
        # expose_schema must be False, or we get recursive
        # loop here (expose schema tries to expose this field)
        context = getTemplateContext(instance, expose_schema=False)        
            
        t, messages = self.compile(text)        
        
        self.outputTemplateErrors(instance, messages)
        if t is None:            
            return ERROR_MESSAGE
            
        output, messages = t.evaluate(context)
        self.outputTemplateErrors(instance, messages)
        if output is None:
            return ERROR_MESSAGE            
        
        return unicode(output).encode("utf-8")
        
    def get(self, instance, **kwargs):        
        """ Define view mode accessor for the widget """                
            
        text = TextField.get(self, instance, **kwargs)
            
        raw = kwargs.get("raw", False)
        
        if raw:
            return text
        else:
            return self._getCooked(instance, text)
    


registerField(TemplatedTextField,
              title='TemplatedTextField',
              description=('A place holder field without value storing'))

    

