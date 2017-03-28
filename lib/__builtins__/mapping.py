#!/usr/bin/env python

"""
Mapping object support.

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

from __builtins__.span import _max
from native import is_int

class hashtable:

    "A dictionary representation mapping keys to values."

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

    def _get_entry(self, buckets, key):

        "Return the index and entry index as a tuple in 'buckets' for 'key'."

        # Find an index identifying the bucket involved.

        index = self._get_index(buckets, key)

        # Find the entry index within the bucket of the key.

        i = self._find_entry(buckets, key, index)

        return index, i

    def _get_index(self, buckets, key):

        """
        Find in 'buckets' the given 'key', returning an index or raising
        TypeError.
        """

        index = key.__hash__()

        if not is_int(index):
            raise TypeError

        return index % len(self.buckets)

    def _find_entry(self, buckets, key, index):

        """
        Search in 'buckets' for 'key', using an 'index' identifying the bucket
        involved.

        Method to be overridden by subclasses.
        """

        pass

    def _items(self):

        "Return the values stored in all buckets."

        l = []
        for bucket in self.buckets:
            l += bucket
        return l

    def _remove_entry(self, key):

        "Remove the entry associated with the given 'key'."

        index, i = self._get_entry(self.buckets, key)

        if index is None or i is None:
            raise KeyError, key

        del self.buckets[index][i]
        self.size -= 1

    def _resize(self, capacity):

        """
        Resize the hashtable to have the given 'capacity'.
        Method to be overridden by subclasses.
        """

        pass

    # Public special methods.

    def __len__(self):

        "Return the number of items in the mapping."

        n = 0
        for bucket in self.buckets:
            n += bucket.__len__()
        return n

    # Public conventional methods.

    def clear(self):

        "Reset the dictionary to an empty state."

        self.size = 0
        self.buckets = self._get_buckets(0)

# vim: tabstop=4 expandtab shiftwidth=4
