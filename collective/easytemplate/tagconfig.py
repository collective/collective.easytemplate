"""

    Maintain list of custom template tags.
    
    Just import & add new tags to this dictionary.
    
"""

from collective.easytemplate.tags.content import list_folder, pick_content

tags = {
        "list_folder" : list_folder,
        "pick_content" : pick_content        
}