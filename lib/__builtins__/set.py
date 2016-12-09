#!/usr/bin/env python

"""
Set objects.

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

class frozenset:
    def __init__(self, iterable): pass

class set:
    def __init__(self, iterable): pass
    def add(self, item): pass
    def clear(self): pass
    def copy(self): pass
    def difference(self, other): pass
    def difference_update(self, other): pass
    def discard(self, item): pass
    def intersection(self, other): pass
    def intersection_update(self, other): pass
    def issubset(self, other): pass
    def issuperset(self, other): pass

    def __iter__(self):

        "Return an iterator."

        return itemiterator(list(self))

    def pop(self): pass
    def remove(self, item): pass
    def symmetric_difference(self, other): pass
    def symmetric_difference_update(self, other): pass
    def union(self, other): pass
    def update(self, other): pass

# vim: tabstop=4 expandtab shiftwidth=4
