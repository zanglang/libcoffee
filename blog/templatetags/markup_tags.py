# Taken from http://www.djangosnippets.org/snippets/119/ and Will Larson's
# http://lethain.com/entry/2008/aug/09/a-syntax-coloring-template-filter-for-django/
import rst_directive
from django import template
from django.contrib.markup.templatetags.markup import markdown, restructuredtext, textile
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from BeautifulSoup import BeautifulSoup
import logging

register = template.Library()

def generate_pygments_css(path=None):
	if path is None:
		import os
		path = os.path.join(os.getcwd(),'pygments.css')
	f = open(path,'w')
	f.write(HtmlFormatter().get_style_defs('.sourcecode'))
	f.close()


@register.filter
@stringfilter
def render(content, type=None):
	"""Render this content for display."""
	
	def wrap_plaintext(text):
		return '<p>' + unicode(content) + '</p>'
	
	try: # this structure feels quite bizarre...
		# Activate markdown extensions
		markedup = type == 'Markdown' and \
			markdown(unicode(content), arg='extra') or {
				'reStructuredText': restructuredtext,
				'Textile': textile,
				None: wrap_plaintext
			}[type](unicode(content)) 			
	except Exception, e:
		logging.warn('Error rendering as %s' % (type), exc_info=True)
		markedup = wrap_plaintext(content) # just wrap with paragraph
	
	# reST doesn't need highlighting using rst_directive.py
	if type == 'reStructuredText':
		return markedup
	
	# Replace the pulled code blocks with syntax-highlighted versions.
	formatter = HtmlFormatter(cssclass='sourcecode')
	soup = BeautifulSoup(markedup)
	# markdown and textile recommend <pre><code></pre> blocks
	for block in soup.findAll('pre'):
		chunk = block.code
		if chunk is None:
			continue # no wrapped code blocks		
		if chunk.has_key('class'):
			# <code class='python'>python code</code>
			try:
				lexer = get_lexer_by_name(chunk['class'], stripnl=True, encoding='UTF-8')
			except ValueError, e:
				continue # keep it untouched
		else:
			try:
				# Guess a lexer by the contents of the block.
				lexer = guess_lexer(chunk.renderContents())
			except ValueError, e:
				continue # keep it untouched
		block.replaceWith(highlight(chunk.renderContents(), lexer, formatter))
		
	return mark_safe(str(soup))