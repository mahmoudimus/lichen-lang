#!/usr/bin/env python

"""
Span-related objects.

Copyright (C) 2015, 2016, 2017, 2018, 2019 Paul Boddie <paul@boddie.org.uk>

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

class slice:

    "Implementation of slice."

    NO_END = object()

    def __init__(self, start_or_end=None, end=NO_END, step=1):

        "Initialise the slice with the given 'start_or_end', 'end' and 'step'."

        if end is slice.NO_END:
            self.start = 0
            self.end = start_or_end
        else:
            self.start = start_or_end
            self.end = end

        if step == 0:
            raise ValueError(self.step)

        self.step = step

    def __str__(self):

        "Return a string representation."

        return "%s.%s(%r, %r, %r)" % (self.__parent__.__name__, self.__name__,
                                      self.start,  self.end, self.step)

    __repr__ = __str__

class xrange(slice):

    "Implementation of xrange."

    def __init__(self, start_or_end, end=slice.NO_END, step=1):

        "Initialise the xrange with the given 'start_or_end', 'end' and 'step'."

        get_using(slice.__init__, self)(start_or_end, end, step)

        # Constrain the end according to the start and step.

        if step > 0:
            self.end = _max(self.start, self.end)
        elif step < 0:
            self.end = _min(self.start, self.end)
        else:
            raise ValueError(self.step)

    def __len__(self):

        "Return the length of the range."

        n = (self.end - self.start) / self.step
        last = self.start + (n * self.step)
        if last == self.end:
            return n
        else:
            return n + 1

    def __iter__(self):

        "Return an iterator, currently self."

        return xrangeiterator(self.start, self.step, self.__len__())

class xrangeiterator:

    "An iterator over an xrange."

    def __init__(self, start, .step, .count):

        "Initialise the iterator with the given 'start', 'step' and 'count'."

        self.current = start

    def next(self):

        "Return the next item or raise a StopIteration exception."

        if not self.count:
            raise StopIteration, self

        current = self.current
        self.current = self.current.__add__(self.step)
        self.count = self.count.__sub__(1)
        return current

def range(start_or_end, end=None, step=1):

    "Implementation of range."

    return list(xrange(start_or_end, end, step))

def _max(x, y):

    "Return the maximum of 'x' and 'y'."

    if x >= y:
        return x
    else:
        return y

def _min(x, y):

    "Return the minimum of 'x' and 'y'."

    if x <= y:
        return x
    else:
        return y

# vim: tabstop=4 expandtab shiftwidth=4
