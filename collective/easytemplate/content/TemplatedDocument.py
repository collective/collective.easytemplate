"""

    Document which allows automatic template variables substitution.
    
"""
__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'plaintext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

from Cheetah.Template import Template
from Cheetah.ErrorCatchers import ListErrors

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Products.Archetypes.atapi import *
from zope.interface import implements

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from collective.easytemplate.config import *
from collective.easytemplate import tagconfig
from collective.easytemplate import interfaces

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
##/code-section after-schema



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

    # Methods
    security.declareProtected(View, 'getTemplatedText')
    def getTemplatedText(self):
        """ Cook the template text. """
        
        text = ATDocument.getText(self)
        
        class StatusMessageErrorCatcher(ListErrors):
            """ Make Cheetah errors user visible. """
            pass
        
        # Execute the function in a new security context.
                        
        try:
            
            self.plone_log(str(self.Title))
                            
            if self.getCatchErrors():
                t = Template(text, searchList = self.getNamespace())
                catcher = StatusMessageErrorCatcher(t)        
                output = str(t)
                
                request = self.REQUEST
                for error in catcher.listErrors():
                    IStatusMessage(request).addStatusMessage(error, type="error")
            else:
                t = Template(text, searchList = self.getNamespace())

            security=getSecurityManager()
            security.addContext(self)            
            try:
                output = str(t)
            finally:
                security.removeContext(self)
            
            return output
        except Exception, e:
            # Error which was not managed by by Cheetah error catcher
            from logging import getLogger
            log = getLogger('Plone')
            
            # Full traceback to logs
            log.exception(e)
                
            # User visible error message
            if self.getCatchErrors():
                request = self.REQUEST                
                IStatusMessage(request).addStatusMessage(str(e), type="error")
            
            return _("The page structure contains errors. Please contact the site manager. Content editors can see the error if they enable Catch errors checkbox on Edit > Template tab")
                                            
      
        
        
    def getNamespace(self):
        """ Return context variables available in Cheetah template. """
        
        
        security=getSecurityManager()
        
        namespace = {
            "context" : self,
            "portal_url" : getToolByName(self, 'portal_url'),
            "user" : security.getUser(),
            "request" : self.REQUEST
        }
        
        # TODO: Temporary hack
        # We add namespace directly as a function attribute, 
        # so that it is accessible in the function without
        # explitcly passing it there. There must be a smarter
        # way to do this, but Cheetag docs didn't tell it.
        # This is not threadsafe, but Zope doesn't use threads...        
        for func in tagconfig.tags.values():
            func.namespace = namespace
        
        namespace.update(tagconfig.tags)
        
        return namespace

registerType(TemplatedDocument, PROJECTNAME)
# end of class TemplatedDocument

##code-section module-footer #fill in your manual code here
##/code-section module-footer



