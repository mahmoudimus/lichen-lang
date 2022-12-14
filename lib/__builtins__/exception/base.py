#!/usr/bin/env python

"""
Base exception objects. See __builtins__.core for the core exceptions.

Copyright (C) 2015, 2016, 2018, 2019 Paul Boddie <paul@boddie.org.uk>

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

class LookupError(Exception):

    "A general lookup error."

    pass

class IndexError(LookupError):

    "An error condition involving an index."

    def __init__(self, .index):

        "Initialise the exception with the given 'index'."

        pass

class KeyError(LookupError):

    "An error concerned with a dictionary key."

    def __init__(self, .key):

        "Initialise the exception with the given 'key'."

        pass

class RuntimeError(Exception):

    "A general runtime error."

    pass

class NotImplementedError(RuntimeError):

    "An error indicating an unimplemented function or method."

    def __init__(self, .name):

        "Initialise the exception with the given 'name'."

        pass

class LoopExit(Exception):

    "An exception signalling the end of iteration in a loop."

    pass

class StopIteration(Exception):

    "An exception signalling the end of iteration."

    def __init__(self, .iterator=None):

        "Initialise the exception with the given 'iterator'."

        pass

class ValueError(Exception):

    "An error concerned with a particular value."

    def __init__(self, .value):

        "Initialise the exception with the given 'value'."

        pass

# vim: tabstop=4 expandtab shiftwidth=4
