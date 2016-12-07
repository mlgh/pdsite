#!/usr/bin/env python

import sys
import os
import subprocess
import json
import textwrap
import tempfile
import hashlib
import tempfile
import shutil

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
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

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

    input_file = os.path.join(cache_dir, hashlib.md5(text).hexdigest() + '.tex')

    with open(input_file, 'wb') as f:
        f.write(text)

    output_file = os.path.join(cache_dir, hashlib.md5(text).hexdigest() + '.html')

    if not os.path.exists(output_file) or not os.path.getsize(output_file):
        try:
            tmpdir = tempfile.mkdtemp()
            with open(input_file) as f:
                subprocess.check_call(['latex'], stdin=f, stdout=sys.stderr, cwd=tmpdir)
            subprocess.check_call(['dvisvgm', '-b2pt', '-Z1.4', '-n', '-o', output_file, 'texput.dvi'], stdout=sys.stderr, cwd=tmpdir)
        finally:
            shutil.rmtree(tmpdir)

    with open(output_file, 'rb') as f:
        result = f.read().rstrip('\n')

    result = result.replace("id='", "id='" + hashlib.md5(text).hexdigest())
    result = result.replace("#g", "#" + hashlib.md5(text).hexdigest() + 'g')

    if params['t'] == 'InlineMath':
        result = result.replace('<svg ', '<svg style="vertical-align: middle; display: inline-block"', 1)
        return RawInline('html', result)
    elif params['t'] == 'DisplayMath':
        return RawInline('html', '<p>' + result + '</p>')

if __name__ == '__main__':
    toJSONFilter(tex_to_svg)
