#!/usr/bin/env python

"""
Dictionary objects.

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

from __builtins__.iteration.iterator import itemiterator
from __builtins__.span import _max
from native import isinstance as _isinstance

class dict:

    "A dictionary representation mapping keys to values."

    MISSING = object()

    def __init__(self, args=None):

        "Initialise the dictionary."

        self.clear()

        if args is not None:
            for key, value in args:
                self.__setitem__(key, value)

    def __str__(self):

        "Return a string representation."

        b = buffer()
        b.append("{")

        first = True

        for key, value in self.items():
            if first:
                first = False
            else:
                b.append(", ")
            b.append(key.__repr__())
            b.append(" : ")
            b.append(value.__repr__())

        b.append("}")
        return str(b)

    __repr__ = __str__

    def _get_buckets(self, capacity):

        """
        Reserve an attribute for a hashtable reference along with some space
        for elements.
        """

        buckets = []
        capacity = _max(capacity, 5)
        i = 0

        while i < capacity:
            buckets.append([])
            i += 1

        return buckets

    def _get_entry(self, key):

        "Return the index and entry index as a tuple for 'key'."

        # Find an index identifying the bucket involved.

        index = self._get_index(key)

        # Find the entry index within the bucket of the key.

        i = self._find_entry(key, index)

        return index, i

    def _get_index(self, key):

        "Check 'key' and return an index or raise TypeError."

        index = key.__hash__()

        if not _isinstance(index, int):
            raise TypeError

        return index % len(self.buckets)

    def _find_entry(self, key, index):

        "Search for 'key', using an 'index' identifying the bucket involved."

        i = 0

        for found, value in self.buckets[index]:
            if found == key:
                return i
            i += 1

        return None

    def _resize(self, capacity):

        "Resize the hashtable to have the given 'capacity'."

        buckets = self._get_buckets(capacity)

        for key, value in self.items():
            self._setitem(buckets, key, value)

        self.buckets = buckets

    def _setitem(self, buckets, key, value):

        "Set in the 'buckets' an item having the given 'key' and 'value'."

        index, i = self._get_entry(key)

        # With no existing entry, append to the bucket.

        if i is None:
            buckets[index].append((key, value))
            self.size += 1

        # With an existing entry, replace the item.

        else:
            buckets[index][i] = key, value

    # Public special methods.

    def __delitem__(self, key):

        "Remove the entry associated with the given 'key' from this dictionary."

        index, i = self._get_entry(key)

        if index is None or i is None:
            raise KeyError, key

        del self.buckets[index][i]
        self.size -= 1

    def __getitem__(self, key):

        "Return the value associated with 'key' from the dictionary."

        return self.get(key, self.MISSING)

    def __iter__(self):

        "Return an iterator."

        return itemiterator(self.keys())

    def __setitem__(self, key, value):

        "Set a mapping from 'key' to 'value' in the dictionary."

        capacity = len(self.buckets)

        if self.size > capacity:
            self._resize(capacity * 2)

        self._setitem(self.buckets, key, value)

    # Public conventional methods.

    def clear(self):

        "Reset the dictionary to an empty state."

        self.size = 0
        self.buckets = self._get_buckets(0)

    def get(self, key, default=None):

        """
        Return the value stored for 'key'. If 'key' does not have an entry in
        the dictionary, 'default' will be returned instead.
        """

        index, i = self._get_entry(key)

        # With no entry index, either raise an exception or return the default.

        if i is None:
            if default is self.MISSING:
                raise KeyError(key)
            else:
                return default

        # With a valid entry index, obtain the corresponding value.

        else:
            return self.buckets[index][i][1]

    def has_key(self, key):

        "Return whether the given 'key' is used with this dictionary."

        return self.get(key) and True or False

    def keys(self):

        "Return the keys for this dictionary."

        l = []
        for key, value in self.items():
            l.append(key)
        return l

    def items(self):

        "Return the items, each being a (key, value) tuple, in this dictionary."

        l = []
        for bucket in self.buckets:
            l += bucket
        return l

    def setdefault(self, key, value): pass

    def update(self, other): pass

    def values(self):

        "Return the values in this dictionary."

        l = []
        for key, value in self.items():
            l.append(value)
        return l

# vim: tabstop=4 expandtab shiftwidth=4
