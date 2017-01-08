Introduction
============

Lichen is a Python-like language and toolchain. The language foregoes various
dynamic aspects of Python to provide a foundation upon which more predictable
programs can be built, while preserving essential functionality to make the
core of the language seem very much like Python. The general syntax is largely
identical to Python, with only certain syntactic constructs being unsupported.

The toolchain employs existing tokeniser and parser software to obtain an
abstract syntax tree which is then inspected to provide data to support
deductions about the structure and nature of a given program. With the
information obtained from these processes, a program is then constructed,
consisting of a number of source files in the target compilation language
(which is currently the C programming language). This generated program may be
compiled and run, hopefully producing the intended results.

Contact, Copyright and Licence Information
==========================================

See the following Web pages for more information about this work:

http://projects.boddie.org.uk/Lichen

The author can be contacted at the following e-mail address:

paul@boddie.org.uk

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/gpl-3.0.txt for more information.
