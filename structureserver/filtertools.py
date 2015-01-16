#!/usr/bin/env python
#
#  Copyright 2009 by Sean Reifschneider, tummy.com, ltd.  <jafo@tummy.com>
#
#  Licensed to PSF under a Contributor Agreement.
#  See http://www.python.org/2.6/license for licensing details.

r'''filtertools - Text filtering tools for strings and files.

One common use-pattern that I find myself doing when using Python to process
data in files is something like:

	for line in fp.readlines():
		m = re.search(r'something(.*)', line)
		if m:
			print r.group(1)
			continue

filtertools initially started to investigate whether the lack of a
"if value = re.search():" ability could be nicely worked around by
augmenting the string objects to have some regular-expression functionality.
Changing the above into:

	for line in fp.readlines():
		if line.re.search(r'something(.*)', line):
			print line.re.group(1)
			continue

A (admittedly small) change which results in a more readable construction.
IMHO, of course.  :-)

It also defines some convenience functions for processing text files.

Regexes as used in the filtertools module
=========================================
The regular expressions used in this module can all be either strings,
which will be compiled, or regular expression objects as returned by
re.compile().  Whether to compile the argument is determined by whether
the requested method, such as search() or match() are available on the
regex.  If not, that regex is compiled.

You can pass a compiled regex if you want to influence the regex such as
having it be case-insensitive.

Files or iterators as arguments
===============================
Methods that take "file_or_iter" as an argument can take any of the
following as arguments:

	A string representing the name of a file.  If a string is passed, it is
	opened as a read-only text file, and then treated as if it were passed
	in as a file.  The file object is closed when done, if this method is
	used.

	A file object, which will be treated as an iterator over the lines
	within the file.  Each line is returned as an restr() object.  The file
	is *NOT* closed when done, if it is passed in as a file object.

	An iterator of restr() objects.  For example, the result of an reopen()
	call.

In the case of "file_or_name" arguments to methods, these can be either a
string representing the filename, or a file object.  It is like the
"file_or_iter" argument, except that iterators are not accepted.

restr() Objects
===============

The restr() class is a string which has grown a "re" attribute.

This is one of the primary features of filtertools, but it is typically not
called directly.  Instead, using the "reopen()" or "grep()" methods would
be used, which iterate over the contents of the file, each line returned as
a restr() object.

The "re" attribute of restr() objects have the following methods:

search(regex):
match(regex):
	The call "restr('Test').re.match(regex)" is equivalent to
	regex.match('Test').  If this match succeeds, the "group()" and
	"groupdict()" methods of the resulting match are stored in the
	"re" attribute of the "restr".

	Note that "regex" can be a string or a SRE_Pattern object as returned by
	"re.compile()".

	See the "re" module documentation for information about the differences
	between search() and match().

	For example:

		s = restr('Test')
		if s.re.match(r'T(.*)'): print s.re.group(1)

group(*args):
groudict(*args):
	These methods are stored off after a successful regular expression match.
	They take the same arguments as a normal SRE_Match object.

	If no previous match()/search() has been completed, group() returns
	an empty tuple and groupdict returns an empty dictionary.

Helper routines
===============
The following helpers are defined to make processing files easier:

reopen(filename, *args, **kwargs):
	A file object is returned as with the built-in open() method.  The
	arguments are passed directly along to open().

	The difference is that the readline() and readlines() methods produce
	restr() objects.

readlines(file_or_name):
	See the above discussion of "file_or_name".

	This helper is shorthand for opening the file (if a file object is not
	passed in), iterating over the lines within the file and yielding
	restr() objects, and then closing the file.

Iterator routines
=================
These routines all work with iterators (which they themselves return) or
files, to perform some sort of processing.  Some of these functions have
Unix-like aliases where appropriate, like "ifilter" and "grep" are
basically the same thing.

ifilter(regexList, file_or_iter):
grep(regexList, file_or_iter):  (Unix-like alias)
	See the above discussions of regexes and "file_or_iter".

	This method results in an iterator which yields restr() objects which
	match (or do not match, if "invert" is True) one of the regexes in
	"regexList".  The regexes are searched in order, and the first matching
	regex is used.

	The "invert" flag causes only lines which *DO NOT* match any regex to be
	yielded.  It is like the "-v" argument to the Unix "grep" program.

	Multiple grep()s can be chainged together, like:

		grep(['smtp'],
				grep(['25'],
				reopen('/etc/services')))

ifilterfalse(regexList, file_or_iter):
grepv(regexList, file_or_iter):  (Unix-like alias)
	This is a short-hand for "grep(..., invert = True)".

dropwhile(regexes, file_or_iter):
	These two routines will yield items after one of the regexes matches.

takewhile(regexes, file_or_iter):
	This is the inverse of dropwhile, it yields items until one of the
	regexes matches.

imap(func, *file_or_iter):
	Call the provided function once for each element of each provided
	file_or_iter.  There can be any number of files or iterators provided.
	For example, this:

		imap(func, a, b)

	Is equivalent to:

		func(a[0], b[0])
		func(a[1], b[1])
		[...]

starmap(func, file_or_iter):
	Call the provided function passing each element as an argument with an
	asterisk.  For example:

		starmap(func, a)

	Is equivalent to:

		func(*(a[0]))
		func(*(a[1]))

islice(file_or_iter, [start,] stop [, step]):
	Yield elements by skipping the optional "start" number, until the "stop"
	element is reached, skipping the optional "step" elements.  This is like
	using slice notation on a list.

chain(*file_or_iter):
cat(*file_or_iter):  (Unix-like alias)
	Yield all elements of each file_or_iter, treating them as if they were
	one long united iterator.  There can be any number of files or iterators
	provided.  For example, this:

		chain(a, b, c)

	Is similar to:

		[ a[0], a[1], ... a[N], b[0], b[1], ... b[N], c[0], c[1], ... c[N] ]

izip(*file_or_iter):
	"Zip" together the listed iterators resulting in an iterator that yields
	a tuple of the corresponding item from each.  There can be any number
	of files or iterators provided.  For example, this:

		izip(a, b)

	Is similar to:

		[ ( a[0], b[0] ), ( a[1], b[1] ), ... (a[N], b[N]) ]

izip_longest(*file_or_iter [, fillvalue = None]):
	Like izip, but if the iterators are of different lengths, the shorter
	ones will be filled with trailing elements of either "None" (default) or
	the keyword argument "fillvalue".

tee(file_or_iter, n):
	Replicate the specified iterator "n" times, producing a list of
	iterators.  For example:

		tee(a, 2)

	Is similar to:

		[ a[:], a[:] ]

Example of use
==============

>>> import filtertools
>>> s = filtertools.restr('This is a test')
>>> s.re.groups()
()
>>> s.re.match(r'^.(.*)$')
<_sre.SRE_Match object at 0xb7e92ae0>
>>> s.re.groups()
('his is a test',)
>>> s.re.groupdict()
{}
>>> for line in filtertools.reopen('/etc/services', 'r').readlines():
...    if line.re.match(r'.*imap.*'): print line.rstrip()
... 
imap            143/tcp         imap2           # Interim Mail Access Proto v2
imap            143/udp         imap2
imap3           220/tcp                         # Interactive Mail Access
imap3           220/udp                         # Protocol v3
imaps           993/tcp                         # IMAP over SSL
imaps           993/udp                         # IMAP over SSL
>>> for line in grep([ r'25' ], grep([ r'smtp' ], '/etc/services')):
...    print line.rstrip()
... 
smtp            25/tcp          mail
smtp            25/udp          mail
>>> 
'''

#################
class restr(str):
	r'''The restr() class is a string which has grown a "re" attribute.

	This is one of the primary features of filtertools, but it is typically not
	called directly.  Instead, using the "reopen()" or "grep()" methods would
	be used, which iterate over the contents of the file, each line returned as
	a restr() object.

	The "re" attribute of restr() objects have the following methods:

		search(regex)
		match(regex)
		group(*args)
		groudict(*args)
	'''

	##############
	class ReClass:
		######################
		def __init__(self, s):
			self.s = s
			self.group = self._nogroup
			self.groups = self._nogroups
			self.groupdict = self._nogroupdict

		######################################
		def _researchmatch(self, regex, name):
			import re
			if hasattr(regex, name):
				match = getattr(regex, name)(self.s)
			else:
				match = getattr(re, name)(regex, self.s)

			if match:
				self.group = match.group
				self.groups = match.groups
				self.groupdict = match.groupdict
			else:
				self.group = self._nogroup
				self.groups = self._nogroups
				self.groupdict = self._nogroupdict

			return(match)

		#######################
		def match(self, regex):
			r'''Match the current string object against the supplied regex.
			match(regex):
				The call "restr('Test').re.match(regex)" is equivalent to
				regex.match('Test').  If this match succeeds, the "group()" and
				"groupdict()" methods of the resulting match are stored in the
				"re" attribute of the "restr".

				Note that "regex" can be a string or a SRE_Pattern object as returned by
				"re.compile()".

				See the "re" module documentation for information about the differences
				between search() and match().

				For example:

					s = restr('Test')
					if s.re.match(r'T(.*)'): print s.re.group(1)
			'''
			return(self._researchmatch(regex, 'match'))

		########################
		def search(self, regex):
			r'''Search the current string object for the supplied regex.
			search(regex):
				The call "restr('Test').re.match(regex)" is equivalent to
				regex.match('Test').  If this match succeeds, the "group()" and
				"groupdict()" methods of the resulting match are stored in the
				"re" attribute of the "restr".

				Note that "regex" can be a string or a SRE_Pattern object as returned by
				"re.compile()".

				See the "re" module documentation for information about the differences
				between search() and match().

				For example:

					s = restr('Test')
					if s.re.search(r'T(.*)'): print s.re.group(1)
			'''
			return(self._researchmatch(regex, 'search'))

		#####################
		def groupdict(*args):
			r'''
			group(*args):
			groups(*args):
			groudict(*args):
				These methods are stored off after a successful regular expression match.
				They take the same arguments as a normal SRE_Match object.

				If no previous match()/search() has been completed, group() returns
				an empty tuple and groupdict returns an empty dictionary.
			'''
			#  NOTE: This is just a documentation place-holder.  At run-time
			#  this method is replaced with the correspondingSRE_Match object
			#  methods.
			pass
		groups = groupdict
		group = groupdict

		##############################
		def _nogroup(*args, **kwargs):
			raise IndexError('no such group')

		###############################
		def _nogroups(*args, **kwargs):
			return(tuple())

		##################################
		def _nogroupdict(*args, **kwargs):
			return({})

	##################################
	def __new__(self, s, *args, **kw):
		self.re = self.ReClass(s)
		return(str.__new__(self, s, *args, **kw))
	
	#########################
	def __add__(self, other):
		return(restr(str(self) + other))

	##########################
	def __radd__(self, other):
		return(restr(other + str(self)))

	#########################
	def __mul__(self, other):
		return(restr(str(self) * other))

###############################
class _ReadlinesHelper(object):
	#######################################
	def __init__(self, fp, doClose = True):
		self.fp = fp
		self.doClose = doClose

	###################
	def __iter__(self):
		while True:
			line = self.fp.readline()
			if not line: break
			yield restr(line)
	
	##################
	def __del__(self):
		if self.doClose:
			self.fp.close()
			self.fp = None

###########################
def _convertToIter(object):
	if hasattr(object, 'readline'):
		object = _ReadlinesHelper(object)
	elif hasattr(object, '__iter__'):
		pass
	else:
		object = reopen(object, 'r')
	return(object)

###########################
def _convertToFile(object):
	if hasattr(object, 'readline'):
		object = _ReadlinesHelper(object)
	else:
		object = reopen(object, 'r')
	return(object)

############################
def readlines(file_or_name):
	return(_ReadlinesHelper(_convertToFile(file_or_name)))

########################
class _FileHelper(file):
	def readlines(self):
		return(_ReadlinesHelper(self, doClose = False))

	def readline(self):
		return(restr(file.readline(self)))

######################################
def reopen(filename, *args, **kwargs):
	return(_FileHelper(filename, *args, **kwargs))

################################################
def _applyiter(itertool, regexes, file_or_iter):
	def compare(line):
		for regex in regexes:
			if line.re.search(regex): return(True)
		return(False)

	return(itertool(compare, _convertToIter(file_or_iter)))

###################################
def ifilter(regexes, file_or_iter):
	import itertools
	return(_applyiter(itertools.ifilter, regexes, _convertToIter(file_or_iter)))

########################################
def ifilterfalse(regexes, file_or_iter):
	import itertools
	return(_applyiter(itertools.ifilterfalse, regexes,
			_convertToIter(file_or_iter)))

#####################################
def dropwhile(regexes, file_or_iter):
	import itertools
	return(_applyiter(itertools.dropwhile, regexes,
			_convertToIter(file_or_iter)))

#####################################
def takewhile(regexes, file_or_iter):
	import itertools
	return(_applyiter(itertools.takewhile, regexes,
			_convertToIter(file_or_iter)))

######################
def imap(func, *args):
	import itertools
	args = map(_convertToIter, args)
	return(itertools.imap(func, *args))

################################
def starmap(func, file_or_iter):
	import itertools
	return(itertools.starmap(func, _convertToIter(file_or_iter)))

################################
def islice(file_or_iter, *args):
	import itertools
	return(itertools.islice(_convertToIter(file_or_iter), *args))

#################
def chain(*args):
	import itertools
	args = map(_convertToIter, args)
	return(itertools.chain(*args))

################
def izip(*args):
	import itertools
	args = map(_convertToIter, args)
	return(itertools.izip(*args))

#############################
def izip_longest(*args, **kw):
	import itertools
	args = map(_convertToIter, args)
	return(itertools.izip_longest(*args, **kw))

#########################
def tee(file_or_iter, n):
	import itertools
	return(itertools.tee(_convertToIter(file_or_iter), n))

##################
#  unix-like names
grep = ifilter
grepv = ifilterfalse
cat = chain
