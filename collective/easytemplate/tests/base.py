from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

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
