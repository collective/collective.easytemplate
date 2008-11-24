from zope import schema

# TODO: Fix to use message factory
from plone.portlet.static.static import _
from plone.portlet.static import static

class ITemplatedPortlet(static.IStaticPortlet):
    """ Define a portlet which allows template tags in the body content. """

    # Override standard  text field
    text = schema.Text(
        title=_("Text"),
        description=_("The text to render. May include dynamic tags."),
        required=True)
