#!/usr/bin/env python

"""
Reference abstractions.

Copyright (C) 2016 Paul Boddie <paul@boddie.org.uk>

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

class Reference:

    "A reference abstraction."

    def __init__(self, kind, origin=None, name=None):

        """
        Initialise a reference using 'kind' to indicate the kind of object,
        'origin' to indicate the actual origin of a referenced object, and a
        'name' indicating an alias for the object in the program structure.
        """

        if isinstance(kind, Reference):
            raise ValueError, (kind, origin)
        self.kind = kind
        self.origin = origin
        self.name = name

    def __repr__(self):
        return "Reference(%r, %r, %r)" % (self.kind, self.origin, self.name)

    def __str__(self):

        """
        Serialise the reference as '<var>' or a description incorporating the
        kind and origin.
        """

        if self.kind == "<var>":
            return self.kind
        else:
            return "%s:%s" % (self.kind, self.origin)

    def __hash__(self):

        "Hash instances using the kind and origin only."

        return hash((self.kind, self.get_origin()))

    def __cmp__(self, other):

        "Compare with 'other' using the kind and origin only."

        if isinstance(other, Reference):
            return cmp((self.kind, self.get_origin()), (other.kind, other.get_origin()))
        else:
            return cmp(str(self), other)

    def get_name(self):

        "Return the name used for this reference."

        return self.name

    def get_origin(self):

        "Return the origin of the reference."

        return self.kind != "<var>" and self.origin or None

    def get_kind(self):

        "Return the kind of object referenced."

        return self.kind

    def has_kind(self, kinds):

        """
        Return whether the reference describes an object from the given 'kinds',
        where such kinds may be "<class>", "<function>", "<instance>",
        "<module>" or "<var>". Unresolved references may also have kinds of
        "<depends>" and "<invoke>".
        """

        if not isinstance(kinds, (list, tuple)):
            kinds = [kinds]
        return self.get_kind() in kinds

    def get_path(self):

        "Return the attribute names comprising the path to the origin."

        return self.get_origin().split(".")

    def unresolved(self):

        "Return whether this reference is unresolved."

        return self.has_kind(["<depends>", "<invoke>"])

    def static(self):

        "Return this reference if it refers to a static object, None otherwise."

        return not self.has_kind(["<var>", "<instance>"]) and self or None

    def final(self):

        "Return a reference to either a static object or None."

        static = self.static()
        return static and static.origin or None

    def instance_of(self):

        "Return a reference to an instance of the referenced class."

        return self.has_kind("<class>") and Reference("<instance>", self.origin) or None

    def as_var(self):

        """
        Return a variable version of this reference. Any origin information is
        discarded since variable references are deliberately ambiguous.
        """

        return Reference("<var>", None, self.name)

    def alias(self, name):

        "Alias this reference employing 'name'."

        return Reference(self.get_kind(), self.get_origin(), name)

    def mutate(self, ref):

        "Mutate this reference to have the same details as 'ref'."

        self.kind = ref.kind
        self.origin = ref.origin
        self.name = ref.name

    def parent(self):

        "Return the parent of this reference's origin."

        if not self.get_origin():
            return None

        return self.get_origin().rsplit(".", 1)[0]

    def name_parent(self):

        "Return the parent of this reference's aliased name."

        if not self.get_name():
            return None

        return self.get_name().rsplit(".", 1)[0]

    def ancestors(self):

        """
        Return ancestors of this reference's origin in order of decreasing
        depth.
        """

        if not self.get_origin():
            return None

        parts = self.get_origin().split(".")
        ancestors = []

        for i in range(len(parts) - 1, 0, -1):
            ancestors.append(".".join(parts[:i]))

        return ancestors

    def get_types(self):

        "Return class, instance-only and module types for this reference."

        class_types = self.has_kind("<class>") and [self.get_origin()] or []
        instance_types = []
        module_types = self.has_kind("<module>") and [self.get_origin()] or []
        return class_types, instance_types, module_types

def decode_reference(s, name=None):

    "Decode 's', making a reference."

    if isinstance(s, Reference):
        return s.alias(name)

    # Null value.

    elif not s:
        return Reference("<var>", None, name)

    # Kind and origin.

    elif ":" in s:
        kind, origin = s.split(":")
        return Reference(kind, origin, name)

    # Kind-only, origin is indicated name.

    elif s[0] == "<":
        return Reference(s, name, name)

    # Module-only.

    else:
        return Reference("<module>", s, name)



# Type/reference collection functions.

def is_single_class_type(all_types):

    """
    Return whether 'all_types' is a mixture of class and instance kinds for
    a single class type.
    """

    kinds = set()
    types = set()

    for type in all_types:
        kinds.add(type.get_kind())
        types.add(type.get_origin())

    return len(types) == 1 and kinds == set(["<class>", "<instance>"])

def combine_types(class_types, instance_types, module_types):

    """
    Combine 'class_types', 'instance_types', 'module_types' into a single
    list of references.
    """

    all_types = []
    for kind, l in [("<class>", class_types), ("<instance>", instance_types), ("<module>", module_types)]:
        for t in l:
            all_types.append(Reference(kind, t))
    return all_types

def separate_types(refs):

    """
    Separate 'refs' into type-specific lists, returning a tuple containing
    lists of class types, instance types, module types, function types and
    unknown "var" types.
    """

    class_types = []
    instance_types = []
    module_types = []
    function_types = []
    var_types = []

    for kind, l in [
        ("<class>", class_types), ("<instance>", instance_types), ("<module>", module_types),
        ("<function>", function_types), ("<var>", var_types)
        ]:

        for ref in refs:
            if ref.get_kind() == kind:
                l.append(ref.get_origin())

    return class_types, instance_types, module_types, function_types, var_types

# vim: tabstop=4 expandtab shiftwidth=4
