"""

    Tags for retrieving RSS feeds.
    
    httP://www.twinapex.com

"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope import interface

from collective.templateengines.interfaces import *

from plone.app.portlets.portlets.rss import RSSFeed

__author__ = """Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"""
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"


class RSSFeedTag:

    interface.implements(ITag)
    
    # Hold RSSFeed objects using url as a key
    _rss_cache = {}
    
    
    def getName(self):
        return "rss_feed"
    
    def render(self, scriptingContext, url, cache_timeout=60):
        """
        TODO: Support portal local date format
        """
        
        try:
            feed = RSSTag._rss_cache[url]
        except:
            feed = RSSFeed(url, cache_timeout)
            RSSFeedTag._rss_cache[url] = feed
            
        feed.update()
        
        items = feed.items
        for i in items:
            # Patch in few helpful variables
            # Format blog entry timestamps for the template
            if "updated" in i:
                # all feeds don't provide this information
                i["friendly_date"] = i["updated"].strftime("%Y-%m-%d")
            
        return items
        
        
        
        
        
        
        
            
        
            
        
    
    
        