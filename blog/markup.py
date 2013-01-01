import logging
import rst_directive  # @UnusedImport
from BeautifulSoup import BeautifulSoup
from docutils.core import publish_parts
from markdown import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from textile import textile

from blog import app

@app.app_template_filter('markup')
def markup(content, markuptype=None):
	"""Render this content for display."""

	def wrap_plaintext(text):
		return u'<p>' + content + u'</p>'

	def markdowntext(text):
		return markdown(text, ['extra', 'codehilite'], output_format='html')

	def restructuredtext(text):
		parts = publish_parts(source=text, writer_name='html4css1',
					settings_overrides={})
		return parts['fragment']

	try:
		# Activate markdown extensions
		markedup = {
				'Markdown': markdowntext,
				'Textile': textile,
				'reStructuredText': restructuredtext,
				None: wrap_plaintext
			}[markuptype](unicode(content))
	except Exception:
		logging.exception('Error rendering as %s' % (markuptype))
		markedup = wrap_plaintext(content)  # just wrap with paragraph

	# reST doesn't need highlighting using rst_directive.py
	if type in ['reStructuredText', 'Markdown']:
		return markedup

	# Replace the pulled code blocks with syntax-highlighted versions.
	formatter = HtmlFormatter(cssclass='sourcecode')
	soup = BeautifulSoup(markedup)
	# markdown and textile recommend <pre><code></pre> blocks
	for block in soup.findAll('pre'):
		chunk = block.code
		if chunk is None:
			continue  # no wrapped code blocks
		if chunk.has_key('class'):
			# <code class='python'>python code</code>
			try:
				lexer = get_lexer_by_name(chunk['class'], stripnl=True, encoding='UTF-8')
			except ValueError:
				continue  # keep it untouched
		else:
			try:
				# Guess a lexer by the contents of the block.
				lexer = guess_lexer(chunk.renderContents())
			except ValueError:
				continue  # keep it untouched
		block.replaceWith(highlight(chunk.renderContents(), lexer, formatter))

	return unicode(soup)
