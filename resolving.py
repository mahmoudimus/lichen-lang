#!/usr/bin/env python

"""
Name resolution.

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

from common import init_item, predefined_constants
from results import AccessRef, InstanceRef, InvocationRef, LocalNameRef, \
                    NameRef, ResolvedNameRef
from referencing import Reference
import sys

class NameResolving:

    "Resolving names mix-in for inspected modules."

    # Post-inspection resolution activities.

    def resolve(self):

        "Resolve dependencies and complete definitions."

        self.resolve_members()
        self.resolve_class_bases()
        self.check_special()
        self.check_names_used()
        self.check_invocations()
        self.resolve_initialisers()
        self.resolve_literals()
        self.remove_redundant_accessors()

    def resolve_members(self):

        """
        Resolve any members referring to deferred references, using information
        stored in the importer. This updates stored object and external name
        records in this module.
        """

        for impd, d in [
            (self.importer.objects, self.objects),
            (self.importer.all_name_references, self.name_references)
            ]:

            for name, ref in d.items():

                # Obtain resolved names from the importer.

                if ref.has_kind("<depends>"):
                    ref = self.importer.identify(name)
                    d[name] = ref

    def resolve_class_bases(self):

        "Resolve all class bases since some of them may have been deferred."

        for name, bases in self.classes.items():
            resolved = []
            bad = []

            for base in bases:
                ref = self.importer.identify(base.get_origin())

                # Obtain the origin of the base class reference.

                if not ref or not ref.has_kind("<class>"):
                    bad.append(base)
                    break

                resolved.append(ref)

            if bad:
                print >>sys.stderr, "Bases of class %s were not classes." % (name, ", ".join(map(str, bad)))
            else:
                self.importer.classes[name] = self.classes[name] = resolved

    def check_special(self):

        "Check special names."

        for name, value in self.special.items():
            self.special[name] = self.importer.identify(value.get_origin())

    def check_names_used(self):

        "Check the external names used by each scope."

        for key, ref in self.name_references.items():
            path, name = key.rsplit(".", 1)
            self.resolve_accesses(path, name, ref)

    def check_invocations(self):

        "Find invocations amongst module data and replace their results."

        # Find members and replace invocation results with values. This is
        # effectively the same as is done for initialised names, but refers to
        # any unchanging value after initialisation.

        for key, ref in self.objects.items():
            if ref.has_kind("<invoke>"):
                ref = self.convert_invocation(ref)
                self.importer.objects[key] = self.objects[key] = ref

        # Convert function defaults, which are effectively extra members of the
        # module, and function locals.

        for fname, parameters in self.function_defaults.items():
            l = []
            for pname, ref in parameters:
                if ref.has_kind("<invoke>"):
                    ref = self.convert_invocation(ref)
                l.append((pname, ref))
            self.function_defaults[fname] = l

        # Convert function locals referencing invocations.

        for fname, names in self.function_locals.items():
            for name, ref in names.items():
                if ref.has_kind("<invoke>"):
                    ref = self.convert_invocation(ref)
                    names[name] = ref

    def convert_invocation(self, ref):

        "Convert the given invocation 'ref', handling instantiation."

        ref = self.importer.identify(ref.get_origin())
        return ref and ref.has_kind("<class>") and ref.instance_of() or Reference("<var>")

    def resolve_accesses(self, path, name, ref):

        """
        Resolve any unresolved accesses in the function at the given 'path'
        for the given 'name' corresponding to the indicated 'ref'. Note that
        this mechanism cannot resolve things like inherited methods because
        they are not recorded as program objects in their inherited locations.
        """

        attr_accesses = self.global_attr_accesses.get(path)
        all_attrnames = attr_accesses and attr_accesses.get(name)

        if not all_attrnames:
            return

        # Insist on constant accessors.

        if not ref.has_kind(["<class>", "<module>"]):
            return

        found_attrnames = set()

        for attrnames in all_attrnames:

            # Start with the resolved name, adding attributes.

            attrs = ref.get_path()
            remaining = attrnames.split(".")
            last_ref = ref

            # Add each component, testing for a constant object.

            while remaining:
                attrname = remaining[0]
                attrs.append(attrname)
                del remaining[0]

                # Find any constant object reference.

                attr_ref = self.get_resolved_object(".".join(attrs))

                # Non-constant accessors terminate the traversal.

                if not attr_ref or not attr_ref.has_kind(["<class>", "<module>", "<function>"]):

                    # Provide the furthest constant accessor unless the final
                    # access can be resolved.

                    if remaining:
                        remaining.insert(0, attrs.pop())
                    else:
                        last_ref = attr_ref
                    break

                # Follow any reference to a constant object.
                # Where the given name refers to an object in another location,
                # switch to the other location in order to be able to test its
                # attributes.

                last_ref = attr_ref
                attrs = attr_ref.get_path()

            # Record a constant accessor only if an object was found
            # that is different from the namespace involved.

            if last_ref:
                objpath = ".".join(attrs)
                if objpath != path:

                    if last_ref.has_kind("<invoke>"):
                        last_ref = self.convert_invocation(last_ref)

                    # Establish a constant access.

                    init_item(self.const_accesses, path, dict)
                    self.const_accesses[path][(name, attrnames)] = (objpath, last_ref, ".".join(remaining))

                    if len(attrs) > 1:
                        found_attrnames.add(attrs[1])

        # Remove any usage records for the name.

        if found_attrnames:

            # NOTE: Should be only one name version.

            versions = []
            for version in self.attr_usage[path][name]:
                new_usage = set()
                for usage in version:
                    if found_attrnames.intersection(usage):
                        new_usage.add(tuple(set(usage).difference(found_attrnames)))
                    else:
                        new_usage.add(usage)
                versions.append(new_usage)

            self.attr_usage[path][name] = versions

    def resolve_initialisers(self):

        "Resolve initialiser values for names."

        # Get the initialisers in each namespace.

        for path, name_initialisers in self.name_initialisers.items():
            const_accesses = self.const_accesses.get(path)

            # Resolve values for each name in a scope.

            for name, values in name_initialisers.items():
                if path == self.name:
                    assigned_path = name
                else:
                    assigned_path = "%s.%s" % (path, name)

                initialised_names = {}
                aliased_names = {}

                for i, name_ref in enumerate(values):

                    # Unwrap invocations.

                    if isinstance(name_ref, InvocationRef):
                        invocation = True
                        name_ref = name_ref.name_ref
                    else:
                        invocation = False

                    # Obtain a usable reference from names or constants.

                    if isinstance(name_ref, ResolvedNameRef):
                        if not name_ref.reference():
                            continue
                        ref = name_ref.reference()

                    # Obtain a reference from instances.

                    elif isinstance(name_ref, InstanceRef):
                        if not name_ref.reference():
                            continue
                        ref = name_ref.reference()

                    # Resolve accesses that employ constants.

                    elif isinstance(name_ref, AccessRef):
                        ref = None

                        if const_accesses:
                            resolved_access = const_accesses.get((name_ref.original_name, name_ref.attrnames))
                            if resolved_access:
                                objpath, ref, remaining_attrnames = resolved_access
                                if remaining_attrnames:
                                    ref = None

                        # Accesses that do not employ constants cannot be resolved,
                        # but they may be resolvable later.

                        if not ref:
                            if not invocation:
                                aliased_names[i] = name_ref.original_name, name_ref.attrnames, name_ref.number
                            continue

                    # Attempt to resolve a plain name reference.

                    elif isinstance(name_ref, LocalNameRef):
                        key = "%s.%s" % (path, name_ref.name)
                        origin = self.name_references.get(key)

                        # Accesses that do not refer to known static objects
                        # cannot be resolved, but they may be resolvable later.

                        if not origin:
                            if not invocation:
                                aliased_names[i] = name_ref.name, None, name_ref.number
                            continue

                        ref = self.get_resolved_object(origin)
                        if not ref:
                            continue

                    elif isinstance(name_ref, NameRef):
                        key = "%s.%s" % (path, name_ref.name)
                        origin = self.name_references.get(key)
                        if not origin:
                            continue

                        ref = self.get_resolved_object(origin)
                        if not ref:
                            continue

                    else:
                        continue

                    # Resolve any hidden dependencies involving external objects
                    # or unresolved names referring to globals or built-ins.

                    if ref.has_kind("<depends>"):
                        ref = self.importer.identify(ref.get_origin())

                    # Convert class invocations to instances.

                    if invocation:
                        ref = self.convert_invocation(ref)

                    if ref and not ref.has_kind("<var>"):
                        initialised_names[i] = ref

                if initialised_names:
                    self.initialised_names[assigned_path] = initialised_names
                if aliased_names:
                    self.aliased_names[assigned_path] = aliased_names

    def resolve_literals(self):

        "Resolve constant value types."

        # Get the constants defined in each namespace.

        for path, constants in self.constants.items():
            for constant, n in constants.items():
                objpath = "%s.$c%d" % (path, n)
                _constant, value_type = self.constant_values[objpath]
                self.initialised_names[objpath] = {0 : Reference("<instance>", value_type)}

        # Get the literals defined in each namespace.

        for path, literals in self.literals.items():
            for n in range(0, literals):
                objpath = "%s.$C%d" % (path, n)
                value_type = self.literal_types[objpath]
                self.initialised_names[objpath] = {0 : Reference("<instance>", value_type)}

    def remove_redundant_accessors(self):

        "Remove now-redundant modifier and accessor information."

        for path, const_accesses in self.const_accesses.items():
            accesses = self.attr_accessors.get(path)
            modifiers = self.attr_access_modifiers.get(path)
            if not accesses:
                continue
            for access in const_accesses.keys():
                if accesses.has_key(access):
                    del accesses[access]
                if modifiers and modifiers.has_key(access):
                    del modifiers[access]

    # Object resolution.

    def get_resolved_object(self, path):

        """
        Get the details of an object with the given 'path' within this module.
        Where the object has not been resolved, None is returned. This differs
        from the get_object method used elsewhere in that it does not return an
        unresolved object reference.
        """

        if self.objects.has_key(path):
            ref = self.objects[path]
            if ref.has_kind("<depends>"):
                return None
            else:
                return ref
        else:
            return None

# vim: tabstop=4 expandtab shiftwidth=4
