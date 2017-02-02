#!/usr/bin/env python

"""
Iterator objects.

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

class itemiterator:

    "An iterator for objects providing item access."

    def __init__(self, l):

        "Initialise with the given list 'l'."

        self.l = l
        self.i = 0

    def next(self):

        "Return the next item."

        try:
            value = self.l[self.i]
            self.i += 1
            return value
        except IndexError:
            raise StopIteration()

# vim: tabstop=4 expandtab shiftwidth=4
