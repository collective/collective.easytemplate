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

ERROR_MESSAGE = _("The page template code contains errors. Please see the error message from site setup -> error log.")

def outputTemplateErrors(messages, request=None, logger=None, context=None):
    """ Write template errors to the user as status messages and the log output. """
    
    # Show user status messages
    if request != None:
        for msg in messages:            
            if msg.getException():
                IStatusMessage(request).addStatusMessage(str(msg.getException()[0]), type="error")
            else:
                IStatusMessage(request).addStatusMessage(msg.getMessage(), type="error")
    
    # Write site error_log            
    if context != None:
        logTemplateErrors(context, messages)
    
    # Write python logging
    if logger != None:
        log_messages(logger, messages)        
    
    # Write stdout
    dump_messages(messages)
    
def logTemplateErrors(context, messages):
    """ Put template errors to site's error_log service.
    """
    
    class TemplateError(Exception):
        """ Dummy exception to used to wrap plain messages to exceptions """
        pass
    
    # Acquire error log tool from any context
    
    try:
        error_log = context.error_log
    except AttributeError, e:
        # Acquisition is not kicking in.... probably error happened during incomplete object creation
        # We have no other options but fail silently here 
        return

    for msg in messages:            
        if not msg.getException():
            
            # This is an error message without traceback
            # Wrap plain error messages to dummy exceptions
            
            try:
                raise TemplateError(msg.getMessage())
            except Exception, e:
                exception = e
        else:
            exception = msg.getException()

        error_log.raising(exception)
    
def applyTemplate(context, string, logger=None):
    """  Shortcut to run a string through our template engine.
    
    @param context: ITemplateContext
    @param string: Template as string
    
    @return: tuple (output as plain text, boolean had errors flag)
    """
    
    if logger:
        if string is not None:
            logger.debug("Applying template:" + string)
        else:
            logger.debug("Applying template:<empty string>")
        
    engine  = getEngine()
    
    # TODO: Assume Plone template context - should be an explict parameter?
    request = context.getMappings()["context"].REQUEST

    if string == None:
        string = ""

    # We might have unicode input data which 
    # will choke Cheetah/template engine
    
    string = string.encode("utf-8")
    
    errors=False
            
    # TODO: Compile template only if the context has been changed           
    t, messages = engine.loadString(string, False)
    outputTemplateErrors(messages, request=request, logger=logger, context=context)    
    errors |= len(messages) > 0
        
    output, messages = t.evaluate(context)    
    outputTemplateErrors(messages, request=request, logger=logger, context=context)
    errors |= len(messages) > 0
            
    return output, errors
            

def compile(text):
    """ Compile the template. """
    engine = getEngine()
    
    if text == None:
        text = ""
                                         
    # TODO: Compile template only if the context has been changed           
    t, messages = engine.loadString(text, False)
    return t, messages            

def cook(instance, request, text):
    """ Shortcut method to render a template.
    
    
    @param text: Templat text as unicode string
    """
    
    # expose_schema must be False, or we get recursive
    # loop here (expose schema tries to expose this field)
    context = getTemplateContext(instance, expose_schema=False)        
        
    t, messages = compile(text)        
        
    outputTemplateErrors(messages, instance)
    if t is None:            
        return ERROR_MESSAGE
        
    output, messages = t.evaluate(context)
    outputTemplateErrors(messages, request=request, context=instance)
    if output is None:
        return ERROR_MESSAGE            
    
    return unicode(output).encode("utf-8")    