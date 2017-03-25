#!/usr/bin/env python

"""
Result abstractions.

Copyright (C) 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

from referencing import Reference

# Classes representing inspection and translation observations.

class Result:

    "An abstract expression result."

    def is_name(self):
        return False

    def is_global_name(self):
        return False

    def reference(self):
        return None

    def references(self):
        return None

    def access_location(self):
        return None

    def access_locations(self):
        return None

    def context(self):
        return None

    def discards_temporary(self, test=True):
        return None

    def get_name(self):
        return None

    def get_origin(self):
        return None

    def static(self):
        return None

    def final(self):
        return None

    def has_kind(self, kinds):
        return False

class AccessRef(Result):

    """
    A reference to an attribute access that is generally only returned from a
    processed access for possible initialiser resolution for assignments.
    """

    def __init__(self, original_name, attrnames, number):
        self.original_name = original_name
        self.attrnames = attrnames
        self.number = number

    def __repr__(self):
        return "AccessRef(%r, %r, %r)" % (self.original_name, self.attrnames, self.number)

class InvocationRef(Result):

    "An invocation of a name reference."

    def __init__(self, name_ref):
        self.name_ref = name_ref

    def reference(self):
        origin = self.name_ref.get_origin()
        if origin:
            return Reference("<invoke>", origin)
        else:
            return Reference("<var>")

    def __repr__(self):
        return "InvocationRef(%r)" % self.name_ref

class NameRef(Result):

    "A reference to a name."

    def __init__(self, name, expr=None, is_global=False):
        self.name = name
        self.expr = expr
        self.is_global = is_global

    def is_name(self):
        return True

    def is_global_name(self):
        return self.is_global

    def final(self):
        return None

    def __repr__(self):
        return "NameRef(%r, %r, %r)" % (self.name, self.expr, self.is_global)

class LocalNameRef(NameRef):

    "A reference to a local name."

    def __init__(self, name, number):
        NameRef.__init__(self, name, is_global=False)
        self.number = number

    def __repr__(self):
        return "LocalNameRef(%r, %r)" % (self.name, self.number)

class ResolvedRef:

    "A resolved reference mix-in."

    def __init__(self, ref):
        self.ref = ref

    def reference(self):
        return self.ref

    def references(self):
        return [self.ref]

    def get_name(self):
        return self.ref and self.ref.get_name() or None

    def get_origin(self):
        return self.ref and self.ref.get_origin() or None

    def static(self):
        return self.ref and self.ref.static() or None

    def final(self):
        return self.ref and self.ref.final() or None

    def has_kind(self, kinds):
        return self.ref and self.ref.has_kind(kinds)

    def is_constant_alias(self):
        return self.ref and self.ref.is_constant_alias()

class ResolvedNameRef(ResolvedRef, NameRef):

    "A resolved name-based reference."

    def __init__(self, name, ref, expr=None, is_global=False):
        NameRef.__init__(self, name, expr, is_global)
        ResolvedRef.__init__(self, ref)

    def __repr__(self):
        return "ResolvedNameRef(%r, %r, %r, %r)" % (self.name, self.ref, self.expr, self.is_global)

class ConstantValueRef(ResolvedNameRef):

    "A constant reference representing a single literal value."

    def __init__(self, name, ref, value, number=None):
        ResolvedNameRef.__init__(self, name, ref)
        self.value = value
        self.number = number

    def __repr__(self):
        return "ConstantValueRef(%r, %r, %r, %r)" % (self.name, self.ref, self.value, self.number)

class InstanceRef(ResolvedRef, Result):

    "An instance reference."

    def reference(self):
        return self.ref

    def __repr__(self):
        return "InstanceRef(%r)" % self.ref

class LiteralSequenceRef(ResolvedNameRef):

    "A reference representing a sequence of values."

    def __init__(self, name, ref, node, items=None):
        ResolvedNameRef.__init__(self, name, ref)
        self.node = node
        self.items = items

    def __repr__(self):
        return "LiteralSequenceRef(%r, %r, %r, %r)" % (self.name, self.ref, self.node, self.items)

class VariableRef(Result):

    "A variable reference."

    def __repr__(self):
        return "VariableRef()"

# vim: tabstop=4 expandtab shiftwidth=4
