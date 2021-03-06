"""
page.py
=======

Get HTML Page
-------------

Add head, breadcrumbs and sub pages if required

This has to be process here and not in client
so that static page can be accurately generated
for search engines.

All this would be un-necessary otherwise

Usage
-----

get(name=[str]) - get full page including template

content(name=[str]) - get content

Template
--------
A template for this must be present in [context]/_index.html

and must have `%(content)s`
"""
from lib.chai import objstore, db, whitelist

def get(name):
	"""return page html"""
	template = get_template()
	obj = content(name=name)
	html = """<div class="content-wrap active" id="%s">%s</div>""" % (name, obj['html'])
	
	if obj.get('js'):
		html += """<script type="text/javascript">%s</script>""" % obj['js']
	
	return template % {'content': html, 'bootjs':bootjs()}

def get_template():
	from lib.chai import sitepath
	
	with open(sitepath('_index.html'), 'r') as index:
		template = index.read()

	return template

@whitelist(allow_guest=True)
def content(**args):
	"""get page html with header and footer"""
	obj = objstore.get(type='page', name=args.get('name', 'index'))
	
	if not 'html' in obj:
		obj['html'] = """<h1>Not Found</h1><p>This link is not active. 
			<a href="#index">Go back to Home Page</a></p>"""
		
	return {'html': header(obj) + obj["html"] + footer(obj), 
		'js': obj.get('js', ''), 'css':obj.get('css', '')}
	
def header(obj):
	"""add page header and breadcrumbs"""
	head = ''
	if 'ancestors' in obj and obj['ancestors']:
		head += '<ul class="breadcrumb">'
		for a in obj['ancestors']:
			head += """<li><a href="#%(name)s">%(label)s</a>
				<span class="divider">/</span></li>""" % a
				
		head = head + """<li class="active">%(label)s</li></ul>""" % obj
		
	if not '</h1>' in obj['html']:
		head += '<div class="page-header"><h1>' + obj['label'] + '</h1></div>'
		
	return head
	
def footer(obj):
	"""append sub-pages to footer"""
	foot = ''
	if 'subpages' in obj and obj['subpages']:
		foot = """<p><div class="span5 round item-box">
			<h5>Content</h5><ol>"""
		
		for s in obj['subpages']:
			foot += """<li><a href="#%(name)s">%(label)s</a></li>""" % s
			
		foot += """</ol></div></p>"""
		
	return foot

def bootjs():
	"""get boot js - cms_settings"""
	from lib.chai import rdfstore
	import json
	return 'app.cms_settings = ' + json.dumps(rdfstore.get(name='cms_settings') or {})
	