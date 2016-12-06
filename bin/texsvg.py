#!/usr/bin/env python

import sys
import os
import subprocess
import json
import textwrap
import tempfile
import hashlib

from pandocfilters import toJSONFilter, RawInline

def tex_to_svg(key, value, fmt, meta):
	if key != 'Math':
		return

	params, text = value

	if params['t'] == 'InlineMath':
		text = '\\(' + text + '\\)'
	elif params['t'] == 'DisplayMath':
		text = '\\[' + text + '\\]'
	else:
		return

	cache_dir = '/tmp/pandoc.texsvg.cache'

	if isinstance(text, unicode):
		text = text.encode('utf-8')

	text = text.replace('\r', '').replace('\n', '')

	text = textwrap.dedent("""
          \\documentclass[border=1pt,varwidth]{standalone}
          \\usepackage{standalone}
          \\usepackage{amsmath}
          \\usepackage{amssymb}
          \\usepackage{cancel}
          \\begin{document}
          """).lstrip() + text + textwrap.dedent("""
          \\end{document}
          """).rstrip()

	output_file = os.path.join(cache_dir, hashlib.md5(text).hexdigest() + '.html')

	with tempfile.TemporaryFile() as f:
		f.write(text.encode('utf-8') if isinstance(text, unicode) else text)
		f.flush()
		f.seek(0)
		print>>sys.stderr, text
		subprocess.check_call(['latex'], stdin=f, stdout=sys.stderr, cwd='/tmp')
		subprocess.check_call(['dvisvgm', '-b2pt', '-Z1.4', '-n', '-o', output_file, 'texput.dvi'], stdout=sys.stderr, cwd='/tmp')

	with open(output_file, 'rb') as f:
		result = f.read().rstrip('\n')

	if params['t'] == 'InlineMath':
		result = result.replace('<svg ', '<svg style="vertical-align: middle; display: inline-block"', 1)
		return RawInline('html', result)
	elif params['t'] == 'DisplayMath':
		return RawInline('html', '<p>' + result + '</p>')



if __name__ == '__main__':
	toJSONFilter(tex_to_svg)
