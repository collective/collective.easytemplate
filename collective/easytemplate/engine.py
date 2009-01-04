"""

    Helper functions.

"""
__author__ = "Mikko Ohtamaa <mikko@redinnovation.com>"
__copyright__ = "2008 Red Innovation Oy"
__license__ = "GPL"
__docformat__ = "epytext"

from collective.templateengines.context.plone import ArchetypesSecureContext
from collective.templateengines.backends import jinja
from collective.templateengines.context import jinjazope

from collective.templateengines.utils import Message

from collective.easytemplate import tagconfig

_engine = None

def getEngine():
    """ Get used template engine. """
    global _engine 
    return _engine

def setupEngine(instance):
    """ Switch to a new global template engine. """
    
    global _engine 
    
    for tag in tagconfig.tags:
        instance.addTag(tag)

    _engine = instance
    
def getTemplateContext(context):
    """ Return context variables available for AT objects.
    
    TODO: Respect field access rights
    
    @param context: Archetypes object
    """
    
    context = ArchetypesSecureContext(context)
    
    # Tags are registered at teh engine level
    return context


def setDefaultEngine():    
    """ Set a Zope sandboxed Jinja execution environment """
    # TODO - hard dependency to Jinja - remove
    # Currently active global engine
    _engine = setupEngine(jinja.Engine(env=jinjazope.ZopeSandbox()))
    
    import AccessControl
    unauthorized = AccessControl.unauthorized.Unauthorized
    if not unauthorized in Message.unwrappableExceptions:
        Message.unwrappableExceptions.append(unauthorized)
    
setDefaultEngine()

