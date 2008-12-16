"""

    Tags for adding different folder lists.

"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'epytext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

def list_folder(folder, title=None, exclude_self=True, extra_items="", filters={}):
    """ List folder contents as bulleted link list. 
    
    @param folder: slashed path to the folder on the site, starting from the site root. No initial slash.
    @param title: optional <h3> level subheading which is shown if the folder contains at least one item
    @param filter: optional content type mask. only this type of content items is shown.
    @param exclude_self: Do not list the current context
    @param extra_items: Comma separated list of item absolute paths which lie outside the target folder, but should be included in the listing
    """
    context = list_folder.namespace["context"]
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


pick_content_template = ViewPageTemplateFile("pick_content.pt")

def pick_content(content_type, count=3, show_title=True, show_description=True):
    """ Create content pick ups. 
    
    Pick content from the site, sorted by newest first. 

    Generate list with title,acting as a link, and description.
    """
    
    pick_content_template()
    
    