#!/usr/bin/env python

"""
Operator support.

Copyright (C) 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

from operator.augmented import (
    iadd,
    iand_,
    idiv,
    ifloordiv,
    ilshift,
    imod,
    imul,
    ior_,
    ipow,
    irshift,
    isub,
    ixor,
    )

from operator.binary import (
    add,
    and_,
    contains,
    div,
    floordiv,
    in_,
    not_in,
    lshift,
    mod,
    mul,
    or_,
    pow,
    rshift,
    sub,
    xor,
    )

from operator.comparison import (
    eq,
    ge,
    gt,
    le,
    lt,
    ne,
    )

from operator.sequence import (
    getitem,
    setitem,
    getslice,
    setslice,
    )

from operator.unary import (
    invert,
    neg,
    not_,
    pos,
    )

# vim: tabstop=4 expandtab shiftwidth=4
