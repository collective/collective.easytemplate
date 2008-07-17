Introduction
------------

collective.easytemplate is targetted for the end users who need automatic text snippets in their Kupu content. 
collective.easytemplate allows safe template tags inside Kupu editable text or any user editable HTML. 
This enables automatic content generation inside HTML pages. 

Motivation 
----------

Plone lacks out of the box support to custom tags for content editors to play with.

Use cases
---------

The orignal use case was help maintaining the vast number of cross-reference link lists on course modules pages.

Possible other use cases are

* Folder list snippets on a page

* Dynamic images

* Generated tables

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

The current version (0.1) is still in development and has few issues.

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

Usage
-----

Use content type "Templated Document" whenever you want to use template tags in Kupu content.

If you get errors in your template code, you can toggle on "Catch errors" on Template schemata
and view detailed exception tracebacks in Zope log.

Available tags
--------------

Currently there isn't much you can do with the product out-of-the-box, but I accept
all tag contributions. Most tags are site specific, so I trust the site developers 
extending this product for their own needs.

Supported tags (version 0.1):

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

* *portal_url*

   Print portal absolute URL. Useful for links.
  
Registering new tags
--------------------

If you want to add your own tags they must be added to Cheetah template namespace::

	from collective.easytemplate import tagconfig
	
	def mytagfunc():
		return "Foobar when the page is viewed"
	
	tagconfig["mytag"] = mytagfunc

See TemplatedDocument.py for hacks regarding security and namespace's availability in the functions.


Backend
-------

Cheetah template engine is used. Plone's native TAL does not work too well with escaped HTML.

Tag debugging tips
------------------

If Cheetah template compilation fails you might have made copy-paste errors

* HTML formatted text, having HTML tags inside Cheetah expression

* Hard line breaked text, having hard line breaks inside Cheetah expression

So please recycle all your template tag copy-pastes through Notepad or similar application.

Sponsorship
------------

The development of this product was sponsored by `London School of Marketing <http://londonschoolofmarketing.com>`_.




