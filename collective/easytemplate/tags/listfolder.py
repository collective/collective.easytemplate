"""

    Tags for adding different folder lists.

"""

from Products.CMFCore.utils import getToolByName

__author__ = """Mikko Ohtamaa <mikko@redinnovation.com>"""
__docformat__ = 'epytext'
__copyright__ = "2008 Red Innovation Ltd."
__license__ = "GPL"

def list_folder(folder, title=None, exclude_self=True, filters={}):
    """ List folder contents as bulleted link list. 
    
    @param folder: slashed path to the folder on the site, starting from the site root. No initial slash.
    @param title: optional <h3> level subheading which is shown if the folder contains at least one item
    @param filter: optional content type mask. only this type of content items is shown.
    @param exclude_self: Do not list the current context
    """
    context = list_folder.namespace["context"]
    # you know some object which is refered as "context"
    portal_url = getToolByName(context, "portal_url")
    portal_catalog = getToolByName(context, "portal_catalog")
    portal = portal_url.getPortalObject()
    mtool = getToolByName(context, "portal_membership") 
    
    path = portal_url.getPortalPath() + "/" + folder
    # Get access to the folder object using slash notation
    #folder=portal.restrictedTraverse()
                
    search_dict = {
        "path" : { "query" : path, "depth" : 1 }
    }
    
    search_dict.update(filters)
        
    # Editors should be able to list items which are not yet publicly visible
    show_inactive = mtool.checkPermission('Access inactive portal content', context)        
    items = portal_catalog.queryCatalog(search_dict, show_inactive=show_inactive)
    
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