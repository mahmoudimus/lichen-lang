#!/usr/bin/env python

"""
Dictionary objects.

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

from __builtins__.iterator import listiterator

class dict(object):
    def __init__(self, *args): pass
    def __setitem__(self, key, value): pass
    def __delitem__(self, key, value): pass

    def __getitem__(self, key):
        # Note usage.
        KeyError

    def clear(self): pass
    def has_key(self): pass
    def keys(self): pass
    def values(self): pass
    def items(self): pass
    def get(self, key): pass
    def setdefault(self, key, value): pass
    def update(self, other): pass

    def __iter__(self):

        "Return an iterator."

        return listiterator(self.keys())

# vim: tabstop=4 expandtab shiftwidth=4
