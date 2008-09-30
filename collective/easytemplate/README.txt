Introduction
------------

collective.easytemplate is targetted for sites whose end users need automatic text snippets in user editable texts. 
collective.easytemplate allows inserting template tags inside Kupu and email actions.

Motivation 
----------

Plone lacks out of the box support for custom, easily addable, template macros in content editors.

Use cases
---------

Possible use cases are

* Folder list snippets on a page

* Dynamic images

* Generated tables

* Emailing the content text on a workflow transtion

* Emailing a person whose email is defined in the contet itself on a workflow transition

The orignal use case was help maintaining the vast number of cross-reference link lists on course modules pages.

Example
-------

You write in Kupu::

  Hello user!
  
  Please select one course from below:
  
  $folder_list("courses")
 
will result to the output:

  Hello user!
  
  Please select one course from below:
  
  * `Math <http://example.example>`_
  
  * `Marketing <http://example.example>`_
  
  * `Chemistry <http://example.example>`_

Status
------

The current version (1.1) is still in development and has few issues.

* Zope security is not respected. You must trust your content editors, since
  Cheetah bypasses security and malicious Python sawy user could seriously 
  harm your site. For this reason, you can suggest any working Zope-aware
  non-XML-based template language for me.

* Cheetah namespace traverse does not work. E.g. $myobject.myvar raises
  NotFound exception even if it is not present. 

Installation 
------------

Add to your buildout::

	eggs = 
		collective.easytemplate
		
	zcml = 
		collective.easytemplate
	
Run quick installer for *Easy Template* product.

The product depends on `collective.templateengines <http://pypi.python.org/pypi?%3Aaction=pkg_edit&name=collective.templateengines>`_
and Cheetah Template engine. They should be automatically be installed by setuptools.

Usage
-----

Use content type "Templated Document" whenever you want to use template tags in Kupu content.

Use content rule action "Templated email" whenever you want to use template tags in workflow transition emails.

If you get errors in your template code, you can toggle on "Catch errors" on Template schemata
and view detailed exception tracebacks in Zope log.

Available templates
-------------------

Currently there isn't much you can do with the product out-of-the-box, but I accept
all tag contributions. Most tags are site specific, so I trust the site developers 
extending this product for their own needs.

Supported tags:

* Archetypes fields are automatically exported depending on the object: title, text, description, etc.

* *object_url* - Absolute url to the content object

* *portal_url*

   Portal absolute URL. Useful for links.

* *$list_folder*($folder, $title, $filters)* 
  
  portal_catalog based folder item listing with optional filter arguments.
  User inactive content access permission is respected (anonymous users
  don't see non-public content). 
  
  *folder*: portal root, slash separated, relative path to the folder. No prefixing slash.
  
  *title*: Print this <h3> heading if the folder contains any items
  
  *filters* : Python dictionary of optional filters

  List all documents in folder yoursite/testfol and print title if there are any present::
  
  	$list_folder($folder="testfol", $title="Test folder items", $filters={ "portal_type" : "Document"} )
  	
  List all portal root items::
  
    $list_folder($folder="")

  
Registering new tags
--------------------

If you want to add your own tags they must be added to Cheetah template namespace::

	from collective.easytemplate import tagconfig
	
	def mytagfunc():
		return "Foobar when the page is viewed"
	
	tagconfig["mytag"] = mytagfunc

See TemplatedDocument.py for hacks regarding security and namespace's availability in the functions.

Backends
--------

`collective.templateengines <http://pypi.python.org/pypi?%3Aaction=pkg_edit&name=collective.templateengines>`_ 
package is used to allow genericr pluggable Python template engines.
Currently only Cheetah template engine is tested and fully supported.

Plone's native TAL template language does not work too well with escaped HTML.

Tag debugging tips
------------------

If Cheetah template compilation fails you might have made copy-paste errors

* HTML formatted text, having HTML tags inside Cheetah expression

* Hard line breaked text, having hard line breaks inside Cheetah expression

So please recycle all your template tag copy-pastes through Notepad or similar application.

Author
------

Mikko Ohtamaa

`Red Innovation Oy, Oulu, Finland <http://www.redinnovation.com>`_ - High quality Python hackers for hire


Sponsorship
------------

The development of this product was sponsored by `London School of Marketing <http://londonschoolofmarketing.com>`_.




