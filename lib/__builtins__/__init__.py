#!/usr/bin/env python

"""
Simple built-in classes and functions.

Copyright (C) 2015, 2016, 2017, 2019, 2021 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __builtins__.core import (
    function, get_using, module, object, type,
    ArithmeticError, Exception, FloatingPointError, MemoryError, OverflowError,
    TypeError, UnboundMethodInvocation, ZeroDivisionError
    )

# Exceptions.

from __builtins__.exception import (
    AssertionError,
    AttributeError,
    EOFError,
    EnvironmentError,
    IndentationError,
    IndexError,
    IOError,
    LoopExit,
    KeyError,
    KeyboardInterrupt,
    NotImplementedError,
    OSError,
    RuntimeError,
    StopIteration,
    SyntaxError,
    SystemError,
    SystemExit,
    TabError,
    UnicodeDecodeError,
    UnicodeEncodeError,
    UnicodeError,
    UnicodeTranslateError,
    ValueError
    )

# Classes.

from __builtins__.boolean import bool, False, True
from __builtins__.buffer import buffer
from __builtins__.complex import complex
from __builtins__.dict import dict
from __builtins__.file import file
from __builtins__.float import float
from __builtins__.int import int
from __builtins__.span import range, slice, xrange
from __builtins__.list import list
from __builtins__.long import long
from __builtins__.none import None, NoneType
from __builtins__.notimplemented import NotImplemented, NotImplementedType
from __builtins__.set import frozenset, set
from __builtins__.str import basestring, str, string
from __builtins__.tuple import tuple
from __builtins__.unicode import unicode

# Functions.

from __builtins__.attribute import getattr, hasattr, setattr
from __builtins__.character import bin, chr, hex, oct, ord, unichr
from __builtins__.comparable import cmp, hash
from __builtins__.identity import callable, id, isinstance, issubclass, repr
from __builtins__.io import open, raw_input, print_
from __builtins__.iteration import all, any, enumerate, filter, iter, len, map, max, min, reduce, reversed, sorted, sum, zip
from __builtins__.namespace import dir, globals, locals, vars
from __builtins__.numeric import abs, divmod, pow, round

# vim: tabstop=4 expandtab shiftwidth=4
