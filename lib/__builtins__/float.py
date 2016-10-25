#!/usr/bin/env python

"""
Floating point objects.

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

class float(object):
    def __init__(self, number_or_string=None):
        # Note member.
        self.__data__ = 0.0

    def __iadd__(self, other): pass
    def __isub__(self, other): pass
    def __add__(self, other): pass
    def __radd__(self, other): pass
    def __sub__(self, other): pass
    def __rsub__(self, other): pass
    def __mul__(self, other): pass
    def __rmul__(self, other): pass
    def __div__(self, other): pass
    def __rdiv__(self, other): pass
    def __floordiv__(self, other): pass
    def __rfloordiv__(self, other): pass
    def __mod__(self, other): pass
    def __rmod__(self, other): pass
    def __pow__(self, other): pass
    def __rpow__(self, other): pass
    def __lt__(self, other): pass
    def __gt__(self, other): pass
    def __le__(self, other): pass
    def __ge__(self, other): pass
    def __eq__(self, other): pass
    def __ne__(self, other): pass
    def __neg__(self): pass
    def __pos__(self): pass
    def __str__(self): pass
    def __bool__(self): pass

# vim: tabstop=4 expandtab shiftwidth=4
