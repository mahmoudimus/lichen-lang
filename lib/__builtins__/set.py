#!/usr/bin/env python

"""
Set objects.

Copyright (C) 2015, 2016, 2017, 2019 Paul Boddie <paul@boddie.org.uk>

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

    def _find_entry(self, buckets, value, index):

        """
        Search in 'buckets' for 'value', using an 'index' identifying the bucket
        involved.
        """

        i = 0

        for found in buckets[index]:
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

        index, i = self._get_entry(buckets, value)

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

        index, i = self._get_entry(self.buckets, value)
        return i is not None

    def __iter__(self):

        "Return an iterator."

        return setiterator(self)

    # Public conventional methods.

    def copy(self):

        "Return a copy of this set."

        result = set()
        result.update(self)
        return result

    def difference(self, other):

        """
        Return a set containing only those values in this set that are not in
        'other'.
        """

        result = set()

        for value in self:
            if value not in other:
                result.add(value)

        return result

    def intersection(self, other):

        "Return a set containing only those values in this set and in 'other'."

        result = set()

        for value in self:
            if value in other:
                result.add(value)

        return result

    def issubset(self, other):

        "Return whether this set is a subset of 'other'."

        for value in self:
            if value not in other:
                return False

        return True

    def issuperset(self, other):

        "Return whether this set is a superset of 'other'."

        for value in other:
            if value not in self:
                return False

        return True

    def symmetric_difference(self, other):

        """
        Return a set containing only the values either in this set or in 'other'
        but not in both.
        """

        result = set()

        for value in self:
            if value not in other:
                result.add(value)

        for value in other:
            if value not in self:
                result.add(value)

        return result

    def union(self, other):

        "Return a set combining this set and 'other'."

        result = set()

        for value in self:
            result.add(value)

        for value in other:
            result.add(value)

        return result

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

    def difference_update(self, other):

        "Remove from this set all values from 'other'."

        for value in other:
            self.discard(value)

    def discard(self, value):

        "Remove 'value' from the set, if present."

        try:
            self.remove(value)
        except KeyError:
            pass

    def intersection_update(self, other):

        "Preserve in this set only values in this set found in 'other'."

        to_remove = set()

        for value in self:
            if value not in other:
                to_remove.add(value)

        for value in to_remove:
            self.remove(value)

    def pop(self):

        "Remove and return an arbitrary value."

        # Get the last element from the first non-empty bucket.

        for bucket in self.buckets:
            if bucket:
                self.size -= 1
                return bucket.pop()

        raise KeyError

    def remove(self, value):

        "Remove 'value' from the set."

        self._remove_entry(value)

    def symmetric_difference_update(self, other):

        """
        Remove from this set all values found in 'other', adding values only
        found in 'other'.
        """

        to_add = other.difference(self)
        self.difference_update(other)
        self.update(to_add)

    def update(self, other):

        "Update this set using the contents of 'other'."

        for value in other:
            self.add(value)

class setiterator:

    "An iterator for set types."

    def __init__(self, mapping):

        "Initialise the iterator with the given 'mapping'."

        self.mapping = mapping
        self.index = 0
        self.i = 0

    def next(self):

        "Return the next value."

        while True:

            # Access the current bucket. If no such bucket exists, stop.

            try:
                bucket = self.mapping.buckets[self.index]
            except IndexError:
                raise StopIteration, self

            # Access the current item. If no such item exists, get another
            # bucket.

            try:
                value = bucket[self.i]
                self.i += 1
                return value

            except IndexError:
                self.index += 1
                self.i = 0

# vim: tabstop=4 expandtab shiftwidth=4
