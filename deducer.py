#!/usr/bin/env python

"""
Deduce types for usage observations.

Copyright (C) 2014, 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

from common import first, get_attrname_from_location, get_attrnames, \
                   get_invoked_attributes, get_name_path, init_item, \
                   sorted_output, CommonOutput
from encoders import encode_attrnames, encode_access_location, \
                     encode_constrained, encode_location, encode_usage, \
                     get_kinds, test_for_kinds, test_for_type
from errors import DeduceError
from os.path import join
from referencing import combine_types, is_single_class_type, separate_types, \
                        Reference

class Deducer(CommonOutput):

    "Deduce types in a program."

    def __init__(self, importer, output):

        """
        Initialise an instance using the given 'importer' that will perform
        deductions on the program information, writing the results to the given
        'output' directory.
        """

        self.importer = importer
        self.output = output

        # Descendants of classes.

        self.descendants = {}
        self.init_descendants()
        self.init_special_attributes()

        # Map locations to usage in order to determine specific types.

        self.location_index = {}

        # Map access locations to definition locations.

        self.access_index = {}

        # Map aliases to accesses that define them.

        self.alias_index = {}

        # Map constant accesses to redefined accesses.

        self.const_accesses = {}
        self.const_accesses_rev = {}

        # Map usage observations to assigned attributes.

        self.assigned_attrs = {}

        # Map usage observations to objects.

        self.attr_class_types = {}
        self.attr_instance_types = {}
        self.attr_module_types = {}

        # Modified attributes from usage observations.

        self.modified_attributes = {}

        # Accesses that are assignments.

        self.reference_assignments = set()

        # Map locations to types, constrained indicators and attributes.

        self.accessor_class_types = {}
        self.accessor_instance_types = {}
        self.accessor_module_types = {}
        self.provider_class_types = {}
        self.provider_instance_types = {}
        self.provider_module_types = {}
        self.accessor_constrained = set()
        self.access_constrained = set()
        self.referenced_attrs = {}
        self.referenced_objects = {}

        # Details of access operations.

        self.access_plans = {}

        # Accumulated information about accessors and providers.

        self.accessor_general_class_types = {}
        self.accessor_general_instance_types = {}
        self.accessor_general_module_types = {}
        self.accessor_all_types = {}
        self.accessor_all_general_types = {}
        self.provider_all_types = {}
        self.accessor_guard_tests = {}

        # Accumulated information about accessed attributes and
        # access/attribute-specific accessor tests.

        self.reference_all_attrs = {}
        self.reference_all_attrtypes = {}
        self.reference_all_accessor_types = {}
        self.reference_all_accessor_general_types = {}
        self.reference_test_types = {}
        self.reference_test_accessor_type = {}

        # The processing workflow itself.

        self.init_usage_index()
        self.init_accessors()
        self.init_accesses()
        self.init_aliases()
        self.init_attr_type_indexes()
        self.modify_mutated_attributes()
        self.identify_references()
        self.classify_accessors()
        self.classify_accesses()
        self.initialise_access_plans()

    def to_output(self):

        "Write the output files using deduction information."

        self.check_output()

        self.write_mutations()
        self.write_accessors()
        self.write_accesses()
        self.write_access_plans()

    def write_mutations(self):

        """
        Write mutation-related output in the following format:

        qualified name " " original object type

        Object type can be "<class>", "<function>" or "<var>".
        """

        f = open(join(self.output, "mutations"), "w")
        try:
            attrs = self.modified_attributes.items()
            attrs.sort()

            for attr, value in attrs:
                print >>f, attr, value
        finally:
            f.close()

    def write_accessors(self):

        """
        Write reference-related output in the following format for types:

        location " " ( "constrained" | "deduced" ) " " attribute type " " most general type names " " number of specific types

        Note that multiple lines can be given for each location, one for each
        attribute type.

        Locations have the following format:

        qualified name of scope "." local name ":" name version

        The attribute type can be "<class>", "<instance>", "<module>" or "<>",
        where the latter indicates an absence of suitable references.

        Type names indicate the type providing the attributes, being either a
        class or module qualified name.

        ----

        A summary of accessor types is formatted as follows:

        location " " ( "constrained" | "deduced" ) " " ( "specific" | "common" | "unguarded" ) " " most general type names " " number of specific types

        This summary groups all attribute types (class, instance, module) into a
        single line in order to determine the complexity of identifying an
        accessor.

        ----

        References that cannot be supported by any types are written to a
        warnings file in the following format:

        location

        ----

        For each location where a guard would be asserted to guarantee the
        nature of an object, the following format is employed:

        location " " ( "specific" | "common" ) " " object kind " " object types

        Object kind can be "<class>", "<instance>" or "<module>".
        """

        f_type_summary = open(join(self.output, "type_summary"), "w")
        f_types = open(join(self.output, "types"), "w")
        f_warnings = open(join(self.output, "type_warnings"), "w")
        f_guards = open(join(self.output, "guards"), "w")

        try:
            locations = self.accessor_class_types.keys()
            locations.sort()

            for location in locations:
                constrained = location in self.accessor_constrained

                # Accessor information.

                class_types = self.accessor_class_types[location]
                instance_types = self.accessor_instance_types[location]
                module_types = self.accessor_module_types[location]

                general_class_types = self.accessor_general_class_types[location]
                general_instance_types = self.accessor_general_instance_types[location]
                general_module_types = self.accessor_general_module_types[location]

                all_types = self.accessor_all_types[location]
                all_general_types = self.accessor_all_general_types[location]

                if class_types:
                    print >>f_types, encode_location(location), encode_constrained(constrained), "<class>", \
                        sorted_output(general_class_types), len(class_types)

                if instance_types:
                    print >>f_types, encode_location(location), encode_constrained(constrained), "<instance>", \
                        sorted_output(general_instance_types), len(instance_types)

                if module_types:
                    print >>f_types, encode_location(location), encode_constrained(constrained), "<module>", \
                        sorted_output(general_module_types), len(module_types)

                if not all_types:
                    print >>f_types, encode_location(location), "deduced", "<>", 0
                    attrnames = list(self.location_index[location])
                    attrnames.sort()
                    print >>f_warnings, encode_location(location), "; ".join(map(encode_usage, attrnames))

                guard_test = self.accessor_guard_tests.get(location)

                # Write specific type guard details.

                if guard_test and guard_test.startswith("specific"):
                    print >>f_guards, encode_location(location), guard_test, \
                        get_kinds(all_types)[0], \
                        sorted_output(all_types)

                # Write common type guard details.

                elif guard_test and guard_test.startswith("common"):
                    print >>f_guards, encode_location(location), guard_test, \
                        get_kinds(all_general_types)[0], \
                        sorted_output(all_general_types)

                print >>f_type_summary, encode_location(location), encode_constrained(constrained), \
                    guard_test or "unguarded", sorted_output(all_general_types), len(all_types)

        finally:
            f_type_summary.close()
            f_types.close()
            f_warnings.close()
            f_guards.close()

    def write_accesses(self):

        """
        Specific attribute output is produced in the following format:

        location " " ( "constrained" | "deduced" ) " " attribute type " " attribute references

        Note that multiple lines can be given for each location and attribute
        name, one for each attribute type.

        Locations have the following format:

        qualified name of scope "." local name " " attribute name ":" access number

        The attribute type can be "<class>", "<instance>", "<module>" or "<>",
        where the latter indicates an absence of suitable references.

        Attribute references have the following format:

        object type ":" qualified name

        Object type can be "<class>", "<function>" or "<var>".

        ----

        A summary of attributes is formatted as follows:

        location " " attribute name " " ( "constrained" | "deduced" ) " " test " " attribute references

        This summary groups all attribute types (class, instance, module) into a
        single line in order to determine the complexity of each access.

        Tests can be "validate", "specific", "untested", "guarded-validate" or "guarded-specific".

        ----

        For each access where a test would be asserted to guarantee the
        nature of an attribute, the following formats are employed:

        location " " attribute name " " "validate"
        location " " attribute name " " "specific" " " attribute type " " object type

        ----

        References that cannot be supported by any types are written to a
        warnings file in the following format:

        location
        """

        f_attr_summary = open(join(self.output, "attribute_summary"), "w")
        f_attrs = open(join(self.output, "attributes"), "w")
        f_tests = open(join(self.output, "tests"), "w")
        f_warnings = open(join(self.output, "attribute_warnings"), "w")

        try:
            locations = self.referenced_attrs.keys()
            locations.sort()

            for location in locations:
                constrained = location in self.access_constrained

                # Attribute information, both name-based and anonymous.

                referenced_attrs = self.referenced_attrs[location]

                if referenced_attrs:
                    attrname = get_attrname_from_location(location)

                    all_accessed_attrs = self.reference_all_attrs[location]

                    for attrtype, attrs in self.get_referenced_attrs(location):
                        print >>f_attrs, encode_access_location(location), encode_constrained(constrained), attrtype, sorted_output(attrs)

                    test_type = self.reference_test_types.get(location)

                    # Write the need to test at run time.

                    if test_type == "validate":
                        print >>f_tests, encode_access_location(location), test_type

                    # Write any type checks for anonymous accesses.

                    elif test_type and self.reference_test_accessor_type.get(location):
                        print >>f_tests, encode_access_location(location), test_type, \
                            sorted_output(all_accessed_attrs), \
                            self.reference_test_accessor_type[location]

                    print >>f_attr_summary, encode_access_location(location), encode_constrained(constrained), \
                        test_type or "untested", sorted_output(all_accessed_attrs)

                else:
                    print >>f_warnings, encode_access_location(location)

        finally:
            f_attr_summary.close()
            f_attrs.close()
            f_tests.close()
            f_warnings.close()

    def write_access_plans(self):

        """
        Each attribute access is written out as a plan of the following form:

        location " " name " " test " " test type " " base " " traversed attributes
                 " " attributes to traverse " " context " " access method
                 " " static attribute
        """

        f_attrs = open(join(self.output, "attribute_plans"), "w")

        try:
            locations = self.access_plans.keys()
            locations.sort()

            for location in locations:
                name, test, test_type, base, traversed, traversal_modes, attrnames, context, \
                    first_method, final_method, attr = self.access_plans[location]

                print >>f_attrs, encode_access_location(location), \
                                 name, test, test_type or "{}", \
                                 base or "{}", \
                                 ".".join(traversed) or "{}", \
                                 ".".join(traversal_modes) or "{}", \
                                 ".".join(attrnames) or "{}", \
                                 context, first_method, final_method, attr or "{}"

        finally:
            f_attrs.close()

    def classify_accessors(self):

        "For each program location, classify accessors."

        # Where instance and module types are defined, class types are also
        # defined. See: init_definition_details

        locations = self.accessor_class_types.keys()

        for location in locations:
            constrained = location in self.accessor_constrained

            # Provider information.

            class_types = self.provider_class_types[location]
            instance_types = self.provider_instance_types[location]
            module_types = self.provider_module_types[location]

            # Collect specific and general type information.

            self.provider_all_types[location] = \
                combine_types(class_types, instance_types, module_types)

            # Accessor information.

            class_types = self.accessor_class_types[location]
            self.accessor_general_class_types[location] = \
                general_class_types = self.get_most_general_class_types(class_types)

            instance_types = self.accessor_instance_types[location]
            self.accessor_general_instance_types[location] = \
                general_instance_types = self.get_most_general_class_types(instance_types)

            module_types = self.accessor_module_types[location]
            self.accessor_general_module_types[location] = \
                general_module_types = self.get_most_general_module_types(module_types)

            # Collect specific and general type information.

            self.accessor_all_types[location] = all_types = \
                combine_types(class_types, instance_types, module_types)

            self.accessor_all_general_types[location] = all_general_types = \
                combine_types(general_class_types, general_instance_types, general_module_types)

            # Record guard information.

            if not constrained:

                # Record specific type guard details.

                if len(all_types) == 1:
                    self.accessor_guard_tests[location] = test_for_type("specific", first(all_types))
                elif is_single_class_type(all_types):
                    self.accessor_guard_tests[location] = "specific-object"

                # Record common type guard details.

                elif len(all_general_types) == 1:
                    self.accessor_guard_tests[location] = test_for_type("common", first(all_types))
                elif is_single_class_type(all_general_types):
                    self.accessor_guard_tests[location] = "common-object"

                # Otherwise, no convenient guard can be defined.

    def classify_accesses(self):

        "For each program location, classify accesses."

        # Attribute accesses use potentially different locations to those of
        # accessors.

        locations = self.referenced_attrs.keys()

        for location in locations:
            constrained = location in self.access_constrained

            # Combine type information from all accessors supplying the access.

            accessor_locations = self.get_accessors_for_access(location)

            all_provider_types = set()
            all_accessor_types = set()
            all_accessor_general_types = set()

            for accessor_location in accessor_locations:

                # Obtain the provider types for guard-related attribute access
                # checks.

                all_provider_types.update(self.provider_all_types.get(accessor_location))

                # Obtain the accessor guard types (specific and general).

                all_accessor_types.update(self.accessor_all_types.get(accessor_location))
                all_accessor_general_types.update(self.accessor_all_general_types.get(accessor_location))

            # Obtain basic properties of the types involved in the access.

            single_accessor_type = len(all_accessor_types) == 1
            single_accessor_class_type = is_single_class_type(all_accessor_types)
            single_accessor_general_type = len(all_accessor_general_types) == 1
            single_accessor_general_class_type = is_single_class_type(all_accessor_general_types)

            # Determine whether the attribute access is guarded or not.

            guarded = (
                single_accessor_type or single_accessor_class_type or
                single_accessor_general_type or single_accessor_general_class_type
                )

            if guarded:
                (guard_class_types, guard_instance_types, guard_module_types,
                    _function_types, _var_types) = separate_types(all_provider_types)

            self.reference_all_accessor_types[location] = all_accessor_types
            self.reference_all_accessor_general_types[location] = all_accessor_general_types

            # Attribute information, both name-based and anonymous.

            referenced_attrs = self.referenced_attrs[location]

            if not referenced_attrs:
                raise DeduceError, repr(location)

            # Record attribute information for each name used on the
            # accessor.

            attrname = get_attrname_from_location(location)

            all_accessed_attrs = set()
            all_providers = set()

            # Obtain provider and attribute details for this kind of
            # object.

            for attrtype, object_type, attr in referenced_attrs:
                all_accessed_attrs.add(attr)
                all_providers.add(object_type)

            all_general_providers = self.get_most_general_types(all_providers)

            # Determine which attributes would be provided by the
            # accessor types upheld by a guard.

            if guarded:
                guard_attrs = set()
                for _attrtype, object_type, attr in \
                    self._identify_reference_attribute(attrname, guard_class_types, guard_instance_types, guard_module_types):
                    guard_attrs.add(attr)
            else:
                guard_attrs = None

            self.reference_all_attrs[location] = all_accessed_attrs

            # Constrained accesses guarantee the nature of the accessor.
            # However, there may still be many types involved.

            if constrained:
                if single_accessor_type:
                    self.reference_test_types[location] = test_for_type("constrained-specific", first(all_accessor_types))
                elif single_accessor_class_type:
                    self.reference_test_types[location] = "constrained-specific-object"
                elif single_accessor_general_type:
                    self.reference_test_types[location] = test_for_type("constrained-common", first(all_accessor_general_types))
                elif single_accessor_general_class_type:
                    self.reference_test_types[location] = "constrained-common-object"
                else:
                    self.reference_test_types[location] = "constrained-many"

            # Suitably guarded accesses, where the nature of the
            # accessor can be guaranteed, do not require the attribute
            # involved to be validated. Otherwise, for unguarded
            # accesses, access-level tests are required.

            elif guarded and all_accessed_attrs.issubset(guard_attrs):
                if single_accessor_type:
                    self.reference_test_types[location] = test_for_type("guarded-specific", first(all_accessor_types))
                elif single_accessor_class_type:
                    self.reference_test_types[location] = "guarded-specific-object"
                elif single_accessor_general_type:
                    self.reference_test_types[location] = test_for_type("guarded-common", first(all_accessor_general_types))
                elif single_accessor_general_class_type:
                    self.reference_test_types[location] = "guarded-common-object"

            # Record the need to test the type of anonymous and
            # unconstrained accessors.

            elif len(all_providers) == 1:
                provider = first(all_providers)
                if provider != '__builtins__.object':
                    all_accessor_kinds = set(get_kinds(all_accessor_types))
                    if len(all_accessor_kinds) == 1:
                        test_type = test_for_kinds("specific", all_accessor_kinds)
                    else:
                        test_type = "specific-object"
                    self.reference_test_types[location] = test_type
                    self.reference_test_accessor_type[location] = provider

            elif len(all_general_providers) == 1:
                provider = first(all_general_providers)
                if provider != '__builtins__.object':
                    all_accessor_kinds = set(get_kinds(all_accessor_general_types))
                    if len(all_accessor_kinds) == 1:
                        test_type = test_for_kinds("common", all_accessor_kinds)
                    else:
                        test_type = "common-object"
                    self.reference_test_types[location] = test_type
                    self.reference_test_accessor_type[location] = provider

            # Record the need to test the identity of the attribute.

            else:
                self.reference_test_types[location] = "validate"

    def initialise_access_plans(self):

        "Define attribute access plans."

        for location in self.referenced_attrs.keys():
            original_location = self.const_accesses_rev.get(location)
            self.access_plans[original_location or location] = self.get_access_plan(location)

    def get_referenced_attrs(self, location):

        """
        Return attributes referenced at the given access 'location' by the given
        'attrname' as a list of (attribute type, attribute set) tuples.
        """

        d = {}
        for attrtype, objtype, attr in self.referenced_attrs[location]:
            init_item(d, attrtype, set)
            d[attrtype].add(attr)
        l = d.items()
        l.sort() # class, module, instance
        return l

    # Initialisation methods.

    def init_descendants(self):

        "Identify descendants of each class."

        for name in self.importer.classes.keys():
            self.get_descendants_for_class(name)

    def get_descendants_for_class(self, name):

        """
        Use subclass information to deduce the descendants for the class of the
        given 'name'.
        """

        if not self.descendants.has_key(name):
            descendants = set()

            for subclass in self.importer.subclasses[name]:
                descendants.update(self.get_descendants_for_class(subclass))
                descendants.add(subclass)

            self.descendants[name] = descendants

        return self.descendants[name]

    def init_special_attributes(self):

        "Add special attributes to the classes for inheritance-related tests."

        all_class_attrs = self.importer.all_class_attrs

        for name, descendants in self.descendants.items():
            for descendant in descendants:
                all_class_attrs[descendant]["#%s" % name] = name

        for name in all_class_attrs.keys():
            all_class_attrs[name]["#%s" % name] = name

    def init_usage_index(self):

        """
        Create indexes for module and function attribute usage and for anonymous
        accesses.
        """

        for module in self.importer.get_modules():
            for path, assignments in module.attr_usage.items():
                self.add_usage(assignments, path)

        for location, all_attrnames in self.importer.all_attr_accesses.items():
            for attrnames in all_attrnames:
                attrname = get_attrnames(attrnames)[-1]
                access_location = (location, None, attrnames, 0)
                self.add_usage_term(access_location, ((attrname, False),))

    def add_usage(self, assignments, path):

        """
        Collect usage from the given 'assignments', adding 'path' details to
        each record if specified. Add the usage to an index mapping to location
        information, as well as to an index mapping locations to usages.
        """

        for name, versions in assignments.items():
            for i, usages in enumerate(versions):
                location = (path, name, None, i)

                for usage in usages:
                    self.add_usage_term(location, usage)

    def add_usage_term(self, location, usage):

        """
        For 'location' and using 'usage' as a description of usage, record
        in the usage index a mapping from the usage to 'location', and record in
        the location index a mapping from 'location' to the usage.
        """

        init_item(self.location_index, location, set)
        self.location_index[location].add(usage)

    def init_accessors(self):

        "Create indexes for module and function accessor information."

        for module in self.importer.get_modules():
            for path, all_accesses in module.attr_accessors.items():
                self.add_accessors(all_accesses, path)

    def add_accessors(self, all_accesses, path):

        """
        For attribute accesses described by the mapping of 'all_accesses' from
        name details to accessor details, record the locations of the accessors
        for each access.
        """

        # Get details for each access combining the given name and attribute.

        for (name, attrnames), accesses in all_accesses.items():

            # Obtain the usage details using the access information.

            for access_number, versions in enumerate(accesses):
                access_location = (path, name, attrnames, access_number)
                locations = []

                for version in versions:
                    location = (path, name, None, version)
                    locations.append(location)

                self.access_index[access_location] = locations

    def get_accessors_for_access(self, access_location):

        "Find a definition providing accessor details, if necessary."

        try:
            return self.access_index[access_location]
        except KeyError:
            return [access_location]

    def init_accesses(self):

        """
        Initialise collections for accesses involving assignments.
        """

        # For each scope, obtain access details.

        for path, all_accesses in self.importer.all_attr_access_modifiers.items():

            # For each combination of name and attribute names, obtain
            # applicable modifiers.

            for (name, attrnames), modifiers in all_accesses.items():

                # For each access, determine the name versions affected by
                # assignments.

                for access_number, assignment in enumerate(modifiers):
                    if name:
                        access_location = (path, name, attrnames, access_number)
                    else:
                        access_location = (path, None, attrnames, 0)

                    if assignment:
                        self.reference_assignments.add(access_location)

                    # Associate assignments with usage.

                    accessor_locations = self.get_accessors_for_access(access_location)

                    for location in accessor_locations:
                        for usage in self.location_index[location]:
                            if assignment:
                                init_item(self.assigned_attrs, usage, set)
                                self.assigned_attrs[usage].add((path, name, attrnames))

    def init_aliases(self):

        "Expand aliases so that alias-based accesses can be resolved."

        # Get aliased names with details of their accesses.

        for name_path, all_aliases in self.importer.all_aliased_names.items():
            path, name = name_path.rsplit(".", 1)

            # For each version of the name, obtain the access location.

            for version, (original_name, attrnames, access_number) in all_aliases.items():
                accessor_location = (path, name, None, version)
                access_location = (path, original_name, attrnames, access_number)
                init_item(self.alias_index, accessor_location, list)
                self.alias_index[accessor_location].append(access_location)

        # Get aliases in terms of non-aliases and accesses.

        for accessor_location, access_locations in self.alias_index.items():
            self.update_aliases(accessor_location, access_locations)

    def update_aliases(self, accessor_location, access_locations, visited=None):

        """
        Update the given 'accessor_location' defining an alias, update
        'access_locations' to refer to non-aliases, following name references
        via the access index.

        If 'visited' is specified, it contains a set of accessor locations (and
        thus keys to the alias index) that are currently being defined.
        """

        if visited is None:
            visited = set()

        updated_locations = set()

        for access_location in access_locations:
            (path, original_name, attrnames, access_number) = access_location

            # Where an alias refers to a name access, obtain the original name
            # version details.

            if attrnames is None:

                # For each name version, attempt to determine any accesses that
                # initialise the name.

                for name_accessor_location in self.access_index[access_location]:

                    # Already-visited aliases do not contribute details.

                    if name_accessor_location in visited:
                        continue

                    visited.add(name_accessor_location)

                    name_access_locations = self.alias_index.get(name_accessor_location)
                    if name_access_locations:
                        updated_locations.update(self.update_aliases(name_accessor_location, name_access_locations, visited))
                    else:
                        updated_locations.add(name_accessor_location)

            # Otherwise, record the access details.

            else:
                updated_locations.add(access_location)

        self.alias_index[accessor_location] = updated_locations
        return updated_locations

    # Attribute mutation for types.

    def modify_mutated_attributes(self):

        "Identify known, mutated attributes and change their state."

        # Usage-based accesses.

        for usage, all_attrnames in self.assigned_attrs.items():
            if not usage:
                continue

            for path, name, attrnames in all_attrnames:
                class_types = self.get_class_types_for_usage(usage)
                only_instance_types = set(self.get_instance_types_for_usage(usage)).difference(class_types)
                module_types = self.get_module_types_for_usage(usage)

                # Detect self usage within methods in order to narrow the scope
                # of the mutation.

                t = name == "self" and self.constrain_self_reference(path, class_types, only_instance_types)
                if t:
                    class_types, only_instance_types, module_types, constrained = t
                objects = set(class_types).union(only_instance_types).union(module_types)

                self.mutate_attribute(objects, attrnames)

    def mutate_attribute(self, objects, attrnames):

        "Mutate static 'objects' with the given 'attrnames'."

        for name in objects:
            attr = "%s.%s" % (name, attrnames)
            value = self.importer.get_object(attr)

            # If the value is None, the attribute is
            # inherited and need not be set explicitly on
            # the class concerned.

            if value:
                self.modified_attributes[attr] = value
                self.importer.set_object(attr, value.as_var())

    # Simplification of types.

    def get_most_general_types(self, types):

        "Return the most general types for the given 'types'."

        module_types = set()
        class_types = set()

        for type in types:
            ref = self.importer.identify(type)
            if ref.has_kind("<module>"):
                module_types.add(type)
            else:
                class_types.add(type)

        types = set(self.get_most_general_module_types(module_types))
        types.update(self.get_most_general_class_types(class_types))
        return types

    def get_most_general_class_types(self, class_types):

        "Return the most general types for the given 'class_types'."

        class_types = set(class_types)
        to_remove = set()

        for class_type in class_types:
            for base in self.importer.classes[class_type]:
                base = base.get_origin()
                descendants = self.descendants[base]
                if base in class_types and descendants.issubset(class_types):
                    to_remove.update(descendants)

        class_types.difference_update(to_remove)
        return class_types

    def get_most_general_module_types(self, module_types):

        "Return the most general type for the given 'module_types'."

        # Where all modules are provided, an object would provide the same
        # attributes.

        if len(module_types) == len(self.importer.modules):
            return ["__builtins__.object"]
        else:
            return module_types

    # More efficient usage-to-type indexing and retrieval.

    def init_attr_type_indexes(self):

        "Identify the types that can support each attribute name."

        self._init_attr_type_index(self.attr_class_types, self.importer.all_class_attrs)
        self._init_attr_type_index(self.attr_instance_types, self.importer.all_combined_attrs)
        self._init_attr_type_index(self.attr_module_types, self.importer.all_module_attrs)

    def _init_attr_type_index(self, attr_types, attrs):

        """
        Initialise the 'attr_types' attribute-to-types mapping using the given
        'attrs' type-to-attributes mapping.
        """

        for name, attrnames in attrs.items():
            for attrname in attrnames:
                init_item(attr_types, attrname, set)
                attr_types[attrname].add(name)

    def get_class_types_for_usage(self, usage):

        "Return names of classes supporting the given 'usage'."

        return self._get_types_for_usage(usage, self.attr_class_types, self.importer.all_class_attrs)

    def get_instance_types_for_usage(self, usage):

        """
        Return names of classes whose instances support the given 'usage'
        (as either class or instance attributes).
        """

        return self._get_types_for_usage(usage, self.attr_instance_types, self.importer.all_combined_attrs)

    def get_module_types_for_usage(self, usage):

        "Return names of modules supporting the given 'usage'."

        return self._get_types_for_usage(usage, self.attr_module_types, self.importer.all_module_attrs)

    def _get_types_for_usage(self, usage, attr_types, attrs):

        """
        For the given 'usage' representing attribute usage, return types
        recorded in the 'attr_types' attribute-to-types mapping that support
        such usage, with the given 'attrs' type-to-attributes mapping used to
        quickly assess whether a type supports all of the stated attributes.
        """

        # Where no attributes are used, any type would be acceptable.

        if not usage:
            return attrs.keys()

        attrnames = []
        for attrname, invocation in usage:
            attrnames.append(attrname)

        types = []

        # Obtain types supporting the first attribute name...

        for name in attr_types.get(attrnames[0]) or []:

            # Record types that support all of the other attributes as well.

            _attrnames = attrs[name]
            if set(attrnames).issubset(_attrnames):
                types.append(name)

        return types

    # Reference identification.

    def identify_references(self):

        "Identify references using usage and name reference information."

        # Names with associated attribute usage.

        for location, usages in self.location_index.items():

            # Obtain attribute usage associated with a name, deducing the nature
            # of the name. Obtain types only for branches involving attribute
            # usage. (In the absence of usage, any type could be involved, but
            # then no accesses exist to require knowledge of the type.)

            have_usage = False
            have_no_usage_branch = False

            for usage in usages:
                if not usage:
                    have_no_usage_branch = True
                    continue
                elif not have_usage:
                    self.init_definition_details(location)
                    have_usage = True
                self.record_types_for_usage(location, usage)

            # Where some usage occurs, but where branches without usage also
            # occur, record the types for those branches anyway.

            if have_usage and have_no_usage_branch:
                self.init_definition_details(location)
                self.record_types_for_usage(location, None)

        # Specific name-based attribute accesses.

        alias_accesses = set()

        for access_location, accessor_locations in self.access_index.items():
            self.record_types_for_access(access_location, accessor_locations, alias_accesses)

        # Anonymous references with attribute chains.

        for location, accesses in self.importer.all_attr_accesses.items():

            # Get distinct attribute names.

            all_attrnames = set()

            for attrnames in accesses:
                all_attrnames.update(get_attrnames(attrnames))

            # Get attribute and accessor details for each attribute name.

            for attrname in all_attrnames:
                access_location = (location, None, attrname, 0)
                self.record_types_for_attribute(access_location, attrname)

        # References via constant/identified objects.

        for location, name_accesses in self.importer.all_const_accesses.items():

            # A mapping from the original name and attributes to resolved access
            # details.

            for original_access, access in name_accesses.items():
                original_name, original_attrnames = original_access
                objpath, ref, attrnames = access

                # Build an accessor combining the name and attribute names used.

                original_accessor = tuple([original_name] + original_attrnames.split("."))

                # Direct accesses to attributes.

                if not attrnames:

                    # Build a descriptive location based on the original
                    # details, exposing the final attribute name.

                    oa, attrname = original_accessor[:-1], original_accessor[-1]
                    oa = ".".join(oa)

                    access_location = (location, oa, attrname, 0)
                    accessor_location = (location, oa, None, 0)
                    self.access_index[access_location] = [accessor_location]

                    self.init_access_details(access_location)
                    self.init_definition_details(accessor_location)

                    # Obtain a reference for the accessor in order to properly
                    # determine its type.

                    if ref.get_kind() != "<instance>":
                        objpath = ref.get_origin()

                    objpath = objpath.rsplit(".", 1)[0]

                    # Where the object name conflicts with the module
                    # providing it, obtain the module details.

                    if objpath in self.importer.modules:
                        accessor = Reference("<module>", objpath)
                    else:
                        accessor = self.importer.get_object(objpath)

                    self.referenced_attrs[access_location] = [(accessor.get_kind(), accessor.get_origin(), ref)]
                    self.access_constrained.add(access_location)

                    class_types, instance_types, module_types = accessor.get_types()
                    self.record_reference_types(accessor_location, class_types, instance_types, module_types, True, True)

                else:

                    # Build a descriptive location based on the original
                    # details, employing the first remaining attribute name.

                    l = get_attrnames(attrnames)
                    attrname = l[0]

                    oa = original_accessor[:-len(l)]
                    oa = ".".join(oa)

                    access_location = (location, oa, attrnames, 0)
                    accessor_location = (location, oa, None, 0)
                    self.access_index[access_location] = [accessor_location]

                    self.init_access_details(access_location)
                    self.init_definition_details(accessor_location)

                    class_types, instance_types, module_types = ref.get_types()

                    self.identify_reference_attributes(access_location, attrname, class_types, instance_types, module_types, True)
                    self.record_reference_types(accessor_location, class_types, instance_types, module_types, True, True)

                original_location = (location, original_name, original_attrnames, 0)

                if original_location != access_location:
                    self.const_accesses[original_location] = access_location
                    self.const_accesses_rev[access_location] = original_location

        # Aliased name definitions. All aliases with usage will have been
        # defined, but they may be refined according to referenced accesses.

        for accessor_location in self.alias_index.keys():
            self.record_types_for_alias(accessor_location)

        # Update accesses employing aliases.

        for access_location in alias_accesses:
            self.record_types_for_access(access_location, self.access_index[access_location])

    def constrain_types(self, path, class_types, instance_types, module_types):

        """
        Using the given 'path' to an object, constrain the given 'class_types',
        'instance_types' and 'module_types'.

        Return the class, instance, module types plus whether the types are
        constrained to a specific kind of type.
        """

        ref = self.importer.identify(path)
        if ref:

            # Constrain usage suggestions using the identified object.

            if ref.has_kind("<class>"):
                return (
                    set(class_types).intersection([ref.get_origin()]), [], [], True
                    )
            elif ref.has_kind("<module>"):
                return (
                    [], [], set(module_types).intersection([ref.get_origin()]), True
                    )

        return class_types, instance_types, module_types, False

    def get_target_types(self, location, usage):

        """
        Return the class, instance and module types constrained for the name at
        the given 'location' exhibiting the given 'usage'. Whether the types
        have been constrained using contextual information is also indicated,
        plus whether the types have been constrained to a specific kind of type.
        """

        unit_path, name, attrnames, version = location

        # Detect any initialised name for the location.

        if name:
            ref = self.get_initialised_name(location)
            if ref:
                (class_types, only_instance_types, module_types,
                    _function_types, _var_types) = separate_types([ref])
                return class_types, only_instance_types, module_types, True, False

        # Retrieve the recorded types for the usage.

        class_types = self.get_class_types_for_usage(usage)
        only_instance_types = set(self.get_instance_types_for_usage(usage)).difference(class_types)
        module_types = self.get_module_types_for_usage(usage)

        # Merge usage deductions with observations to obtain reference types
        # for names involved with attribute accesses.

        if not name:
            return class_types, only_instance_types, module_types, False, False

        # Obtain references to known objects.

        path = get_name_path(unit_path, name)

        class_types, only_instance_types, module_types, constrained_specific = \
            self.constrain_types(path, class_types, only_instance_types, module_types)

        if constrained_specific:
            return class_types, only_instance_types, module_types, constrained_specific, constrained_specific

        # Constrain "self" references.

        if name == "self":
            t = self.constrain_self_reference(unit_path, class_types, only_instance_types)
            if t:
                class_types, only_instance_types, module_types, constrained = t
                return class_types, only_instance_types, module_types, constrained, False

        return class_types, only_instance_types, module_types, False, False

    def constrain_self_reference(self, unit_path, class_types, only_instance_types):

        """
        Where the name "self" appears in a method, attempt to constrain the
        classes involved.

        Return the class, instance, module types plus whether the types are
        constrained.
        """

        class_name = self.in_method(unit_path)

        if not class_name:
            return None

        classes = set([class_name])
        classes.update(self.get_descendants_for_class(class_name))

        # Note that only instances will be expected for these references but
        # either classes or instances may provide the attributes.

        return (
            set(class_types).intersection(classes),
            set(only_instance_types).intersection(classes),
            [], True
            )

    def in_method(self, path):

        "Return whether 'path' refers to a method."

        class_name, method_name = path.rsplit(".", 1)
        return self.importer.classes.has_key(class_name) and class_name

    def init_reference_details(self, location):

        "Initialise reference-related details for 'location'."

        self.init_definition_details(location)
        self.init_access_details(location)

    def init_definition_details(self, location):

        "Initialise name definition details for 'location'."

        self.accessor_class_types[location] = set()
        self.accessor_instance_types[location] = set()
        self.accessor_module_types[location] = set()
        self.provider_class_types[location] = set()
        self.provider_instance_types[location] = set()
        self.provider_module_types[location] = set()

    def init_access_details(self, location):

        "Initialise access details at 'location'."

        self.referenced_attrs[location] = {}

    def record_types_for_access(self, access_location, accessor_locations, alias_accesses=None):

        """
        Define types for the 'access_location' associated with the given
        'accessor_locations'.
        """

        attrname = get_attrname_from_location(access_location)
        if not attrname:
            return

        # Collect all suggested types for the accessors. Accesses may
        # require accessors from of a subset of the complete set of types.

        class_types = set()
        module_types = set()
        instance_types = set()

        constrained = True

        for location in accessor_locations:

            # Remember accesses employing aliases.

            if alias_accesses is not None and self.alias_index.has_key(location):
                alias_accesses.add(access_location)

            # Use the type information deduced for names from above.

            if self.accessor_class_types.has_key(location):
                class_types.update(self.accessor_class_types[location])
                module_types.update(self.accessor_module_types[location])
                instance_types.update(self.accessor_instance_types[location])

            # Where accesses are associated with assignments but where no
            # attribute usage observations have caused such an association,
            # the attribute name is considered by itself.

            else:
                self.init_definition_details(location)
                self.record_types_for_usage(location, [(attrname, False)])

            constrained = location in self.accessor_constrained and constrained

        self.init_access_details(access_location)
        self.identify_reference_attributes(access_location, attrname, class_types, instance_types, module_types, constrained)

    def record_types_for_usage(self, accessor_location, usage):

        """
        Record types for the given 'accessor_location' according to the given
        'usage' observations which may be None to indicate an absence of usage.
        """

        (class_types,
         instance_types,
         module_types,
         constrained,
         constrained_specific) = self.get_target_types(accessor_location, usage)

        invocations = get_invoked_attributes(usage)

        self.record_reference_types(accessor_location, class_types, instance_types, module_types, constrained, constrained_specific, invocations)

    def record_types_for_attribute(self, access_location, attrname):

        """
        Record types for the 'access_location' employing only the given
        'attrname' for type deduction.
        """

        usage = ((attrname, False),)

        class_types = self.get_class_types_for_usage(usage)
        only_instance_types = set(self.get_instance_types_for_usage(usage)).difference(class_types)
        module_types = self.get_module_types_for_usage(usage)

        self.init_reference_details(access_location)

        self.identify_reference_attributes(access_location, attrname, class_types, only_instance_types, module_types, False)
        self.record_reference_types(access_location, class_types, only_instance_types, module_types, False)

    def record_types_for_alias(self, accessor_location):

        """
        Define types for the 'accessor_location' not having associated usage.
        """

        have_access = self.provider_class_types.has_key(accessor_location)

        # With an access, attempt to narrow the existing selection of provider
        # types.

        if have_access:
            provider_class_types = self.provider_class_types[accessor_location]
            provider_instance_types = self.provider_instance_types[accessor_location]
            provider_module_types = self.provider_module_types[accessor_location]

            # Find details for any corresponding access.

            all_class_types = set()
            all_instance_types = set()
            all_module_types = set()

            for access_location in self.alias_index[accessor_location]:
                location, name, attrnames, access_number = access_location

                # Alias references an attribute access.

                if attrnames:

                    # Obtain attribute references for the access.

                    attrs = [attr for _attrtype, object_type, attr in self.referenced_attrs[access_location]]

                    # Separate the different attribute types.

                    (class_types, instance_types, module_types,
                        function_types, var_types) = separate_types(attrs)

                    # Where non-accessor types are found, do not attempt to refine
                    # the defined accessor types.

                    if function_types or var_types:
                        return

                    class_types = set(provider_class_types).intersection(class_types)
                    instance_types = set(provider_instance_types).intersection(instance_types)
                    module_types = set(provider_module_types).intersection(module_types)

                # Alias references a name, not an access.

                else:
                    # Attempt to refine the types using initialised names.

                    attr = self.get_initialised_name(access_location)
                    if attr:
                        (class_types, instance_types, module_types,
                            _function_types, _var_types) = separate_types([attr])

                    # Where no further information is found, do not attempt to
                    # refine the defined accessor types.

                    else:
                        return

                all_class_types.update(class_types)
                all_instance_types.update(instance_types)
                all_module_types.update(module_types)

            # Record refined type details for the alias as an accessor.

            self.init_definition_details(accessor_location)
            self.record_reference_types(accessor_location, all_class_types, all_instance_types, all_module_types, False)

        # Without an access, attempt to identify references for the alias.

        else:
            refs = set()

            for access_location in self.alias_index[accessor_location]:

                # Obtain any redefined constant access location.

                if self.const_accesses.has_key(access_location):
                    access_location = self.const_accesses[access_location]

                location, name, attrnames, access_number = access_location

                # Alias references an attribute access.

                if attrnames:
                    attrs = [attr for attrtype, object_type, attr in self.referenced_attrs[access_location]]
                    refs.update(attrs)

                # Alias references a name, not an access.

                else:
                    attr = self.get_initialised_name(access_location)
                    attrs = attr and [attr] or []
                    if not attrs and self.provider_class_types.has_key(access_location):
                        class_types = self.provider_class_types[access_location]
                        instance_types = self.provider_instance_types[access_location]
                        module_types = self.provider_module_types[access_location]
                        attrs = combine_types(class_types, instance_types, module_types)
                    if attrs:
                        refs.update(attrs)

            # Record reference details for the alias separately from accessors.

            self.referenced_objects[accessor_location] = refs

    def get_initialised_name(self, access_location):

        """
        Return references for any initialised names at 'access_location', or
        None if no such references exist.
        """

        location, name, attrnames, version = access_location
        path = get_name_path(location, name)

        # Use initialiser information, if available.

        refs = self.importer.all_initialised_names.get(path)
        if refs and refs.has_key(version):
            return refs[version]
        else:
            return None

    def record_reference_types(self, location, class_types, instance_types,
        module_types, constrained, constrained_specific=False, invocations=None):

        """
        Associate attribute provider types with the given 'location', consisting
        of the given 'class_types', 'instance_types' and 'module_types'.

        If 'constrained' is indicated, the constrained nature of the accessor is
        recorded for the location.

        If 'constrained_specific' is indicated using a true value, instance types
        will not be added to class types to permit access via instances at the
        given location. This is only useful where a specific accessor is known
        to be a class.

        Note that the specified types only indicate the provider types for
        attributes, whereas the recorded accessor types indicate the possible
        types of the actual objects used to access attributes.
        """

        # Update the type details for the location.

        self.provider_class_types[location].update(class_types)
        self.provider_instance_types[location].update(instance_types)
        self.provider_module_types[location].update(module_types)

        # Class types support classes and instances as accessors.
        # Instance-only and module types support only their own kinds as
        # accessors.

        path, name, version, attrnames = location

        if invocations:
            class_only_types = self.filter_for_invocations(class_types, invocations)
        else:
            class_only_types = class_types

        # However, the nature of accessors can be further determined.
        # Any self variable may only refer to an instance.

        if name != "self" or not self.in_method(path):
            self.accessor_class_types[location].update(class_only_types)

        if not constrained_specific:
            self.accessor_instance_types[location].update(class_types)

        self.accessor_instance_types[location].update(instance_types)

        if name != "self" or not self.in_method(path):
            self.accessor_module_types[location].update(module_types)

        if constrained:
            self.accessor_constrained.add(location)

    def filter_for_invocations(self, class_types, attrnames):

        """
        From the given 'class_types', identify methods for the given
        'attrnames' that are being invoked, returning a filtered collection of
        class types.
        """

        to_filter = set()

        for class_type in class_types:
            for attrname in attrnames:
                ref = self.importer.get_class_attribute(class_type, attrname)
                parent_class = ref and ref.parent()

                if ref and ref.has_kind("<function>") and (
                   parent_class == class_type or
                   class_type in self.descendants[parent_class]):

                    to_filter.add(class_type)
                    break

        return set(class_types).difference(to_filter)

    def identify_reference_attributes(self, location, attrname, class_types, instance_types, module_types, constrained):

        """
        Identify reference attributes, associating them with the given
        'location', identifying the given 'attrname', employing the given
        'class_types', 'instance_types' and 'module_types'.

        If 'constrained' is indicated, the constrained nature of the access is
        recorded for the location.
        """

        # Record the referenced objects.

        self.referenced_attrs[location] = \
            self._identify_reference_attribute(attrname, class_types, instance_types, module_types)

        if constrained:
            self.access_constrained.add(location)

    def _identify_reference_attribute(self, attrname, class_types, instance_types, module_types):

        """
        Identify the reference attribute with the given 'attrname', employing
        the given 'class_types', 'instance_types' and 'module_types'.
        """

        attrs = set()

        # The class types expose class attributes either directly or via
        # instances.

        for object_type in class_types:
            ref = self.importer.get_class_attribute(object_type, attrname)
            if ref:
                attrs.add(("<class>", object_type, ref))

            # Add any distinct instance attributes that would be provided
            # by instances also providing indirect class attribute access.

            for ref in self.importer.get_instance_attributes(object_type, attrname):
                attrs.add(("<instance>", object_type, ref))

        # The instance-only types expose instance attributes, but although
        # classes are excluded as potential accessors (since they do not provide
        # the instance attributes), the class types may still provide some
        # attributes.

        for object_type in instance_types:
            instance_attrs = self.importer.get_instance_attributes(object_type, attrname)

            if instance_attrs:
                for ref in instance_attrs:
                    attrs.add(("<instance>", object_type, ref))
            else:
                ref = self.importer.get_class_attribute(object_type, attrname)
                if ref:
                    attrs.add(("<class>", object_type, ref))

        # Module types expose module attributes for module accessors.

        for object_type in module_types:
            ref = self.importer.get_module_attribute(object_type, attrname)
            if ref:
                attrs.add(("<module>", object_type, ref))

        return attrs

    constrained_specific_tests = (
        "constrained-specific-instance",
        "constrained-specific-type",
        "constrained-specific-object",
        )

    constrained_common_tests = (
        "constrained-common-instance",
        "constrained-common-type",
        "constrained-common-object",
        )

    guarded_specific_tests = (
        "guarded-specific-instance",
        "guarded-specific-type",
        "guarded-specific-object",
        )

    guarded_common_tests = (
        "guarded-common-instance",
        "guarded-common-type",
        "guarded-common-object",
        )

    specific_tests = (
        "specific-instance",
        "specific-type",
        "specific-object",
        )

    common_tests = (
        "common-instance",
        "common-type",
        "common-object",
        )

    class_tests = (
        "guarded-specific-type",
        "guarded-common-type",
        "specific-type",
        "common-type",
        )

    class_or_instance_tests = (
        "guarded-specific-object",
        "guarded-common-object",
        "specific-object",
        "common-object",
        )

    def get_access_plan(self, location):

        """
        Return details of the access at the given 'location'. The details are as
        follows:

         * the initial accessor (from which accesses will be performed if no
           computed static accessor is found)
         * details of any test required on the initial accessor
         * details of any type employed by the test
         * any static accessor (from which accesses will be performed in
           preference to the initial accessor)
         * attributes needing to be traversed from the base that yield
           unambiguous objects
         * access modes for each of the unambiguously-traversed attributes
         * remaining attributes needing to be tested and traversed
         * details of the context
         * the method of obtaining the final attribute
         * any static final attribute
        """

        const_access = self.const_accesses_rev.has_key(location)

        path, name, attrnames, version = location
        remaining = attrnames.split(".")
        attrname = remaining[0]

        # Obtain reference and accessor information, retaining also distinct
        # provider kind details.

        attrs = []
        objtypes = []
        provider_kinds = set()

        for attrtype, objtype, attr in self.referenced_attrs[location]:
            attrs.append(attr)
            objtypes.append(objtype)
            provider_kinds.add(attrtype)

        # Obtain accessor type and kind information.

        accessor_types = self.reference_all_accessor_types[location]
        accessor_general_types = self.reference_all_accessor_general_types[location]
        accessor_kinds = get_kinds(accessor_general_types)

        # Determine any guard or test requirements.

        constrained = location in self.access_constrained
        test = self.reference_test_types[location]
        test_type = self.reference_test_accessor_type.get(location)

        # Determine the accessor and provider properties.

        class_accessor = "<class>" in accessor_kinds
        module_accessor = "<module>" in accessor_kinds
        instance_accessor = "<instance>" in accessor_kinds
        provided_by_class = "<class>" in provider_kinds
        provided_by_instance = "<instance>" in provider_kinds

        # Determine how attributes may be accessed relative to the accessor.

        object_relative = class_accessor or module_accessor or provided_by_instance
        class_relative = instance_accessor and provided_by_class

        # Identify the last static attribute for context acquisition.

        base = None
        dynamic_base = None

        # Constant accesses have static accessors.

        if const_access:
            base = len(objtypes) == 1 and first(objtypes)

        # Constant accessors are static.

        else:
            ref = self.importer.identify("%s.%s" % (path, name))
            if ref:
                base = ref.get_origin()

            # Usage of previously-generated guard and test details.

            elif test in self.constrained_specific_tests:
                ref = first(accessor_types)

            elif test in self.constrained_common_tests:
                ref = first(accessor_general_types)

            elif test in self.guarded_specific_tests:
                ref = first(accessor_types)

            elif test in self.guarded_common_tests:
                ref = first(accessor_general_types)

            # For attribute-based tests, tentatively identify a dynamic base.
            # Such tests allow single or multiple kinds of a type.

            elif test in self.common_tests or test in self.specific_tests:
                dynamic_base = test_type

            # Static accessors.

            if not base and test in self.class_tests:
                base = ref and ref.get_origin() or dynamic_base

            # Accessors that are not static but whose nature is determined.

            elif not base and ref:
                dynamic_base = ref.get_origin()

        traversed = []
        traversal_modes = []
        provider_kind = first(provider_kinds)

        # Traverse remaining attributes.

        while len(attrs) == 1:
            attr = first(attrs)
            accessor_kind = attr.get_kind()

            traversed.append(attrname)
            traversal_modes.append(accessor_kind == provider_kind and "object" or "class")

            del remaining[0]

            if not remaining:
                break

            # Update the last static attribute.

            if attr.static():
                base = attr.get_origin()
                traversed = []
                traversal_modes = []

            # Get the next attribute.

            attrname = remaining[0]
            attrs = self.importer.get_attributes(attr, attrname)
            provider_kind = self.importer.get_attribute_provider(attr, attrname)

        # Where many attributes are suggested, no single attribute identity can
        # be loaded.

        else:
            attr = None

        # Determine the method of access.

        is_assignment = location in self.reference_assignments

        # Identified attribute that must be accessed via its parent.

        if attr and attr.get_name() and is_assignment:
            final_method = "static-assign"; origin = attr.get_name()

        # Static, identified attribute.

        elif attr and attr.static():
            final_method = is_assignment and "static-assign" or "static"
            origin = attr.final()

        # All other methods of access involve traversal.

        else:
            final_method = is_assignment and "assign" or "access"
            origin = None

        # First attribute accessed at a known position via the accessor.

        if base or dynamic_base:
            first_method = "relative" + (object_relative and "-object" or "") + \
                                        (class_relative and "-class" or "")

        # The fallback case is always run-time testing and access.

        else:
            first_method = "check" + (object_relative and "-object" or "") + \
                                     (class_relative and "-class" or "")

        # Determine the nature of the context.

        context = is_assignment and "unset" or \
                  len(traversed + remaining) == 1 and \
                      (base and "base" or "original-accessor") or \
                  "final-accessor"

        return name, test, test_type, base, traversed, traversal_modes, remaining, context, first_method, final_method, origin

# vim: tabstop=4 expandtab shiftwidth=4
