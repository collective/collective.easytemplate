"""Common configuration constants
"""

from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'collective.easytemplate'

ADD_CONTENT_PERMISSIONS = {
    'TemplatedDocument': 'collective.easytemplate: Add TemplatedDocument',
}

setDefaultRoles('collective.easytemplate: Add TemplatedDocument', ('Manager',))
