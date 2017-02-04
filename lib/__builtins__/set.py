#!/usr/bin/env python

"""
Set objects.

Copyright (C) 2015, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

from __builtins__.iteration.iterator import itemiterator
from __builtins__.mapping import hashtable

class frozenset(hashtable):

    "An immutable set representation holding a collection of distinct values."

    def __init__(self, iterable=None):

        "Initialise the set with any given 'iterable'."

        self.clear()

        if iterable is not None:
            for value in iterable:
                self._setitem(self.buckets, value)

    # Implementation methods.

    def _find_entry(self, value, index):

        "Search for 'value', using an 'index' identifying the bucket involved."

        i = 0

        for found in self.buckets[index]:
            if found == value:
                return i
            i += 1

        return None

    def _resize(self, capacity):

        "Resize the hashtable to have the given 'capacity'."

        buckets = self._get_buckets(capacity)

        for value in self._items():
            self._setitem(buckets, value)

        self.buckets = buckets

    def _setitem(self, buckets, value):

        "Set in the 'buckets' an item having the given 'value'."

        index, i = self._get_entry(value)

        # With no existing entry, append to the bucket.

        if i is None:
            buckets[index].append(value)
            self.size += 1

        # With an existing entry, replace the item.

        else:
            buckets[index][i] = value

    # String representations.

    def _str(self, name):

        "Return a string representation."

        b = buffer()
        b.append(name)
        b.append("(")
        b.append(self._items().__repr__())
        b.append(")")
        return str(b)

    def __str__(self):

        "Return a string representation."

        return self._str("frozenset")

    __repr__ = __str__

    # Public special methods.

    def __contains__(self, value):

        "Return whether 'value' is in the set."

        index, i = self._get_entry(value)
        return i is not None

    def __iter__(self):

        "Return an iterator."

        return itemiterator(list(self))

    # Public conventional methods.

    def copy(self): pass
    def difference(self, other): pass
    def intersection(self, other): pass
    def issubset(self, other): pass
    def issuperset(self, other): pass
    def symmetric_difference(self, other): pass
    def union(self, other): pass

class set(frozenset):

    "A mutable set representation holding a collection of distinct values."

    # String representation methods.

    def __str__(self):

        "Return a string representation."

        return self._str("set")

    __repr__ = __str__

    # Public conventional methods.

    def add(self, value):

        "Add the given 'value' to the set."

        capacity = len(self.buckets)

        if self.size > capacity:
            self._resize(capacity * 2)

        self._setitem(self.buckets, value)

    def difference_update(self, other): pass

    def discard(self, value):

        "Remove 'value' from the set, if present."

        try:
            self.remove(value)
        except KeyError:
            pass

    def intersection_update(self, other): pass

    def pop(self): pass

    def remove(self, value):

        "Remove 'value' from the set."

        self._remove_entry(value)

    def symmetric_difference_update(self, other): pass

    def update(self, other): pass

# vim: tabstop=4 expandtab shiftwidth=4
