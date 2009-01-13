"""

    Maintain list of custom template tags.
    
    Just import & add new tags to this dictionary.
    
"""

from collective.easytemplate.tags.content import ListFolder, QueryTag, ExploreTag
from collective.easytemplate.tags.views import ViewletTag, PortletTag
from collective.easytemplate.tags.rss import RSSFeedTag

# Registered tags - function name - ITag interface instance
tags = [ListFolder(), QueryTag(), ViewletTag(), PortletTag(), RSSFeedTag(), ExploreTag() ]