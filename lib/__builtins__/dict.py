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

from __builtins__.iterator import itemiterator
from __builtins__.sequence import _max
import native

class dict:

    "A dictionary representation mapping keys to values."

    MISSING = object()

    def __init__(self, args=None):

        "Initialise the dictionary."

        self.__data__ = self._get_data(args is not None and len(args) / 2 or 0)

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

    def _get_data(self, capacity):

        """
        Reserve an attribute for a hashtable reference along with some space
        for elements.
        """

        return native._dict_init(_max(capacity, 5))

    def _get_index(self, key):

        "Check 'key' and return an index or raise TypeError."

        index = key.__hash__()
        if not native._isinstance(index, int):
            raise TypeError

        return index

    def _find_entry(self, key, index):

        "Search for 'key', using an 'index' identifying the bucket involved."

        size = native._dict_bucketsize(self.__data__, index)
        i = 0

        while i < size:
            found = native._dict_key(self.__data__, index, i)
            if found == key:
                return i
            i += 1

        return None

    def _resize(self, capacity):

        "Resize the hashtable to have the given 'capacity'."

        newdata = self._get_data(capacity)

        for key, value in self.items():
            self._setitem(newdata, key, value)

        self.__data__ = newdata

    def _setitem(self, data, key, value):

        "Set in the 'data' an item having the given 'key' and 'value'."

        # Find an index identifying the bucket involved.

        index = self._get_index(key)

        # Find the entry index within the bucket of the key.

        i = self._find_entry(key, index)

        # With no existing entry, append to the bucket.

        if i is None:
            native._dict_additem(data, index, key, value)

        # With an existing entry, replace the item.

        else:
            native._dict_setitem(data, index, i, key, value)

    def __setitem__(self, key, value):

        "Set a mapping from 'key' to 'value' in the dictionary."

        size = native._dict_items(self.__data__)
        capacity = native._dict_buckets(self.__data__)

        if size > capacity:
            self._resize(capacity * 2)

        self._setitem(self.__data__, key, value)

    def __delitem__(self, key, value): pass

    def __getitem__(self, key, default=MISSING):

        """
        Return the value stored for 'key'. If 'key' does not have an entry in
        the dictionary, a KeyError will be raised unless 'default' is specified.
        In which case, 'default' will be returned instead.
        """

        # Find an index identifying the bucket involved.

        index = self._get_index(key)

        # Find the entry index within the bucket of the key.

        i = self._find_entry(key, index)

        # With no entry index, either raise an exception or return the default.

        if i is None:
            if default is self.MISSING:
                raise KeyError(key)
            else:
                return default

        # With a valid entry index, obtain the corresponding value.

        else:
            return native._dict_value(self.__data__, index, i)

    def clear(self): pass
    def has_key(self): pass

    def keys(self):

        "Return the keys for this dictionary."

        return native._dict_keys(self.__data__)

    def values(self):

        "Return the values in this dictionary."

        return native._dict_values(self.__data__)

    def items(self):

        "Return the items, each being a (key, value) tuple, in this dictionary."

        return zip([self.keys(), self.values()])

    def get(self, key): pass
    def setdefault(self, key, value): pass
    def update(self, other): pass

    def __iter__(self):

        "Return an iterator."

        return itemiterator(self.keys())

# vim: tabstop=4 expandtab shiftwidth=4
