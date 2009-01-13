from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from Products.statusmessages.interfaces import IStatusMessage

from collective.easytemplate import tagconfig, engine
from collective.templateengines.backends import jinja

@onsetup
def setup_app():

    fiveconfigure.debug_mode = True
    import collective.easytemplate
    zcml.load_config('configure.zcml', collective.easytemplate)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    
    ztc.installPackage('collective.easytemplate')
    
# The order here is important.

setup_app()
ptc.setupPloneSite(products=['collective.easytemplate'])

class EasyTemplateTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

    def afterSetUp(self):
        # Might be another engine since some tests switch
        # this global variable
        engine.setDefaultEngine()

    def createContent(self):
        """ Create site content which is used in test cases. """
        self.loginAsPortalOwner()
        
        # Published folder
        self.portal.invokeFactory("Folder", "folder")
                
        # Published doc
        self.portal.folder.invokeFactory("Document", "doc")
        self.portal.folder.invokeFactory("Document", "doc_published")
        
        self.portal.folder.invokeFactory("TemplatedDocument", "easy_template")
        
        self.portal.folder.easy_template.setCatchErrors(True)
        
        self.portal.folder.doc_published.setTitle("Published Title")
        self.portal.folder.doc.setTitle("Unpublished")                
                
        self.portal.portal_workflow.doActionFor(self.portal.folder.doc_published, "publish")
        self.portal.portal_workflow.doActionFor(self.portal.folder.easy_template, "publish")
        self.portal.portal_workflow.doActionFor(self.portal.folder, "publish")
        self.logout()
    
    def runSnippet(self, str, admin=False, assumeErrors=False):
        """ Execute Jinja snippet in a secure context. 
        
        @param assumeErrors: There should be error output
        """
        doc = self.portal.folder.easy_template
        self.loginAsPortalOwner()
        doc.setText(str)
        
        if not admin:        
            self.logout()
            
        output = doc.getTemplatedText()
        messages = IStatusMessage(self.portal.REQUEST).showStatusMessages()        
        
        if messages:            
            for m in messages: 
                print "Template error:" + m.message
            
        if assumeErrors:
            # There should be no error messages
            self.assertNotEqual(len(messages), 0)
        else:
            self.assertEqual(len(messages), 0)
            
        return output    