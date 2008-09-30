"""

    Document which allows automatic template variables substitution.
    
"""
__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'plaintext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

import logging

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Products.Archetypes.atapi import *
from zope.interface import implements

from collective.templateengines.utils import log_messages

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema

from collective.easytemplate.config import *
from collective.easytemplate import interfaces
from collective.easytemplate.engine import getEngine, getTemplateContext

from zope.i18nmessageid import MessageFactory
# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

easytemplateMessageFactory = MessageFactory('collective.easytemplate')
_ = easytemplateMessageFactory

schema = Schema((
    BooleanField('catchErrors',
        required = False,
        default = False,
        languageIndependent = True,
        schemata="Template",
        widget = BooleanWidget(
            label= _(
                u'help_catch_errors', 
                default=u'Catch errors'),
            description = _(
                u'help_catch_errors_description', 
                default=u'If selected, template errors will provide debugging output.')
            ),
        ),
    ),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

TemplatedDocument_schema = ATDocumentSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
# Patch schema to use our accessor
TemplatedDocument_schema["text"].accessor = "getTemplatedText"
TemplatedDocument_schema["text"].widget.label = "Text (templated)"
TemplatedDocument_schema["text"].widget.description = "This document view supports automatic text substitutions. For available substitutions, please contact your site administration."
#TemplatedDocument_schema["text"].
##/code-section after-schema


# Display this text instead of content if there are errors 
ERROR_MESSAGE = _("The page structure contains errors. Please contact the site manager. Content editors can see the error if they enable Catch errors checkbox on Edit > Template tab")

class TemplatedDocument(ATDocument):
    """ A page allowing Cheetah template tags in Kupu text.
    """
    security = ClassSecurityInfo()

    implements(interfaces.ITemplatedDocument)

    meta_type = 'TemplatedDocument'
    _at_rename_after_creation = True

    schema = TemplatedDocument_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header
    
    
    def outputTemplateErrors(self, messages):
        """ Write template errors to the user and the log output. """    
        logger = logging.getLogger("Plone")
        
        if self.getCatchErrors():
            for msg in messages:            
                IStatusMessage(self.REQUEST).addStatusMessage(msg.getMessage(), type="error")
            
        log_messages(logger, messages)
                

    # Methods
    security.declareProtected(View, 'getTemplatedText')
    def getTemplatedText(self):
        """ Cook the templated text. """
        
        text = self.getRawText()
        
        engine = getEngine()
        context = getTemplateContext(self)
        
        if text == None:
            text = ""
                                             
        # TODO: Compile template only if the context has been changed           
        t, messages = engine.loadString(text, False)
        self.outputTemplateErrors(messages)
        if not t:            
            return ERROR_MESSAGE
            
        output, messages = t.evaluate(context)
        self.outputTemplateErrors(messages)
        if not output:
            return ERROR_MESSAGE            
        
        # TODO: Didn't find instructions how this should be really done
        # I am not going to spent another night going through
        # piles of old undocumented codebase to figure this out.
        # I so hate Plone.
        transforms = getToolByName(self, 'portal_transforms')
        output = transforms.convertTo("text/x-html-safe", output)
                                                                                    
        return str(output)
            
                                                    

registerType(TemplatedDocument, PROJECTNAME)
# end of class TemplatedDocument

##code-section module-footer #fill in your manual code here
##/code-section module-footer



