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
	f.write(HtmlFormatter().get_style_defs('.highlight'))
	f.close()


@register.filter
@stringfilter
def render(content, type=None):
	"""Render this content for display."""
	
	def wrap_plaintext(text):
		return '<p>' + str(content) + '</p>'
	
	try: # this structure feels quite bizarre...
		markeddown = {
			'reStructuredText': restructuredtext,
			'Markdown': markdown,
			'Textile': textile,
			None: wrap_plaintext
		}[type](str(content))
	except Exception, e:
		logging.warn('Error rendering as %s' % (type), exc_info=True)
		markeddown = wrap_plaintext(content) # just wrap with paragraph
	
	# Replace the pulled code blocks with syntax-highlighted versions.
	soup = BeautifulSoup(markeddown)
	code_blocks = soup.findAll('code')
	formatter = HtmlFormatter()
	for block in code_blocks:
		chunk = block.renderContents()
		if block.has_key('class'):
			# <code class='python'>python code</code>
			try:
				lexer = get_lexer_by_name(block['class'], stripnl=True, encoding='UTF-8')
			except ValueError, e:
				# <code>plain text, whitespace-preserved</code>
				lexer = get_lexer_by_name('text', stripnl=True, encoding='UTF-8')
		else:
			try:
				# Guess a lexer by the contents of the block.
				lexer = guess_lexer(chunk)
			except ValueError, e:
				# <code>plain text, whitespace-preserved</code>
				lexer = get_lexer_by_name('text', stripnl=True, encoding='UTF-8')
		# Just make it plain text.
		block.replaceWith(highlight(chunk, lexer, formatter))
	return mark_safe(str(soup))