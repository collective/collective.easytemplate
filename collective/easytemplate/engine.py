"""

    Helper functions.

"""
__author__ = "Mikko Ohtamaa <mikko@redinnovation.com>"
__copyright__ = "2008 Red Innovation Oy"
__license__ = "GPL"
__docformat__ = "epytext"


from collective.templateengines.backends import cheetah
from collective.templateengines.context.plone import ArchetypesSecureContext

from collective.easytemplate import tagconfig

def getEngine():
    """ Get used template engine. """
    
    # TODO: Hardcoded for now
    return cheetah.Engine()

def getTemplateContext(context):
    """ Return context variables available for AT objects.
    
    TODO: Respect field access rights
    
    @param context: Archetypes object
    """
    
    context = ArchetypesSecureContext(context)
    
    # Register custpom
    for tag, obj in tagconfig.tags.items():
        context.addMapping(tag, obj)        
    return context
