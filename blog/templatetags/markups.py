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
def render(content, markuptype='None'):
	"""Render this content for display."""

	# First, pull out all the <code></code> blocks, to keep them away
	# from Markdown (and preserve whitespace).
	soup = BeautifulSoup(str(content))
	code_blocks = soup.findAll('code') # Typo support
	for block in code_blocks:
		block.replaceWith('<code class="removed"></code>')
	print code_blocks
	print soup
	print '-------'
	markeddown = '' # probably should use lambdas here...
	if markuptype == 'r':
		markeddown = restructuredtext(str(soup))
	elif markuptype == 'm':
		markeddown = markdown(str(soup))
	elif markuptype == 't':
		markeddown = textile(str(soup))
	else:
		markeddown = '<p>' + str(soup) + '</p>' # just wrap with paragraph
	
	# Replace the pulled code blocks with syntax-highlighted versions.
	soup = BeautifulSoup(markeddown)
	print soup
	empty_code_blocks, index = soup.findAll('code', 'removed'), 0
	print empty_code_blocks
	formatter = HtmlFormatter()
	for block in code_blocks:
		if block.has_key('class'):
			# <code class='python'>python code</code>
			language = block['class']
		else:
			# <code>plain text, whitespace-preserved</code>
			language = 'text'
		try:
			lexer = get_lexer_by_name(language, stripnl=True, encoding='UTF-8')
		except ValueError, e:
			try:
				# Guess a lexer by the contents of the block.
				lexer = guess_lexer(block.renderContents())
			except ValueError, e:
				# Just make it plain text.
				lexer = get_lexer_by_name('text', stripnl=True, encoding='UTF-8')
		empty_code_blocks[index].replaceWith(
				highlight(block.renderContents(), lexer, formatter))
		index = index + 1

	return mark_safe(str(soup))