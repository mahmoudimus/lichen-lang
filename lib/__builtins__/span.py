#!/usr/bin/env python

"""
Span-related objects.

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

from __builtins__.sequence import _max, _min

class xrange:

    "Implementation of xrange."

    NO_END = object()

    def __init__(self, start_or_end, end=NO_END, step=1):

        "Initialise the xrange with the given 'start_or_end', 'end' and 'step'."

        if end is xrange.NO_END:
            self.start = 0
            self.end = start_or_end
        else:
            self.start = start_or_end
            self.end = end

        self.step = step

        # Constrain the end according to the start and step.

        if step > 0:
            self.end = _max(self.start, self.end)
        elif step < 0:
            self.end = _min(self.start, self.end)
        else:
            raise ValueError(self.step)

        self.current = self.start

    def __str__(self):

        "Return a string representation."

        b = buffer([self.__name__, "(", self.start, ", ", self.end, ", ", self.step, ")"])
        return str(b)

    __repr__ = __str__

    def __len__(self):

        "Return the length of the range."

        return (self.end - self.start) / self.step

    def __iter__(self):

        "Return an iterator, currently self."

        return self

    def next(self):

        "Return the next item or raise a StopIteration exception."

        if self.step < 0 and self.current <= self.end or self.step > 0 and self.current >= self.end:
            raise StopIteration()

        current = self.current
        self.current += self.step
        return current

class slice(xrange):

    "Implementation of slice."

    def __init__(self, start_or_end=None, end=xrange.NO_END, step=1):

        "Initialise the slice with the given 'start_or_end', 'end' and 'step'."

        get_using(xrange.__init__, self)(start_or_end, end, step)

def range(start_or_end, end=None, step=1):

    "Implementation of range."

    return list(xrange(start_or_end, end, step))

# vim: tabstop=4 expandtab shiftwidth=4
