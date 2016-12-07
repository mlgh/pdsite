#!/usr/bin/env python

import sys
from pandocfilters import toJSONFilter, RawBlock
import matplotlib.pyplot as plt
import numpy as np
import os
import contextlib
import shutil
import tempfile

@contextlib.contextmanager
def chdir_ctx(d):
	cwd = os.getcwd()
	try:
		os.chdir(d)
		yield
	finally:
		os.chdir(cwd)

@contextlib.contextmanager
def tempdir(*args, **kwargs):
	delete = kwargs.pop('delete', True)
	d = None
	try:
		d = tempfile.mkdtemp(*args, **kwargs)
		yield d
	finally:
		if delete and d is not None:
			shutil.rmtree(d)

def indent(text):
	return '\n'.join(' ' * 4 + line for line in text.split('\n'))

def inline_image(filename):
	with open(filename, 'rb') as f:
		base64_img = f.read().encode('base64').replace('\n', '')
		return RawBlock('html', '<img src="data:image/png;base64,%s" />' % base64_img)


def run_python_filter(key, value, fmt, meta):
	if key != 'CodeBlock':
		return
	params, text = value
	if params[1] != ['run_python']:
		return
	func_text = 'def generated_function():\n' + indent(text)
	exec func_text
	with tempdir() as tmpdir:
		with chdir_ctx(tmpdir):
			return generated_function()

if __name__ == '__main__':
    toJSONFilter(run_python_filter)