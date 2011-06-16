"""

    Document which allows automatic template variables substitution.
    
    http://mfabrik.com
    
"""
__author__ = """Mikko Ohtamaa <mikko@mfabrik.com>"""
__docformat__ = 'epytext'
__copyright__ = "2009-2010 mFabrik Research Oy"
__license__ = "GPL 2"

import logging

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Products.Archetypes.atapi import *
from zope.interface import implements

from collective.templateengines.utils import log_messages

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema

from collective.easytemplate.config import *
from collective.easytemplate import interfaces
from collective.easytemplate.engine import getEngine, getTemplateContext
from collective.easytemplate.utils import outputTemplateErrors, logTemplateErrors


# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

from collective.easytemplate.messages import easytemplateMessageFactory

_ = easytemplateMessageFactory

logger = logging.getLogger("EasyTemplate")

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

   # 
   TextField('unfilteredTemplate',
        required = False,
        default = "",
        languageIndependent = False,
        schemata="Template",
        widget = TextAreaWidget(
            label= _(
                u"unfiltered_template_label", 
                default=u'Unfiltered template code'),
            description = _(
                u'unfiltered_template_description', 
                default=u'Edit template code here if you are working with raw HTML - otherwise WYSIWYG editor might scramble the result. Leave empty if normal WYSIWYG input is used.'),
            rows = 25
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
ERROR_MESSAGE = _("The page structure contains errors (template evalution failed or resulted to emptry string). Please contact the site manager. Content editors can see the error if they enable Catch errors checkbox on Edit > Template tab")

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
        
        # XXX: we cannot rely request being present
        outputTemplateErrors(messages, request=getattr(self, "REQUEST", None), logger=logger, context=self)
        
    def getTemplateSource(self):
        # Choose between normal kupu editor input
        # and unfiltered input
        unfiltered = self.getRawUnfilteredTemplate()
        if unfiltered != None and unfiltered.strip() != "":
            # We are using raw HTML input
            text = unfiltered.decode("utf-8")
        else:
            text = self.getRawText()
                        
        return text

    def compile(self, text):
        """ Compile the template. """
        engine = getEngine()
        
        if text == None:
            text = ""
                                             
        # TODO: Compile template only if the context has been changed           
        t, messages = engine.loadString(text, False)
        return t, messages
      

    security.declareProtected(View, 'getTemplatedText')
    def getTemplatedText(self):
        """ Cook the view mode output. """
        
        context = getTemplateContext(self)        
        
        text = self.getTemplateSource()
                
        t, messages = self.compile(text)
        
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
        
        # XXX 2011-06: latest hot fixes to portal_transforms screw this
        
        #transforms = getToolByName(self, 'portal_transforms')                
        #output = transforms.convertTo("text/html", output, context=self)
                                                                                                                                                    
        return unicode(output).encode("utf-8")

    security.declareProtected(View, 'getTemplatedText')    
    def testTemplate(self):
        """ Return template output without HTML transformations.
        
        Useful for template debugging.
        """
        
        context = getTemplateContext(self)        
        text = self.getTemplateSource()        
        t, messages = self.compile(text)            
        if len(messages) > 0:
            return str(messages)
        
        response = self.REQUEST.RESPONSE
        response.setHeader('Content-type', "text/plain")
        
        output, messages = t.evaluate(context)
        if len(messages) > 0:
            response.write(str(messages))
        else:
            response.write(str(output))
                                                    

registerType(TemplatedDocument, PROJECTNAME)
# end of class TemplatedDocument

##code-section module-footer #fill in your manual code here
##/code-section module-footer



