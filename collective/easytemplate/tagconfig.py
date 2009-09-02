"""

    Maintain list of custom template tags.
    
    Just import & add new tags to this dictionary.
    
"""

from collective.easytemplate.tags.content import ListFolder, QueryTag, ExploreTag, LatestNewsTag
from collective.easytemplate.tags.views import ViewletTag, PortletTag, ViewTag, ProviderTag
from collective.easytemplate.tags.rss import RSSFeedTag

# Registered tags - function name - ITag interface instance
tags = [ListFolder(), QueryTag(), ViewletTag(), ViewTag(), PortletTag(), RSSFeedTag(), ExploreTag(), LatestNewsTag(), ProviderTag() ]

try:
    # Add translations tags only if LinguaPlone is installed
    import Products.LinguaPlone
    from collective.easytemplate.tags.i18n import CurrentLanguageTag, TranslateTag
    tags.append(CurrentLanguageTag())
    tags.append(TranslateTag())
except:
    pass