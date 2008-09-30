# -*- coding: utf-8 -*-

from zope.interface import Interface

##code-section HEAD
##/code-section HEAD

class ITemplatedDocument(Interface):
    """Marker interface for .TemplatedDocument.TemplatedDocument
    """
    
class ITEmplateContext(Interface):
    """ Hold information about variables exposed to the template language. """
    
    def getAsMapping():
        """ Return exposed variables as a dictionary. """
    
class ITemplateLanguageEngine(Interface):
    
    def makeTemplateFromString(s):
        """
        @param s: Template source code as string
        @return (ITemplate, sequence of ITEmplateMessages)
        """
        
class ITemplate(Interface):
    """ Holds one template.
    
    Template can be string/file sourced and processed.
    """
    
    def execute(context):
        """ 
        @param context: ITemplateContext object
        @return: (evaluation result as string, sequence of ITEmplateMessages)
        """

##code-section FOOT
##/code-section FOOT