"""

    Tags for retrieving RSS feeds.
    
    httP://www.twinapex.com

"""
import time
from DateTime import DateTime

try:
    import feedparser
except:
    # Plone 3.1
    feedparser =None
    pass

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope import interface

from collective.templateengines.interfaces import *
from collective.templateengines.interfaces import ITag

from plone.app.portlets.portlets.rss import RSSFeed

if feedparser != None:
    ACCEPTED_FEEDPARSER_EXCEPTIONS = (feedparser.CharacterEncodingOverride, )

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__docformat__ = 'epytext'
__copyright__ = "2010 Twinapex Research"
__license__ = "GPL v2"


class RSSFeedTag:
    """ Expose RSS feed as iterable items to templates.
    
    Possible item parameters, directly from RSS mappings:
    
    * updated
    
    * friendly_date (readable date)
    
    * title
    
    * url
    
    """
    interface.implements(ITag)
    
    # Hold RSSFeed objects using url as a key
    _rss_cache = {}
    
    
    def getName(self):
        return "rss_feed"
    
    @staticmethod
    def getFeed(url, cache_timeout=300):
        """ A helper method to read RSS feed status as cached.
        
        """

        if not url in RSSFeedTag._rss_cache:
            # Lazy construction pattern
            feed = NiceRSSFeed(url, cache_timeout)
            RSSFeedTag._rss_cache[url] = feed
                
        feed = RSSFeedTag._rss_cache[url]
        feed.update()
        
        return feed

    
    def render(self, scriptingContext, url, cache_timeout=300):
        """
        TODO: Support portal local date format
        """
        
        feed = RSSFeedTag.getFeed(url, cache_timeout)
        
        items = feed.items
        for i in items:
            # Patch in few helpful variables
            # Format blog entry timestamps for the template

            
            # Templates can use Zope DateTime formatting directly
            # http://pypi.python.org/pypi/DateTime/
            # http://n2.nabble.com/toLocalizedTime-td1090969.html
            
            if "updated" in i:
                # all feeds don't provide this information
                i["friendly_date"] = i["updated"].strftime("%Y-%m-%d")
                
            else:
                i["update"] = None
                                            
        return items
        
class NiceRSSFeed(RSSFeed):
    """ Add support for additional RSS parameters 
    
    http://svn.plone.org/svn/plone/plone.app.portlets/trunk/plone/app/portlets/portlets/rss.py        
    """
    
    def _retrieveFeed(self):
        """do the actual work and try to retrieve the feed"""
        url = self.url
        if url!='':
            self._last_update_time_in_minutes = time.time()/60
            self._last_update_time = DateTime()
            d = feedparser.parse(url)
            if d.bozo == 1 and not isinstance(d.get('bozo_exception'),
                                              ACCEPTED_FEEDPARSER_EXCEPTIONS):
                self._loaded = True # we tried at least but have a failed load
                self._failed = True
                return False
            self._title = d.feed.title
            self._siteurl = d.feed.link
            self._items = []
            for item in d['items']:
                try:
                    link = item.links[0]['href']

                    itemdict = {
                        'title' : item.title,
                        'url' : link,
                        'summary' : item.get('description',''),
                        'author' : item.get('author', None)
                    }
                    if hasattr(item, "updated"):
                        itemdict['updated']=DateTime(item.updated)
                except AttributeError:
                    continue
                self._items.append(itemdict)
            self._loaded = True
            self._failed = False
            return True
        self._loaded = True
        self._failed = True # no url set means failed
        return False # no url set, although that actually should not really happen
    