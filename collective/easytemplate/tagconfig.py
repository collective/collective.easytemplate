"""

    Maintain list of custom template tags.
    
    Just import & add new tags to this dictionary.
    
"""

from collective.easytemplate.tags.content import ListFolder


# Registered tags - function name - ITag interface instance
tags = [ListFolder(),]