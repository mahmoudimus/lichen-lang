Introduction
============

Lichen is both a Python-like language and a toolchain for that language. The
language foregoes various dynamic aspects of Python to provide a foundation
upon which more predictable programs can be built, while preserving essential
functionality to make the core of the language seem very much "like Python"
(thus yielding the name "Lichen"). The general syntax is largely identical to
Python, with only certain syntactic constructs being deliberately unsupported,
largely because the associated features are not desired.

The toolchain employs existing tokeniser and parser software to obtain an
abstract syntax tree which is then inspected to provide data to support
deductions about the structure and nature of a given program. With the
information obtained from these processes, a program is then constructed,
consisting of a number of source files in the target compilation language
(which is currently the C programming language). This generated program may be
compiled and run, hopefully producing the results intended by the source
program's authors.

Lichen source files use the .py suffix since the language syntax is
superficially compatible with Python, allowing text editors to provide
highlighting and editing support for Lichen programs without the need to
reconfigure such tools. However, an alternative suffix is likely to be
introduced in future.

Getting Started
===============

The principal interface to the toolchain is the lplc command which can be run
on source files as in the following example:

lplc tests/unicode.py

This causes the inspection of the indicated program file and all imported
modules, the deduction and optimisation of program information, and the
generation and translation of the program to a form suitable for compilation.
By default, compilation is performed by invoking the widely-known make
utility.

The results of this process are stored in the _lplc directory, with the
executable program being written out as "_main" in the working directory
unless the -o option is presented to lplc. For example:

lplc -o unicode tests/unicode.py

The executable program here will be written out as "unicode" and can be run
directly:

./unicode

Since the executable program is merely C source code and can be compiled using
a normal C compiler, it may also be compiled using a cross compiler by setting
the ARCH environment variable. For example:

ARCH=mipsel-linux-gnu lplc -o unicode tests/unicode.py

This employs a cross compiler targeting the mipsel (little-endian MIPS)
architecture running GNU/Linux.

Test Suite
==========

A test suite is provided to exercise the toolchain and expose regressions.
More information is available by running the test_all.sh script with the
appropriate option:

./test_all.sh --help

Running it with the --build option should prove to be the most useful
approach in testing code analysis and validating code generation.

Source Code Overview
====================

The source files implementing the toolchain are found in the distribution
directory with .py suffixes. The lplc tool is also found in the distribution
directory.

The following directories also contain source code employed by the toolchain:

compiler       - a modified version of the Python compiler package
pyparser       - a modified version of the PyPy parser package

The following directories provide tests:

internal_tests - a collection of tests exercising toolchain objects directly
tests          - individual test programs exercising the toolchain itself

The toolchain relies on additional code when generating output programs:

lib            - the standard library for Lichen programs
templates      - runtime support libraries for generated programs

Finally, a docs directory provides documentation about this project.

Contact, Copyright and Licence Information
==========================================

See the following Web pages for more information about this work:

http://projects.boddie.org.uk/Lichen

The author can be contacted at the following e-mail address:

paul@boddie.org.uk

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/gpl-3.0.txt for more information.

Generating the Wiki Pages
=========================

The docs/tools/make_pages.sh script generates a page package for MoinMoin. The
following command will generate a page package called pages.zip using the
pages directory for staging, with Lichen as the page prefix:

docs/tools/make_pages.sh pages Lichen

Make sure to include the page prefix where the pages are being deployed in a
wiki with other content at the top level.

Currently, the wiki pages require the following extensions:

ImprovedTableParser     https://moinmo.in/ParserMarket/ImprovedTableParser

MoinSupport             http://hgweb.boddie.org.uk/MoinSupport

GraphvizParser          https://moinmo.in/ParserMarket/graphviz

The GraphvizParser requires diagram-tools for the notugly.xsl stylesheet,
although a copy of the stylesheet is provided in the GraphvizParser
distribution for convenience.
