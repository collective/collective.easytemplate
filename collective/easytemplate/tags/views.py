"""

    Tags for rendering viewlets and portlets inside the content text.
    
    httP://www.twinapex.com

"""

import Acquisition
import zope
from zope import interface
from zope.interface import providedBy

from zope.component import getUtility, getAdapters
from zope.component import getMultiAdapter, getSiteManager
from zope.component import getUtility, queryUtility
from zope.component import getSiteManager
from zope.component import adapts, queryMultiAdapter
from zope.contentprovider import interfaces as cp_interfaces

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.component.hooks import getSite
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getSiteManager, getAllUtilitiesRegisteredFor
from zope.viewlet import manager

from zope.viewlet.interfaces import IViewlet
from zope.contentprovider.interfaces import IContentProvider

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from plone.portlets.interfaces import IPortletManager, IPortletType, IPortletRenderer
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.browserlayer.interfaces import ILocalBrowserLayerType
from plone.app.customerize import registration

from collective.templateengines.interfaces import *

__author__ = """Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"""
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"

# Declare some dumminess to satisfy the complexty of viewlet management

class IDummyViewletManager(zope.viewlet.interfaces.IViewletManager):
    """ Refer to zope.viewlet README.txt """
    pass

class DummyContent:
    """ Refer to zope.viewlet README.txt """
    zope.interface.implements(zope.interface.Interface)

class DummyView(BrowserView):
    """ Refer to zope.viewlet README.txt """    
    
class DummyContent(object):
      zope.interface.implements(Interface)


class ViewTag(object):
    """ A tag to render a BrowserPage view by its id. 
        
    """

    interface.implements(ITag)
    
    def getName(self):
        return "view"

    def render(self, scriptingContext, name, function="__call__"):
        """
        """
        
        mappings = scriptingContext.getMappings()
        
        # Get traversing context
        context = mappings["context"]
        request = mappings["request"]
        
        view = queryMultiAdapter((context, request), name=name)
        
        if view == None:
            return u"[ No view " + unicode(name) + u" ]"
        
       
        if function == "__call__":        
            html = view()
            return html
        else:
            func = getattr(view, function)    
            return func()

      
class ViewletTag(object):
    """ A tag to render for a Plone viewlet. 
        
    """
    
    interface.implements(ITag)
    
    def getName(self):
        return "viewlet"
    
    def getLocalRegistrations(self, context):
        """ See plone.app.customerize.browser """
        layers = getAllUtilitiesRegisteredFor(ILocalBrowserLayerType)
        components = getSiteManager(context)
        for reg in components.registeredAdapters():
            if (len(reg.required) in (2, 4, 5) and
                   (reg.required[1].isOrExtends(IBrowserRequest) or
                    reg.required[1] in layers) and
                    ITTWViewTemplate.providedBy(reg.factory)):
                yield reg
    
        
    def getTemplateViewRegistrations(self, context):
        """ See plone.app.customerize.browser """
        regs = []
        local = {}
        for reg in self.getLocalRegistrations(context):
            local[(reg.required, str(reg.name), str(reg.factory.name))] = reg
        for reg in registration.templateViewRegistrations():
            lreg = local.get((reg.required, str(reg.name), str(reg.ptname)), None)
            if lreg is not None:
                regs.append(lreg)
            else:
                regs.append(reg)
        return registration.templateViewRegistrationGroups(regs)  

                
    def getViewFactoryFromViewName(self, context, request, viewname):
        """ Resolve view class by using Zope's component architecture.
        """
        view = getMultiAdapter((context, request), name=viewname)
        return view
    
    def getViewletByName(self, name):
        
        views = registration.getViews(IBrowserRequest)
        for v in views:
            if v.name == name: return v
        return None
               
    def render(self, scriptingContext, name):
        """     
        
        @param scriptingContext: Instance of collective.templateengines.interfaces.ITemplateContext
        """
        
        mappings = scriptingContext.getMappings()
        
        # Get traversing context
        context = mappings["context"]
        request = mappings["request"]
        
        # No idea what this does but big boys have
        # told that it might be required
            
        site = getSite()
        
        reg = self.getViewletByName(name)
        if reg == None:
            raise KeyError("Unknown viewlet: " + str(name))
        
        # See zope.viewlet README.txt how to wrap the viewlet                        
        content = DummyContent()
        view = DummyView(content, request)

        # Viewlet creation always nees a manager, create dummy one
        DummyManager = manager.ViewletManager('Easy Template dummy viewlet manager', IDummyViewletManager)
        dummy_manager = DummyManager(content, request, view)
        
        # Call viewlet factory to create a viewlet object for us
        view = reg.factory(context, request, view, dummy_manager)
        # Bring view to the acquisition chain
        # so that viewlet can access the acquired context variables
        view = view.__of__(context)
        
        view.update()
        return view.render()
        
class ProviderTag(object):
    """ Render content providers e.g. viewlet and portlet managers """
    
    interface.implements(ITag)
    
    def getName(self):
        return "provider"
    
    def render(self, scriptingContext, name, **kwargs):
        """
        
        The code is took from Products.five.browser.providerexpression.
                        
        @param scriptingContext: Instance of collective.templateengines.interfaces.ITemplateContext        
        """
        
        # Get traversing context
        mappings = scriptingContext.getMappings()
        context = mappings["context"]
        request = mappings["request"]
            
        class Dummy(BrowserView):
            pass
            
        context = context
        request = request
        view = Dummy(context, request)
        view = view.__of__(context)

        # Try to look up the provider.
        provider = zope.component.queryMultiAdapter(
            (context, request, view), cp_interfaces.IContentProvider, name)

        # Provide a useful error message, if the provider was not found.
        if provider is None:
            raise cp_interfaces.ContentProviderLookupError("Cannot find content provider:" + name)

        if getattr(provider, '__of__', None) is not None:
            provider = provider.__of__(context)

        # Stage 1: Do the state update.
        provider.update()

        # Stage 2: Render the HTML content.
        return provider.render()

class PortletTag(object):
    """ Render a portlet inside context text.
    
    TODO: Finish
        
    """
    
    interface.implements(ITag)    
    
    def getName(self):
        return "portlet"
    
    def render(self, scriptingContext, name, **kwargs):
        """
        
        Just too difficult.
                
        @param scriptingContext: Instance of collective.templateengines.interfaces.ITemplateContext        
        """
        
        # Get traversing context
        mappings = scriptingContext.getMappings()
        context = mappings["context"]
        request = mappings["request"]
        
        
        #manager = getUtility()
        #portletManager = getMultiAdapter((context, request), interface=IPortletManager)
        
        # For resolving logic, see plone.app.portlets.metaconfigure
        
        # First let's get PortletType
        #sm = getSiteManager()
        #type = None
        #for util in sm.registeredUtilities():                                        
        #    if util.name == name:  
        #        type = util
        #        break
                    
                
        #if type == None:
        #    raise KeyError("Portlet %s does not exist" % str(name))
        
        # It is freaking difficult 
        # to get portlet rendererer out of plone
        # due to engineered portlet manager
        # I spent few hours trying for nothing
        # I just freaking hate those multi-adapters
        # which have no sensible means shortcutting them
        # and needs crapload of dummy classes to squeeze
        # the answer out of pile of undebuggable adapter mappings
        # ugh
        

        # Map IPortletType to IPortlet interface
        #portlet = None
        #for util in sm.registeredUtilities():
        #    print str(util)
        #    print str(type)
        #    if util.component == type.component:
        #        portlet = util            
        #        break

        # Get renderer for IPortlet
        #from plone.app.portlets.metaconfigure import _default_renderers      
        #try:
        #    renderer = _default_renderers[portlet]
        #except KeyError:
        #    raise KeyError("Cannot get portlet renderer for portlet:" + str(portlet))
                    
        # We should have a renderer assigned for this interface
        #renderer = getMultiAdapter((context, request, , IPortletRenderer)
    
        #type_instance = type.factory()
                
                
        
        