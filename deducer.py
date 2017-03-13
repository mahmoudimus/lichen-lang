#!/usr/bin/env python

"""
Deduce types for usage observations.

Copyright (C) 2014, 2015, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

from common import first, get_assigned_attributes, \
                   get_attrname_from_location, get_attrnames, \
                   get_invoked_attributes, get_name_path, init_item, \
                   sorted_output, CommonOutput
from encoders import encode_access_location, encode_constrained, \
                     encode_instruction, encode_location, encode_usage, \
                     get_kinds, test_label_for_kind, test_label_for_type
from errors import DeduceError
from os.path import join
from referencing import combine_types, is_single_class_type, separate_types, \
                        Reference

class Deducer(CommonOutput):

    "Deduce types in a program."

    root_class_type = "__builtins__.object"

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

        # All known attribute names.

        self.all_attrnames = set()

        # Modified attributes from usage observations.

        self.modified_attributes = {}

        # Accesses that are assignments or invocations.

        self.reference_assignments = set()
        self.reference_invocations = {}
        self.reference_invocations_unsuitable = {}

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

        # Specific attribute access information.

        self.access_instructions = {}
        self.accessor_kinds = {}

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
        self.reference_all_providers = {}
        self.reference_all_provider_kinds = {}
        self.reference_all_accessor_types = {}
        self.reference_all_accessor_general_types = {}
        self.reference_test_types = {}
        self.reference_test_accessor_type = {}

        # The processing workflow itself.

        self.init_usage_index()
        self.init_attr_type_indexes()
        self.init_combined_attribute_index()
        self.init_accessors()
        self.init_accesses()
        self.init_aliases()
        self.modify_mutated_attributes()
        self.identify_references()
        self.classify_accessors()
        self.classify_accesses()
        self.initialise_access_plans()
        self.initialise_access_instructions()
        self.identify_dependencies()

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
                if guard_test:
                    guard_test_type, guard_test_arg = guard_test

                # Write specific type guard details.

                if guard_test and guard_test_type == "specific":
                    print >>f_guards, encode_location(location), "-".join(guard_test), \
                        first(get_kinds(all_types)), \
                        sorted_output(all_types)

                # Write common type guard details.

                elif guard_test and guard_test_type == "common":
                    print >>f_guards, encode_location(location), "-".join(guard_test), \
                        first(get_kinds(all_general_types)), \
                        sorted_output(all_general_types)

                print >>f_type_summary, encode_location(location), encode_constrained(constrained), \
                    guard_test and "-".join(guard_test) or "unguarded", sorted_output(all_general_types), len(all_types)

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
        f_unsuitable = open(join(self.output, "invocation_warnings"), "w")

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

                    if test_type[0] == "validate":
                        print >>f_tests, encode_access_location(location), "-".join(test_type)

                    # Write any type checks for anonymous accesses.

                    elif test_type and self.reference_test_accessor_type.get(location):
                        print >>f_tests, encode_access_location(location), "-".join(test_type), \
                            sorted_output(all_accessed_attrs), \
                            self.reference_test_accessor_type[location]

                    print >>f_attr_summary, encode_access_location(location), encode_constrained(constrained), \
                        test_type and "-".join(test_type) or "untested", sorted_output(all_accessed_attrs)

                    # Write details of potentially unsuitable invocation
                    # occurrences.

                    unsuitable = self.reference_invocations_unsuitable.get(location)
                    if unsuitable:
                        unsuitable = map(str, unsuitable)
                        unsuitable.sort()
                        print >>f_unsuitable, encode_access_location(location), ", ".join(unsuitable)

                else:
                    print >>f_warnings, encode_access_location(location)

        finally:
            f_attr_summary.close()
            f_attrs.close()
            f_tests.close()
            f_warnings.close()
            f_unsuitable.close()

    def write_access_plans(self):

        """
        Write access and instruction plans.

        Each attribute access is written out as a plan of the following form:

        location " " name " " test " " test type " " base " " traversed attributes
                 " " traversal access modes " " attributes to traverse
                 " " context " " context test " " first access method
                 " " final access method " " static attribute " " accessor kinds

        Locations have the following format:

        qualified name of scope "." local name ":" name version

        Traversal access modes are either "class" (obtain accessor class to
        access attribute) or "object" (obtain attribute directly from accessor).
        """

        f_attrs = open(join(self.output, "attribute_plans"), "w")

        try:
            locations = self.access_plans.keys()
            locations.sort()

            for location in locations:
                name, test, test_type, base, \
                    traversed, traversal_modes, attrnames, \
                    context, context_test, \
                    first_method, final_method, \
                    attr, accessor_kinds = self.access_plans[location]

                print >>f_attrs, encode_access_location(location), \
                                 name or "{}", \
                                 test and "-".join(test) or "{}", \
                                 test_type or "{}", \
                                 base or "{}", \
                                 ".".join(traversed) or "{}", \
                                 ".".join(traversal_modes) or "{}", \
                                 ".".join(attrnames) or "{}", \
                                 context, context_test, \
                                 first_method, final_method, attr or "{}", \
                                 ",".join(accessor_kinds)

        finally:
            f_attrs.close()

        f = open(join(self.output, "instruction_plans"), "w")
        try:
            access_instructions = self.access_instructions.items()
            access_instructions.sort()

            for location, instructions in access_instructions:
                print >>f, encode_access_location(location), "..."
                for instruction in instructions:
                    print >>f, encode_instruction(instruction)
                print >>f

        finally:
            f.close()

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
                    self.accessor_guard_tests[location] = ("specific", test_label_for_type(first(all_types)))
                elif is_single_class_type(all_types):
                    self.accessor_guard_tests[location] = ("specific", "object")

                # Record common type guard details.

                elif len(all_general_types) == 1:
                    self.accessor_guard_tests[location] = ("common", test_label_for_type(first(all_types)))
                elif is_single_class_type(all_general_types):
                    self.accessor_guard_tests[location] = ("common", "object")

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
                raise DeduceError("In %s, access via %s to attribute %s (occurrence %d) cannot be identified." % location)

            # Record attribute information for each name used on the
            # accessor.

            attrname = get_attrname_from_location(location)

            self.reference_all_attrs[location] = all_accessed_attrs = []
            self.reference_all_providers[location] = all_providers = []
            self.reference_all_provider_kinds[location] = all_provider_kinds = set()

            # Obtain provider and attribute details for this kind of
            # object.

            for attrtype, object_type, attr in referenced_attrs:
                all_accessed_attrs.append(attr)
                all_providers.append(object_type)
                all_provider_kinds.add(attrtype)

            # Obtain reference and provider information as sets for the
            # operations below, retaining the list forms for use with
            # instruction plan preparation.

            all_accessed_attrs = set(all_accessed_attrs)
            all_providers = set(all_providers)
            all_general_providers = self.get_most_general_types(all_providers)

            # Determine which attributes would be provided by the
            # accessor types upheld by a guard.

            if guarded:
                guard_attrs = set()

                for _attrtype, object_type, attr in \
                    self._identify_reference_attribute(location, attrname, guard_class_types, guard_instance_types, guard_module_types):

                    guard_attrs.add(attr)
            else:
                guard_attrs = None

            # Constrained accesses guarantee the nature of the accessor.
            # However, there may still be many types involved.

            if constrained:
                if single_accessor_type:
                    self.reference_test_types[location] = ("constrained", "specific", test_label_for_type(first(all_accessor_types)))
                elif single_accessor_class_type:
                    self.reference_test_types[location] = ("constrained", "specific", "object")
                elif single_accessor_general_type:
                    self.reference_test_types[location] = ("constrained", "common", test_label_for_type(first(all_accessor_general_types)))
                elif single_accessor_general_class_type:
                    self.reference_test_types[location] = ("constrained", "common", "object")
                else:
                    self.reference_test_types[location] = ("constrained", "many")

            # Suitably guarded accesses, where the nature of the
            # accessor can be guaranteed, do not require the attribute
            # involved to be validated. Otherwise, for unguarded
            # accesses, access-level tests are required.

            elif guarded and all_accessed_attrs.issubset(guard_attrs):
                if single_accessor_type:
                    self.reference_test_types[location] = ("guarded", "specific", test_label_for_type(first(all_accessor_types)))
                elif single_accessor_class_type:
                    self.reference_test_types[location] = ("guarded", "specific", "object")
                elif single_accessor_general_type:
                    self.reference_test_types[location] = ("guarded", "common", test_label_for_type(first(all_accessor_general_types)))
                elif single_accessor_general_class_type:
                    self.reference_test_types[location] = ("guarded", "common", "object")

            # Record the need to test the type of anonymous and
            # unconstrained accessors.

            elif len(all_providers) == 1:
                provider = first(all_providers)
                if provider != self.root_class_type:
                    all_accessor_kinds = set(get_kinds(all_accessor_types))
                    if len(all_accessor_kinds) == 1:
                        test_type = ("test", "specific", test_label_for_kind(first(all_accessor_kinds)))
                    else:
                        test_type = ("test", "specific", "object")
                    self.reference_test_types[location] = test_type
                    self.reference_test_accessor_type[location] = provider

            elif len(all_general_providers) == 1:
                provider = first(all_general_providers)
                if provider != self.root_class_type:
                    all_accessor_kinds = set(get_kinds(all_accessor_general_types))
                    if len(all_accessor_kinds) == 1:
                        test_type = ("test", "common", test_label_for_kind(first(all_accessor_kinds)))
                    else:
                        test_type = ("test", "common", "object")
                    self.reference_test_types[location] = test_type
                    self.reference_test_accessor_type[location] = provider

            # Record the need to test the identity of the attribute.

            else:
                self.reference_test_types[location] = ("validate",)

    def initialise_access_plans(self):

        "Define attribute access plans."

        for location in self.referenced_attrs.keys():
            original_location = self.const_accesses_rev.get(location)
            self.access_plans[original_location or location] = self.get_access_plan(location)

    def identify_dependencies(self):

        "Introduce more module dependencies to the importer."

        for location, referenced_attrs in self.referenced_attrs.items():
            path, name, attrnames, version = location

            # Identify module-level paths.

            if self.importer.modules.has_key(path):
                module_name = path

            # Identify the module containing other paths.

            else:
                ref = self.importer.identify(path)
                for objpath in ref.ancestors():
                    if self.importer.modules.has_key(objpath):
                        module_name = objpath
                        break
                else:
                    raise DeduceError("Cannot find module for path %s." % path)

            # Identify references providing dependencies.

            for attrtype, objtype, attr in referenced_attrs:
                self.importer.add_dependency(path, attr.get_origin())

    def get_referenced_attrs(self, location):

        """
        Return attributes referenced at the given access 'location' by the given
        'attrname' as a list of (attribute type, attribute set) tuples.
        """

        d = {}
        for attrtype, objtype, attr in self.referenced_attrs[location]:
            init_item(d, attrtype, set)
            d[attrtype].add(attr.unaliased())
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
                self.add_usage_term(access_location, ((attrname, False, False),))

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
        Check that attributes used in accesses are actually defined on some
        object. This can be overlooked if unknown attributes are employed in
        attribute chains.

        Initialise collections for accesses involving assignments.
        """

        # For each scope, obtain access details.

        for path, all_accesses in self.importer.all_attr_access_modifiers.items():

            # For each combination of name and attribute names, obtain
            # applicable modifiers.

            for (name, attrname_str), modifiers in all_accesses.items():

                # For each access, determine the name versions affected by
                # assignments.

                for access_number, (assignment, invocation) in enumerate(modifiers):

                    if name:
                        access_location = (path, name, attrname_str, access_number)
                    else:
                        access_location = (path, None, attrname_str, 0)

                    # Plain name accesses do not employ attributes and are
                    # ignored. Whether they are invoked is of interest, however.

                    if not attrname_str:
                        if invocation:
                            self.reference_invocations[access_location] = invocation
                        continue

                    attrnames = get_attrnames(attrname_str)

                    # Check the attribute names.

                    for attrname in attrnames:
                        if not attrname in self.all_attrnames:
                            raise DeduceError("In %s, attribute %s is not defined in the program." % (path, attrname))

                    # Now only process assignments and invocations.

                    if invocation:
                        self.reference_invocations[access_location] = invocation
                        continue
                    elif not assignment:
                        continue

                    # Associate assignments with usage.

                    self.reference_assignments.add(access_location)

                    # Assignment occurs for the only attribute.

                    if len(attrnames) == 1:
                        accessor_locations = self.get_accessors_for_access(access_location)

                        for location in accessor_locations:
                            for usage in self.location_index[location]:
                                init_item(self.assigned_attrs, usage, set)
                                self.assigned_attrs[usage].add((path, name, attrnames[0]))

                    # Assignment occurs for the final attribute.

                    else:
                        usage = ((attrnames[-1], False, False),)
                        init_item(self.assigned_attrs, usage, set)
                        self.assigned_attrs[usage].add((path, name, attrnames[-1]))

    def init_aliases(self):

        "Expand aliases so that alias-based accesses can be resolved."

        # Get aliased names with details of their accesses.

        for (path, name), all_aliases in self.importer.all_aliased_names.items():

            # For each version of the name, obtain the access location.

            for version, (original_path, original_name, attrnames, access_number) in all_aliases.items():
                accessor_location = (path, name, None, version)
                access_location = (original_path, original_name, attrnames, access_number)
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

            for path, name, attrname in all_attrnames:
                class_types = self.get_class_types_for_usage(usage)
                only_instance_types = set(self.get_instance_types_for_usage(usage)).difference(class_types)
                module_types = self.get_module_types_for_usage(usage)

                # Detect self usage within methods in order to narrow the scope
                # of the mutation.

                t = name == "self" and self.constrain_self_reference(path, class_types, only_instance_types)
                if t:
                    class_types, only_instance_types, module_types, constrained = t
                objects = set(class_types).union(only_instance_types).union(module_types)

                self.mutate_attribute(objects, attrname)

    def mutate_attribute(self, objects, attrname):

        "Mutate static 'objects' with the given 'attrname'."

        for name in objects:
            attr = "%s.%s" % (name, attrname)
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
            return [self.root_class_type]
        else:
            return module_types

    # More efficient usage-to-type indexing and retrieval.

    def init_attr_type_indexes(self):

        "Identify the types that can support each attribute name."

        self._init_attr_type_index(self.attr_class_types, self.importer.all_class_attrs)
        self._init_attr_type_index(self.attr_instance_types, self.importer.all_instance_attrs, True)
        self._init_attr_type_index(self.attr_instance_types, self.importer.all_combined_attrs, False)
        self._init_attr_type_index(self.attr_module_types, self.importer.all_module_attrs)

    def _init_attr_type_index(self, attr_types, attrs, assignment=None):

        """
        Initialise the 'attr_types' attribute-to-types mapping using the given
        'attrs' type-to-attributes mapping.
        """

        for name, attrnames in attrs.items():
            for attrname in attrnames:

                # Permit general access for certain kinds of object.

                if assignment is None:
                    init_item(attr_types, (attrname, False), set)
                    init_item(attr_types, (attrname, True), set)
                    attr_types[(attrname, False)].add(name)
                    attr_types[(attrname, True)].add(name)

                # Restrict attribute assignment for instances.

                else:
                    init_item(attr_types, (attrname, assignment), set)
                    attr_types[(attrname, assignment)].add(name)

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

        keys = []
        for attrname, invocation, assignment in usage:
            keys.append((attrname, assignment))

        # Obtain types supporting the first (attribute name, assignment) key...

        types = set(attr_types.get(keys[0]) or [])

        for key in keys[1:]:
            
            # Record types that support all of the other attributes as well.

            types.intersection_update(attr_types.get(key) or [])

        return types

    def init_combined_attribute_index(self):

        "Initialise a combined index for the detection of invalid attributes."

        self.all_attrnames = set()
        for attrs in (self.importer.all_combined_attrs, self.importer.all_module_attrs):
            for name, attrnames in attrs.items():
                self.all_attrnames.update(attrnames)

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

                # Define mappings between the original and access locations
                # so that translation can work from the source details.

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
        have_assignments = get_assigned_attributes(usage)

        # Detect any initialised name for the location.

        if name:
            ref = self.get_initialised_name(location)
            if ref:
                (class_types, only_instance_types, module_types,
                    _function_types, _var_types) = separate_types([ref])
                return class_types, only_instance_types, module_types, True, have_assignments

        # Retrieve the recorded types for the usage.

        class_types = self.get_class_types_for_usage(usage)
        only_instance_types = set(self.get_instance_types_for_usage(usage)).difference(class_types)
        module_types = self.get_module_types_for_usage(usage)

        # Merge usage deductions with observations to obtain reference types
        # for names involved with attribute accesses.

        if not name:
            return class_types, only_instance_types, module_types, False, have_assignments

        # Obtain references to known objects.

        path = get_name_path(unit_path, name)

        class_types, only_instance_types, module_types, constrained_specific = \
            self.constrain_types(path, class_types, only_instance_types, module_types)

        if constrained_specific:
            return class_types, only_instance_types, module_types, constrained_specific, \
                constrained_specific or have_assignments

        # Constrain "self" references.

        if name == "self":

            # Test for the class of the method in the deduced types.

            class_name = self.in_method(unit_path)

            if class_name and class_name not in class_types and class_name not in only_instance_types:
                raise DeduceError("In %s, usage {%s} is not directly supported by class %s or its instances." %
                                  (unit_path, encode_usage(usage), class_name))

            # Constrain the types to the class's hierarchy.

            t = self.constrain_self_reference(unit_path, class_types, only_instance_types)
            if t:
                class_types, only_instance_types, module_types, constrained = t
                return class_types, only_instance_types, module_types, constrained, have_assignments

        return class_types, only_instance_types, module_types, False, have_assignments

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
        return class_name != "__builtins__.core.type" and self.importer.classes.has_key(class_name) and class_name

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

        invocation = access_location in self.reference_invocations
        assignment = access_location in self.reference_assignments

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
                self.record_types_for_usage(location, [(attrname, invocation, assignment)])

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

        self.record_reference_types(accessor_location, class_types, instance_types,
            module_types, constrained, constrained_specific, invocations)

    def record_types_for_attribute(self, access_location, attrname):

        """
        Record types for the 'access_location' employing only the given
        'attrname' for type deduction.
        """

        (class_types,
         only_instance_types,
         module_types) = self.get_types_for_attribute(attrname)

        self.init_reference_details(access_location)

        self.identify_reference_attributes(access_location, attrname, class_types, only_instance_types, module_types, False)
        self.record_reference_types(access_location, class_types, only_instance_types, module_types, False)

    def get_types_for_attribute(self, attrname):

        "Return class, instance-only and module types supporting 'attrname'."

        usage = ((attrname, False, False),)

        class_types = self.get_class_types_for_usage(usage)
        only_instance_types = set(self.get_instance_types_for_usage(usage)).difference(class_types)
        module_types = self.get_module_types_for_usage(usage)

        return class_types, only_instance_types, module_types

    def record_types_for_alias(self, accessor_location):

        """
        Define types for the 'accessor_location' not having associated usage.
        """

        have_access = self.provider_class_types.has_key(accessor_location)

        # With an access, attempt to narrow the existing selection of provider
        # types. Invocations attempt to find return value information, with
        # instance return values also yielding class providers (since attributes
        # on instances could be provided by classes).

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
                invocation = self.reference_invocations.get(access_location)

                attrnames = attrnames and attrnames.split(".")
                remaining = attrnames and len(attrnames) > 1

                # Alias has remaining attributes: reference details do not
                # correspond to the accessor; the remaining attributes would
                # need to be traversed first.

                if remaining:
                    return

                # Alias references an attribute access.

                if attrnames:

                    # Obtain references and attribute types for the access.

                    attrs = self.get_references_for_access(access_location)
                    attrs = self.convert_invocation_providers(attrs, invocation)

                    (class_types, instance_types, module_types, function_types,
                        var_types) = separate_types(attrs)

                    # Where non-accessor types are found, do not attempt to refine
                    # the defined accessor types.

                    if function_types or var_types:
                        return

                    # Invocations converting class accessors to instances do not
                    # change the nature of class providers.

                    class_types = set(provider_class_types).intersection(class_types)
                    instance_types = set(provider_instance_types).intersection(instance_types)
                    module_types = set(provider_module_types).intersection(module_types)

                # Alias references a name, not an access.

                else:
                    # Attempt to refine the types using initialised names.

                    attr = self.get_initialised_name(access_location)
                    if attr:
                        attrs = self.convert_invocation_providers([attr], invocation)

                        (class_types, instance_types, module_types, function_types,
                            var_types) = separate_types(attrs)

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
        # Invocations convert classes to instances and also attempt to find
        # return value information.

        else:
            refs = set()

            for access_location in self.alias_index[accessor_location]:

                # Obtain any redefined constant access location.

                if self.const_accesses.has_key(access_location):
                    access_location = self.const_accesses[access_location]

                location, name, attrnames, access_number = access_location
                invocation = self.reference_invocations.get(access_location)

                attrnames = attrnames and attrnames.split(".")
                remaining = attrnames and len(attrnames) > 1

                # Alias has remaining attributes: reference details do not
                # correspond to the accessor; the remaining attributes would
                # need to be traversed first.

                if remaining:
                    return

                # Alias references an attribute access.

                attrname = attrnames and attrnames[0]

                if attrname:

                    # Obtain references and attribute types for the access.

                    attrs = self.get_references_for_access(access_location)
                    attrs = self.convert_invocations(attrs, invocation)
                    refs.update(attrs)

                # Alias references a name, not an access.

                else:

                    # Obtain initialiser information.

                    attr = self.get_initialised_name(access_location)
                    if attr:
                        refs.update(self.convert_invocations([attr], invocation))

                    # Obtain provider information.

                    elif self.provider_class_types.has_key(access_location):
                        class_types = self.provider_class_types[access_location]
                        instance_types = self.provider_instance_types[access_location]
                        module_types = self.provider_module_types[access_location]

                        refs.update(combine_types(class_types, instance_types, module_types))

            # Record reference details for the alias separately from accessors.

            self.referenced_objects[accessor_location] = refs

    def get_references_for_access(self, access_location):

        "Return the references identified for 'access_location'."

        attrs = []
        for attrtype, object_type, attr in self.referenced_attrs[access_location]:
            attrs.append(attr)
        return attrs

    def convert_invocation_providers(self, refs, invocation):

        """
        Convert 'refs' to providers corresponding to the results of invoking
        each of the given references, if 'invocation' is set to a true value.
        """

        if not invocation:
            return refs

        providers = set()

        for ref in refs:
            ref = self.convert_invocation_provider(ref)
            if ref.has_kind("<instance>"):
                providers.add(Reference("<class>", ref.get_origin()))
            providers.add(ref)

        return providers

    def convert_invocation_provider(self, ref):

        "Convert 'ref' to a provider appropriate to its invocation result."

        if ref and ref.has_kind("<class>"):
            return ref

        return Reference("<var>")

    def convert_invocations(self, refs, invocation):

        """
        Convert 'refs' to invocation results if 'invocation' is set to a true
        value.
        """

        return invocation and map(self.convert_invocation, refs) or refs

    def convert_invocation(self, ref):

        "Convert 'ref' to its invocation result."

        if ref and ref.has_kind("<class>"):
            return ref.instance_of()

        return Reference("<var>")

    def get_initialised_name(self, access_location):

        """
        Return references for any initialised names at 'access_location', or
        None if no such references exist.
        """

        path, name, attrnames, version = access_location

        # Use initialiser information, if available.

        refs = self.importer.all_initialised_names.get((path, name))
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

        If 'invocations' is given, the given attribute names indicate those
        which are involved in invocations. Such invocations, if involving
        functions, will employ those functions as bound methods and will
        therefore not support classes as accessors, only instances of such
        classes.

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

        This method may be used to remove class types from consideration where
        their attributes are methods that are directly invoked: method
        invocations must involve instance accessors.
        """

        to_filter = set()

        for class_type in class_types:
            for attrname in attrnames:

                # Attempt to obtain a class attribute of the given name. This
                # may return an attribute provided by an ancestor class.

                ref = self.importer.get_class_attribute(class_type, attrname)
                parent_class = ref and ref.parent()

                # If such an attribute is a method and would be available on
                # the given class, record the class for filtering.

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
            self._identify_reference_attribute(location, attrname, class_types, instance_types, module_types)

        if constrained:
            self.access_constrained.add(location)

    def _identify_reference_attribute(self, location, attrname, class_types, instance_types, module_types):

        """
        Identify the reference attribute at the given access 'location', using
        the given 'attrname', and employing the given 'class_types',
        'instance_types' and 'module_types'.
        """

        attrs = set()

        # The class types expose class attributes either directly or via
        # instances.

        for object_type in class_types:
            ref = self.importer.get_class_attribute(object_type, attrname)
            if ref and self.is_compatible_callable(location, object_type, ref):
                attrs.add(("<class>", object_type, ref))

            # Add any distinct instance attributes that would be provided
            # by instances also providing indirect class attribute access.

            for ref in self.importer.get_instance_attributes(object_type, attrname):
                if self.is_compatible_callable(location, object_type, ref):
                    attrs.add(("<instance>", object_type, ref))

        # The instance-only types expose instance attributes, but although
        # classes are excluded as potential accessors (since they do not provide
        # the instance attributes), the class types may still provide some
        # attributes.

        for object_type in instance_types:
            instance_attrs = self.importer.get_instance_attributes(object_type, attrname)

            if instance_attrs:
                for ref in instance_attrs:
                    if self.is_compatible_callable(location, object_type, ref):
                        attrs.add(("<instance>", object_type, ref))
            else:
                ref = self.importer.get_class_attribute(object_type, attrname)
                if ref and self.is_compatible_callable(location, object_type, ref):
                    attrs.add(("<class>", object_type, ref))

        # Module types expose module attributes for module accessors.

        for object_type in module_types:
            ref = self.importer.get_module_attribute(object_type, attrname)
            if ref and self.is_compatible_callable(location, object_type, ref):
                attrs.add(("<module>", object_type, ref))

        return attrs

    def is_compatible_callable(self, location, object_type, ref):

        """
        Return whether any invocation at 'location' involving an attribute of
        'object_type' identified by 'ref' is compatible with any arguments used.
        """

        invocation = self.reference_invocations.get(location)
        if invocation is None:
            return True

        objpath = ref.get_origin()
        if not objpath:
            return True

        parameters = self.importer.function_parameters.get(objpath)
        if not parameters:
            return True

        defaults = self.importer.function_defaults.get(objpath)
        arguments, keywords = invocation
        names = set(parameters)

        # Determine whether the specified arguments are
        # compatible with the callable signature.

        if arguments >= len(parameters) - len(defaults) and \
           arguments <= len(parameters) and \
           names.issuperset(keywords):

            return True
        else:
            init_item(self.reference_invocations_unsuitable, location, set)
            self.reference_invocations_unsuitable[location].add(ref)
            return False

    # Attribute access plan formulation.

    class_tests = (
        ("guarded", "specific", "type"),
        ("guarded", "common", "type"),
        ("test", "specific", "type"),
        ("test", "common", "type"),
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
         * any test to apply to the context
         * the method of obtaining the first attribute
         * the method of obtaining the final attribute
         * any static final attribute
         * the kinds of objects providing the final attribute
        """

        const_access = self.const_accesses_rev.get(location)

        path, name, attrnames, version = location
        remaining = attrnames.split(".")
        attrname = remaining[0]

        # Obtain reference, provider and provider kind information.

        attrs = self.reference_all_attrs[location]
        provider_types = self.reference_all_providers[location]
        provider_kinds = self.reference_all_provider_kinds[location]

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

        # Constant accesses have static providers.

        if const_access:
            base = len(provider_types) == 1 and first(provider_types)

        # Name-based accesses.

        elif name:
            ref = self.importer.identify("%s.%s" % (path, name))

            # Constant accessors are static.

            if ref and ref.static():
                base = ref.get_origin()

            # Usage of previously-generated guard and test details.

            elif test[:2] == ("constrained", "specific"):
                ref = first(accessor_types)

            elif test[:2] == ("constrained", "common"):
                ref = first(accessor_general_types)

            elif test[:2] == ("guarded", "specific"):
                ref = first(accessor_types)

            elif test[:2] == ("guarded", "common"):
                ref = first(accessor_general_types)

            # For attribute-based tests, tentatively identify a dynamic base.
            # Such tests allow single or multiple kinds of a type.

            elif test[0] == "test" and test[1] in ("common", "specific"):
                dynamic_base = test_type

            # Static accessors.

            if not base and test in self.class_tests:
                base = ref and ref.get_origin() or dynamic_base

            # Accessors that are not static but whose nature is determined.

            elif not base and ref:
                dynamic_base = ref.get_origin()

        # Determine initial accessor details.

        accessor = base or dynamic_base
        accessor_kind = len(accessor_kinds) == 1 and first(accessor_kinds) or None
        provider_kind = len(provider_kinds) == 1 and first(provider_kinds) or None

        # Traverse remaining attributes.

        traversed = []
        traversal_modes = []

        while len(attrs) == 1 and not first(attrs).has_kind("<var>"):
            attr = first(attrs)

            traversed.append(attrname)
            traversal_modes.append(accessor_kind == provider_kind and "object" or "class")

            # Consume attribute names providing unambiguous attributes.

            del remaining[0]

            if not remaining:
                break

            # Update the last static attribute.

            if attr.static():
                base = attr.get_origin()
                traversed = []
                traversal_modes = []

            # Get the access details.

            attrname = remaining[0]
            accessor = attr.get_origin()
            accessor_kind = attr.get_kind()
            provider_kind = self.importer.get_attribute_provider(attr, attrname)
            accessor_kinds = [accessor_kind]
            provider_kinds = [provider_kind]

            # Get the next attribute.

            attrs = self.importer.get_attributes(attr, attrname)

        # Where many attributes are suggested, no single attribute identity can
        # be loaded.

        else:
            attr = None

        # Determine the method of access.

        is_assignment = location in self.reference_assignments or const_access in self.reference_assignments
        is_invocation = location in self.reference_invocations or const_access in self.reference_invocations

        # Identified attribute that must be accessed via its parent.

        if attr and attr.get_name() and is_assignment:
            final_method = "static-assign"; origin = attr.get_name()

        # Static, identified attribute.

        elif attr and attr.static():
            final_method = is_assignment and "static-assign" or \
                           is_invocation and "static-invoke" or \
                           "static"
            origin = attr.final()

        # All other methods of access involve traversal.

        else:
            final_method = is_assignment and "assign" or \
                           is_invocation and "access-invoke" or \
                           "access"
            origin = None

        # First attribute accessed at a known position via the accessor.

        # Static bases support object-relative accesses only.

        if base:
            first_method = "relative-object"

        # Dynamic bases support either object- or class-relative accesses.

        elif dynamic_base:
            first_method = "relative" + (object_relative and "-object" or "") + \
                                        (class_relative and "-class" or "")

        # The fallback case is always run-time testing and access.

        else:
            first_method = "check" + (object_relative and "-object" or "") + \
                                     (class_relative and "-class" or "")

        # Determine whether an unbound method is being accessed via an instance,
        # requiring a context test.

        context_test = "ignore"

        # Assignments do not employ the context.

        if is_assignment:
            pass

        # Obtain a selection of possible attributes if no unambiguous attribute
        # was identified.

        elif not attr:

            # Use previously-deduced attributes for a simple ambiguous access.
            # Otherwise, use the final attribute name to obtain possible
            # attributes.

            if len(remaining) > 1:
                attrname = remaining[-1]

                (class_types,
                 only_instance_types,
                 module_types) = self.get_types_for_attribute(attrname)

                accessor_kinds = set()
                provider_kinds = set()

                if class_types:
                    accessor_kinds.add("<class>")
                    accessor_kinds.add("<instance>")
                    provider_kinds.add("<class>")
                if only_instance_types:
                    accessor_kinds.add("<instance>")
                    provider_kinds.add("<instance>")
                if module_types:
                    accessor_kinds.add("<module>")
                    provider_kinds.add("<module>")

                attrs = set()
                for type in combine_types(class_types, only_instance_types, module_types):
                    attrs.update(self.importer.get_attributes(type, attrname))

            always_unbound = True
            have_function = False
            have_var = False

            # Determine whether all attributes are unbound methods and whether
            # functions or unidentified attributes occur.

            for attr in attrs:
                always_unbound = always_unbound and attr.has_kind("<function>") and attr.name_parent() == attr.parent()
                have_function = have_function or attr.has_kind("<function>")
                have_var = have_var or attr.has_kind("<var>")

            # Test for class-via-instance accesses.

            if accessor_kind == "<instance>" and \
               provider_kind == "<class>":

                if always_unbound:
                    context_test = "replace"
                else:
                    context_test = "test"

            # Test for the presence of class-via-instance accesses.

            elif "<instance>" in accessor_kinds and \
                 "<class>" in provider_kinds and \
                 (have_function or have_var):

                context_test = "test"

        # With an unambiguous attribute, determine whether a test is needed.

        elif accessor_kind == "<instance>" and \
             provider_kind == "<class>" and \
             (attr.has_kind("<var>") or
              attr.has_kind("<function>") and
              attr.name_parent() == attr.parent()):

            if attr.has_kind("<var>"):
                context_test = "test"
            else:
                context_test = "replace"

        # With an unambiguous attribute with ambiguity in the access method,
        # generate a test.

        elif "<instance>" in accessor_kinds and \
             "<class>" in provider_kinds and \
             (attr.has_kind("<var>") or
              attr.has_kind("<function>") and
              attr.name_parent() == attr.parent()):

            context_test = "test"

        # Determine the nature of the context.

        context = context_test == "ignore" and "unset" or \
                  len(traversed + remaining) == 1 and \
                      (base and "base" or "original-accessor") or \
                  "final-accessor"

        return name, test, test_type, base, \
               traversed, traversal_modes, remaining, \
               context, context_test, \
               first_method, final_method, \
               origin, accessor_kinds

    def initialise_access_instructions(self):

        "Expand access plans into instruction sequences."

        for access_location, access_plan in self.access_plans.items():

            # Obtain the access details.

            name, test, test_type, base, \
                traversed, traversal_modes, attrnames, \
                context, context_test, \
                first_method, final_method, \
                origin, accessor_kinds = access_plan

            # Emit instructions by appending them to a list.

            instructions = []
            emit = instructions.append

            # Identify any static original accessor.

            if base:
                original_accessor = base

            # Employ names as contexts unless the context needs testing and
            # potentially updating. In such cases, temporary context storage is
            # used instead.

            elif name and not (context_test == "test" and
                               final_method in ("access-invoke", "static-invoke")):
                original_accessor = "<name>" # refers to the name

            # Use a generic placeholder representing the access expression in
            # the general case.

            else:
                original_accessor = "<expr>"

            # Prepare for any first attribute access.

            if traversed:
                attrname = traversed[0]
                del traversed[0]
            elif attrnames:
                attrname = attrnames[0]
                del attrnames[0]

            # Perform the first access explicitly if at least one operation
            # requires it.

            access_first_attribute = final_method in ("access", "access-invoke", "assign") or traversed or attrnames

            # Determine whether the first access involves assignment.

            assigning = not traversed and not attrnames and final_method == "assign"
            set_accessor = assigning and "<set_target_accessor>" or "<set_accessor>"
            stored_accessor = assigning and "<target_accessor>" or "<accessor>"

            # Set the context if already available.

            context_var = None

            if context == "base":
                accessor = context_var = (base,)
            elif context == "original-accessor":

                # Prevent re-evaluation of any dynamic expression by storing it.

                if original_accessor == "<expr>":
                    if final_method in ("access-invoke", "static-invoke"):
                        emit(("<set_context>", original_accessor))
                        accessor = context_var = ("<context>",)
                    else:
                        emit((set_accessor, original_accessor))
                        accessor = context_var = (stored_accessor,)
                else:
                    accessor = context_var = (original_accessor,)

            # Assigning does not set the context.

            elif context in ("final-accessor", "unset") and access_first_attribute:

                # Prevent re-evaluation of any dynamic expression by storing it.

                if original_accessor == "<expr>":
                    emit((set_accessor, original_accessor))
                    accessor = (stored_accessor,)
                else:
                    accessor = (original_accessor,)

            # Apply any test.

            if test[0] == "test":
                accessor = ("__%s_%s_%s" % test, accessor, test_type)

            # Perform the first or final access.
            # The access only needs performing if the resulting accessor is used.

            remaining = len(traversed + attrnames)

            if access_first_attribute:

                if first_method == "relative-class":
                    if assigning:
                        emit(("__store_via_class", accessor, attrname, "<assexpr>"))
                    else:
                        accessor = ("__load_via_class", accessor, attrname)

                elif first_method == "relative-object":
                    if assigning:
                        emit(("__store_via_object", accessor, attrname, "<assexpr>"))
                    else:
                        accessor = ("__load_via_object", accessor, attrname)

                elif first_method == "relative-object-class":
                    if assigning:
                        emit(("__get_class_and_store", accessor, attrname, "<assexpr>"))
                    else:
                        accessor = ("__get_class_and_load", accessor, attrname)

                elif first_method == "check-class":
                    if assigning:
                        emit(("__check_and_store_via_class", accessor, attrname, "<assexpr>"))
                    else:
                        accessor = ("__check_and_load_via_class", accessor, attrname)

                elif first_method == "check-object":
                    if assigning:
                        emit(("__check_and_store_via_object", accessor, attrname, "<assexpr>"))
                    else:
                        accessor = ("__check_and_load_via_object", accessor, attrname)

                elif first_method == "check-object-class":
                    if assigning:
                        emit(("__check_and_store_via_any", accessor, attrname, "<assexpr>"))
                    else:
                        accessor = ("__check_and_load_via_any", accessor, attrname)

            # Traverse attributes using the accessor.

            if traversed:
                for attrname, traversal_mode in zip(traversed, traversal_modes):
                    assigning = remaining == 1 and final_method == "assign"

                    # Set the context, if appropriate.

                    if remaining == 1 and final_method != "assign" and context == "final-accessor":

                        # Invoked attributes employ a separate context accessed
                        # during invocation.

                        if final_method in ("access-invoke", "static-invoke"):
                            emit(("<set_context>", accessor))
                            accessor = context_var = "<context>"

                        # A private context within the access is otherwise
                        # retained.

                        else:
                            emit(("<set_private_context>", accessor))
                            accessor = context_var = "<private_context>"

                    # Perform the access only if not achieved directly.

                    if remaining > 1 or final_method in ("access", "access-invoke", "assign"):

                        if traversal_mode == "class":
                            if assigning:
                                emit(("__store_via_class", accessor, attrname, "<assexpr>"))
                            else:
                                accessor = ("__load_via_class", accessor, attrname)
                        else:
                            if assigning:
                                emit(("__store_via_object", accessor, attrname, "<assexpr>"))
                            else:
                                accessor = ("__load_via_object", accessor, attrname)

                    remaining -= 1

            if attrnames:
                for attrname in attrnames:
                    assigning = remaining == 1 and final_method == "assign"

                    # Set the context, if appropriate.

                    if remaining == 1 and final_method != "assign" and context == "final-accessor":

                        # Invoked attributes employ a separate context accessed
                        # during invocation.

                        if final_method in ("access-invoke", "static-invoke"):
                            emit(("<set_context>", accessor))
                            accessor = context_var = "<context>"

                        # A private context within the access is otherwise
                        # retained.

                        else:
                            emit(("<set_private_context>", accessor))
                            accessor = context_var = "<private_context>"

                    # Perform the access only if not achieved directly.

                    if remaining > 1 or final_method in ("access", "access-invoke", "assign"):

                        # Constrain instructions involving certain special
                        # attribute names.

                        to_search = attrname == "__data__" and "object" or "any"

                        if assigning:
                            emit(("__check_and_store_via_%s" % to_search, accessor, attrname, "<assexpr>"))
                        else:
                            accessor = ("__check_and_load_via_%s" % to_search, accessor, attrname)

                    remaining -= 1

            # Define or emit the means of accessing the actual target.

            # Assignments to known attributes.

            if final_method == "static-assign":
                parent, attrname = origin.rsplit(".", 1)
                emit(("__store_via_object", parent, attrname, "<assexpr>"))

            # Invoked attributes employ a separate context.

            elif final_method in ("static", "static-invoke"):
                accessor = ("__load_static_ignore", origin)

            # Wrap accesses in context operations.

            if context_test == "test":

                # Test and combine the context with static attribute details.

                if final_method == "static":
                    emit(("__load_static_test", context_var, origin))

                # Test the context, storing it separately if required for the
                # immediately invoked static attribute.

                elif final_method == "static-invoke":
                    emit(("<test_context_static>", context_var, origin))

                # Test the context, storing it separately if required for an
                # immediately invoked attribute.

                elif final_method == "access-invoke":
                    emit(("<test_context_revert>", context_var, accessor))

                # Test the context and update the attribute details if
                # appropriate.

                else:
                    emit(("__test_context", context_var, accessor))

            elif context_test == "replace":

                # Produce an object with updated context.

                if final_method == "static":
                    emit(("__load_static_replace", context_var, origin))

                # Omit the context update operation where the target is static
                # and the context is recorded separately.

                elif final_method == "static-invoke":
                    pass

                # If a separate context is used for an immediate invocation,
                # produce the attribute details unchanged.

                elif final_method == "access-invoke":
                    emit(accessor)

                # Update the context in the attribute details.

                else:
                    emit(("__update_context", context_var, accessor))

            # Omit the accessor for assignments and for invocations of static
            # targets.

            elif final_method not in ("assign", "static-assign", "static-invoke"):
                emit(accessor)

            # Produce an advisory instruction regarding the context.

            if context_var:
                emit(("<context_identity>", context_var))

            self.access_instructions[access_location] = instructions
            self.accessor_kinds[access_location] = accessor_kinds

# vim: tabstop=4 expandtab shiftwidth=4
