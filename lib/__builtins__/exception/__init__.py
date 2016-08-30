#!/usr/bin/env python

"""
Exception objects.

Copyright (C) 2015 Paul Boddie <paul@boddie.org.uk>

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

from __builtins__.exception.assertion import (
    AssertionError
    )

from __builtins__.exception.base import (
    GeneratorExit,
    IndexError,
    KeyError,
    LookupError,
    NotImplementedError,
    ReferenceError,
    StandardError,
    StopIteration,
    TypeError,
    ValueError
    )

from __builtins__.exception.io import (
    EOFError,
    IOError,
    KeyboardInterrupt
    )

from __builtins__.exception.naming import (
    AttributeError,
    ImportError,
    ImportWarning,
    NameError,
    UnboundLocalError
    )

from __builtins__.exception.numeric import (
    ArithmeticError,
    FloatingPointError,
    OverflowError,
    ZeroDivisionError
    )

from __builtins__.exception.program import (
    DeprecationWarning,
    FutureWarning,
    IndentationError,
    PendingDeprecationWarning,
    SyntaxError,
    SyntaxWarning,
    TabError,
    UserWarning
    )

from __builtins__.exception.system import (
    EnvironmentError,
    MemoryError,
    OSError,
    RuntimeError,
    RuntimeWarning,
    SystemError,
    SystemExit
    )

from __builtins__.exception.unicode import (
    UnicodeDecodeError,
    UnicodeEncodeError,
    UnicodeError,
    UnicodeTranslateError,
    UnicodeWarning
    )

# vim: tabstop=4 expandtab shiftwidth=4
