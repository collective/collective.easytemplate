"""

    Tags for outputting content data.

"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope import interface

from collective.templateengines.interfaces import *

from Products.LinguaPlone.interfaces import ITranslatable
from Products.LinguaPlone.browser.selector import TranslatableLanguageSelector

__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'epytext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

def getCurrentLanguage(context):
    # See plone.app.i18n.locales.browser.selector
    tool =  getToolByName(context, 'portal_languages', None)
    
    bound = tool.getLanguageBindings()
    current = bound[0]        
    return current

class CurrentLanguageTag(object):
    """ Return current active language. """

    interface.implements(ITag)
    
    def getName(self):
        return "current_language"
    
    def render(self, scriptingContext):
        
        # Get traversing context
        mappings = scriptingContext.getMappings()
        context = mappings["context"]
        request = mappings["request"]
        
        return getCurrentLanguage(context)
        
        
        
class TranslateTag(object):
    """ Look up values from translation dictionary.
        
    """
    
    interface.implements(ITag)
    
    def getName(self):
        return "translate"
    
    
    def render(self, scriptingContext, message, domain="plone", language=None, default=None):
        """             
        
        """

        # Get traversing context
        mappings = scriptingContext.getMappings()
        context = mappings["context"]
        request = mappings["request"]
        
        if language == None:
            language = getCurrentLanguage(context)
        
        tool = getToolByName(context, 'translation_service')        

        value = tool.utranslate(context=context, domain=domain, msgid=message, target_language=language, default=default)
        return value
        
        