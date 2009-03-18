"""

    Common helper functions.
    
    http://www.redinnovation.com
    
"""
__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'plaintext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage

from collective.templateengines.utils import log_messages, dump_messages
from collective.easytemplate.config import *
from collective.easytemplate import interfaces
from collective.easytemplate.engine import getEngine, getTemplateContext


def outputTemplateErrors(messages, request=None, logger=None):
    """ Write template errors to the user as status messages and the log output. """
    
    if request != None:
        for msg in messages:            
            if msg.getException():
                IStatusMessage(request).addStatusMessage(str(msg.getException()[0]), type="error")
            else:
                IStatusMessage(request).addStatusMessage(msg.getMessage(), type="error")
    
    if logger != None:
        log_messages(logger, messages)        
        
    dump_messages(messages)
            
    
def applyTemplate(context, string, logger=None):
    """  Shortcut to run a string through our template engine.
    
    @param context: ITemplateContext
    @param string: Template as string
    
    @return: tuple (output as plain text, boolean had errors flag)
    """
    
    if logger:
        logger.debug("Applying template:" + string)
        
    engine  = getEngine()
    
    # TODO: Assume Plone template context - should be an explict parameter?
    request = context.getMappings()["context"].REQUEST

    # We might have unicode input data which 
    # will choke Cheetah/template engine
    string = string.encode("utf-8")
    
    errors=False
            
    # TODO: Compile template only if the context has been changed           
    t, messages = engine.loadString(string, False)
    outputTemplateErrors(messages, request=request, logger=logger)    
    
    errors |= len(messages) > 0
        
    output, messages = t.evaluate(context)
    outputTemplateErrors(messages, request=request, logger=logger)        
    errors |= len(messages) > 0
            
    return output, errors
            