"""

    Tags for outputting content data.

"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from zope import interface

from collective.templateengines.interfaces import *
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'epytext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

class ListFolder:

    interface.implements(ITag)
    
    def getName(self):
        return "list_folder"
    
    def render(self, context, folder, title=None, exclude_self=True, extra_items="", filters={}):
        """ List folder contents as bulleted link list. 
        
        @param context: ITemplateContext object
        
        @param folder: slashed path to the folder on the site, starting from the site root. No initial slash.
        @param title: optional <h3> level subheading which is shown if the folder contains at least one item
        @param filter: optional content type mask. only this type of content items is shown.
        @param exclude_self: Do not list the current context
        @param extra_items: Comma separated list of item absolute paths which lie outside the target folder, but should be included in the listing
        """
        
        # Get zope traversing context - don't confuse these two!
        context = context.getTraversingContext()
        
        # you know some object which is refered as "context"
        portal_url = getToolByName(context, "portal_url")
        portal_catalog = getToolByName(context, "portal_catalog")
        portal = portal_url.getPortalObject()
        mtool = getToolByName(context, "portal_membership") 
        
        def sanify_path(path):
            if path.startswith("/"):
                path = path[1:]
            return portal_url.getPortalPath() + "/" + path
            
        path = sanify_path(folder) 
        # Get access to the folder object using slash notation
        #folder=portal.restrictedTraverse()
                    
        search_dict = {
            "path" : { "query" : path, "depth" : 1 }
        }
        
        search_dict.update(filters)
            
        # Editors should be able to list items which are not yet publicly visible
        show_inactive = mtool.checkPermission('Access inactive portal content', context)        
        items = portal_catalog.queryCatalog(search_dict, show_inactive=show_inactive)
        
        if extra_items != "":
            extra_items = extra_items.split(" ,")
            
            items = list(items)
        
            for extra in extra_items:
                
                if extra == "":
                    # Skip stale etnries
                    continue
                
                # And then they wanted exception to the rule...
                path = sanify_path(extra)
                query = {
                         "path" : { "query" : path, "depth" : 0 }
                }     
                extra = portal_catalog.queryCatalog(query)
                items += list(extra)
        
        # Generate HTML snippets directly into a Python string
        output = ""
            
        if len(items) > 0:
            if title:
                output += "<h3>" + title + "</h3>"
                 
        output += """<ul class="folder-list">"""
        
        for item in items:
            if exclude_self and item.getURL() == context.absolute_url():
                continue
            output += """<li><a href="%s">%s</a></li>""" % (item.getURL(), item["Title"])
            
        output += """</ul>"""
        return output
    
    def __call__(self, *args, **kwargs):
        raise RuntimeError("Deprecated - TagProxy should call render() method")
    
    
class QueryTag(object):
    """ Perform portal_catalog search query and return results.
        
    """
    
    interface.implements(ITag)
    
    def getName(self):
        return "query"
    
    def render(self, scriptingContext, searchParameters):
        """     
        
        @param searchParameters: Dictionary of portal_catalog query parameters
        @param scriptingContext: Instance of collective.templateengines.interfaces.ITemplateContext
        @return: Raw catalog brains objects
        """
        
        mappings = scriptingContext.getMappings()
        
        # Get traversing context
        context = mappings["context"]
        request = mappings["request"]    
        
        portal_catalog = getToolByName(context, "portal_catalog")
        return portal_catalog.queryCatalog(searchParameters)
    
    
class ExploreTag(object):
    """ Dump object developer info.
        
    """
    
    interface.implements(ITag)
    
    def getName(self):
        return "explore"
    
    def renderObject(self, object, pp, buffer):
        print >> buffer, '<table class="object-explore">'
        print >> buffer, "<thead>"
        print >> buffer, "<tr>"
        print >> buffer, "<th>Attribute name</th>"        
        print >> buffer, "<th>Value</th>"        
        print >> buffer, "</tr>"        
        
        def do_obj(key, value):
            print >> buffer, "<tr>"
            print >> buffer, "<td>"            
            print >> buffer, str(key)
            print >> buffer, "</td>"           
            
            print >> buffer, "<td>"            
            pp.pprint(value)
            print >> buffer, "</td>"
            print >> buffer, "</tr>"            
            
        # Outputters, most specialized firsh
        if isinstance(object, AbstractCatalogBrain):
            # Zope catalog brain objects need special keying
            for key in object.__record_schema__.keys():
                value = object[key]
                do_obj(key, value)
        elif hasattr(object, "__dict__"):        
            for key, value in object.__dict__.items():
                do_obj(key, value)
        elif type(object) == type({}):
            for key, value in object.items():
                do_obj(key, value)            
        elif type(object) == type([]) or type(object) == type(()):
            # List & sequence
            for i in range(0, len(object)):
                self.do_obj(i, object[i])                            
        else:
            do_obj("Object", object)

        print >> buffer, "</tbody>"
        print >> buffer, "</table>"        
    
    def render(self, scriptingContext, object):
        """             
        Use Python PrettyPrinter to dump objects 
        to HTML table.
        """

        import pprint
        import StringIO
        buffer = StringIO.StringIO()
        pp = pprint.PrettyPrinter(indent=4, depth=3, stream=buffer)
        self.renderObject(object, pp, buffer)        
        return buffer.getvalue()
    
    
class LatestNewsView(BrowserView):
    
    index = ViewPageTemplateFile("latest_news.pt")
    
    def __call__(self):
        self.news_items = self.context.portal_catalog.queryCatalog({"portal_type":"News Item","sort_on":"Date","sort_order":"reverse","sort_limit":self.count,"review_state":"published"})
        return self.index()

class LatestNewsTag(object):
    """ Render latest news items """
    
    interface.implements(ITag)
    
    def getName(self):
        return "latest_news"

    def render(self, scriptingContext, count=3):
                
        mappings = scriptingContext.getMappings()
        
        # Get traversing context
        context = mappings["context"]
        request = mappings["request"]
                
        view = LatestNewsView(context, request)
        view.count = count
        # Put view into context acquistion chain
        view = view.__of__(context)
        
        return view()
    
    
    