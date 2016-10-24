#!/usr/bin/env python

"""
Optimise object layouts and generate access instruction plans.

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

from common import add_counter_item, get_attrname_from_location, init_item, \
                   sorted_output
from encoders import encode_access_location, encode_instruction, get_kinds
from os.path import exists, join
from os import makedirs
from referencing import Reference

class Optimiser:

    "Optimise objects in a program."

    def __init__(self, importer, deducer, output):

        """
        Initialise an instance using the given 'importer' and 'deducer' that
        will perform the arrangement of attributes for program objects, writing
        the results to the given 'output' directory.
        """

        self.importer = importer
        self.deducer = deducer
        self.output = output

        # Locations/offsets of attributes in objects.

        self.locations = None
        self.attr_locations = None
        self.all_attrnames = None

        # Locations of parameters in parameter tables.

        self.arg_locations = None
        self.param_locations = None
        self.all_paramnames = None

        # Specific attribute access information.

        self.access_instructions = {}

        # Object structure information.

        self.structures = {}
        self.attr_table = {}

        # Parameter list information.

        self.parameters = {}
        self.param_table = {}

        # Constant literal information.

        self.constants = []
        self.constant_numbers = {}

        # Optimiser activities.

        self.populate_objects()
        self.position_attributes()
        self.populate_parameters()
        self.position_parameters()
        self.populate_tables()
        self.populate_constants()
        self.initialise_access_instructions()

    def to_output(self):

        "Write the output files using optimisation information."

        if not exists(self.output):
            makedirs(self.output)

        self.write_objects()

    def write_objects(self):

        """
        Write object-related output.

        The locations are a list of positions indicating the attributes residing
        at each position in the different structures in a program.

        ----

        The parameter locations are a list of positions indicating the parameters
        residing at each position in the different parameter lists in a program.

        ----

        Each attribute plan provides attribute details in the following format:

        location " " name " " test " " test type " " base
                 " " traversed attributes " " traversed attribute ambiguity
                 " " traversal access modes
                 " " attributes to traverse " " attribute ambiguity
                 " " context " " access method " " static attribute

        Locations have the following format:

        qualified name of scope "." local name ":" name version

        Traversal access modes are either "class" (obtain accessor class to
        access attribute) or "object" (obtain attribute directly from accessor).

        ----

        The structures are presented as a table in the following format:

        qualified name " " attribute names

        The attribute names are separated by ", " characters and indicate the
        attribute provided at each position in the structure associated with the
        given type. Where no attribute is provided at a particular location
        within a structure, "-" is given.

        ----

        The parameters are presented as a table in the following format:

        qualified name " " parameter details

        The parameter details are separated by ", " characters and indicate
        the parameter name and list position for each parameter described at
        each location in the parameter table associated with the given
        function. Where no parameter details are provided at a particular
        location within a parameter table, "-" is given. The name and list
        position are separated by a colon (":").

        ----

        The attribute table is presented as a table in the following format:

        qualified name " " attribute identifiers

        Instead of attribute names, identifiers defined according to the order
        given in the "attrnames" file are employed to denote the attributes
        featured in each type's structure. Where no attribute is provided at a
        particular location within a structure, "-" is given.

        ----

        The parameter table is presented as a table in the following format:

        qualified name " " parameter details

        Instead of parameter names, identifiers defined according to the order
        given in the "paramnames" file are employed to denote the parameters
        featured in each function's parameter table. Where no parameter is
        provided at a particular location within a table, "-" is given.

        ----

        The ordered list of attribute names is given in the "attrnames" file.

        ----

        The ordered list of parameter names is given in the "paramnames" file.

        ----

        The ordered list of constant literals is given in the "constants" file.
        """

        f = open(join(self.output, "locations"), "w")
        try:
            for attrnames in self.locations:
                print >>f, sorted_output(attrnames)

        finally:
            f.close()

        f = open(join(self.output, "parameter_locations"), "w")
        try:
            for argnames in self.arg_locations:
                print >>f, sorted_output(argnames)

        finally:
            f.close()

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

        f = open(join(self.output, "structures"), "w")
        try:
            structures = self.structures.items()
            structures.sort()

            for name, attrnames in structures:
                print >>f, name, ", ".join([s or "-" for s in attrnames])

        finally:
            f.close()

        f = open(join(self.output, "parameters"), "w")
        try:
            parameters = self.parameters.items()
            parameters.sort()

            for name, argnames in parameters:
                print >>f, name, ", ".join([s and ("%s:%d" % s) or "-" for s in argnames])

        finally:
            f.close()

        f = open(join(self.output, "attrtable"), "w")
        try:
            attr_table = self.attr_table.items()
            attr_table.sort()

            for name, attrcodes in attr_table:
                print >>f, name, ", ".join([i is not None and str(i) or "-" for i in attrcodes])

        finally:
            f.close()

        f = open(join(self.output, "paramtable"), "w")
        try:
            param_table = self.param_table.items()
            param_table.sort()

            for name, paramcodes in param_table:
                print >>f, name, ", ".join([s and ("%d:%d" % s) or "-" for s in paramcodes])

        finally:
            f.close()

        f = open(join(self.output, "attrnames"), "w")
        try:
            for name in self.all_attrnames:
                print >>f, name

        finally:
            f.close()

        f = open(join(self.output, "paramnames"), "w")
        try:
            for name in self.all_paramnames:
                print >>f, name

        finally:
            f.close()

        f = open(join(self.output, "constants"), "w")
        try:
            constants = [(n, value) for (value, n) in self.constants.items()]
            constants.sort()
            for n, value in constants:
                print >>f, repr(value)

        finally:
            f.close()

    def populate_objects(self):

        "Populate objects using attribute and usage information."

        all_attrs = {}

        # Partition attributes into separate sections so that class and instance
        # attributes are treated separately.

        for source, objtype in [
            (self.importer.all_class_attrs, "<class>"),
            (self.importer.all_instance_attrs, "<instance>"),
            (self.importer.all_module_attrs, "<module>")
            ]:
            for name, attrs in source.items():
                all_attrs[(objtype, name)] = attrs

        self.locations = get_allocated_locations(all_attrs, get_attributes_and_sizes)

    def populate_parameters(self):

        "Populate parameter tables using parameter information."

        self.arg_locations = [set()] + get_allocated_locations(self.importer.function_parameters, get_parameters_and_sizes)

    def position_attributes(self):

        "Position specific attribute references."

        # Reverse the location mappings.

        attr_locations = self.attr_locations = {}

        for i, attrnames in enumerate(self.locations):
            for attrname in attrnames:
                attr_locations[attrname] = i

        # Record the structures.

        for source, objtype in [
            (self.importer.all_class_attrs, "<class>"),
            (self.importer.all_instance_attrs, "<instance>"),
            (self.importer.all_module_attrs, "<module>")
            ]:

            for name, attrnames in source.items():
                key = Reference(objtype, name)
                l = self.structures[key] = [None] * len(attrnames)
                for attrname in attrnames:
                    position = attr_locations[attrname]
                    if position >= len(l):
                        l.extend([None] * (position - len(l) + 1))
                    l[position] = attrname

    def initialise_access_instructions(self):

        "Expand access plans into instruction sequences."

        for access_location, access_plan in self.deducer.access_plans.items():

            # Obtain the access details.

            name, test, test_type, base, traversed, traversal_modes, \
                attrnames, context, context_test, first_method, final_method, origin = access_plan

            instructions = []
            emit = instructions.append

            if base:
                original_accessor = base
            else:
                original_accessor = "<expr>" # use a generic placeholder

            # Prepare for any first attribute access.

            if traversed:
                attrname = traversed[0]
                del traversed[0]
            elif attrnames:
                attrname = attrnames[0]
                del attrnames[0]

            # Perform the first access explicitly if at least one operation
            # requires it.

            access_first_attribute = final_method in ("access", "assign") or traversed or attrnames

            # Determine whether the first access involves assignment.

            assigning = not traversed and not attrnames and final_method == "assign"

            # Set the context if already available.

            if context == "base":
                accessor = context_var = (base,)
            elif context == "original-accessor":

                # Prevent re-evaluation of any dynamic expression by storing it.

                if original_accessor == "<expr>":
                    emit(("__set_accessor", original_accessor))
                    accessor = context_var = ("<accessor>",)
                else:
                    accessor = context_var = (original_accessor,)

            # Assigning does not set the context.

            elif context in ("final-accessor", "unset") and access_first_attribute:

                # Prevent re-evaluation of any dynamic expression by storing it.

                if original_accessor == "<expr>":
                    emit(("__set_accessor", original_accessor))
                    accessor = ("<accessor>",)
                else:
                    accessor = (original_accessor,)

            # Apply any test.

            if test == "specific-type":
                accessor = ("__test_specific_type", accessor, test_type)
            elif test == "specific-instance":
                accessor = ("__test_specific_instance", accessor, test_type)
            elif test == "specific-object":
                accessor = ("__test_specific_object", accessor, test_type)
            elif test == "common-type":
                accessor = ("__test_common_type", accessor, test_type)
            elif test == "common-instance":
                accessor = ("__test_common_instance", accessor, test_type)
            elif test == "common-object":
                accessor = ("__test_common_object", accessor, test_type)

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
                        emit(("__set_context", accessor))
                        accessor = context_var = "<context>"

                    # Perform the access only if not achieved directly.

                    if remaining > 1 or final_method in ("access", "assign"):

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
                        emit(("__set_context", accessor))
                        accessor = context_var = "<context>"

                    # Perform the access only if not achieved directly.

                    if remaining > 1 or final_method in ("access", "assign"):

                        if assigning:
                            emit(("__check_and_store_via_any", accessor, attrname, "<assexpr>"))
                        else:
                            accessor = ("__check_and_load_via_any", accessor, attrname)

                    remaining -= 1

            # Define or emit the means of accessing the actual target.

            if final_method == "static-assign":
                parent, attrname = origin.rsplit(".", 1)
                emit(("__store_via_object", parent, attrname, "<assexpr>"))

            elif final_method == "static":
                accessor = ("__load_static", origin)

            elif final_method == "static-invoke":
                kind = self.importer.get_object(origin).get_kind()
                accessor = ("__encode_callable", origin, kind)

            # Wrap accesses in context operations.

            if context_test == "test":
                emit(("__test_context", context_var, accessor))

            elif context_test == "replace":

                # Static invocation targets have a context added but no other
                # transformation performed.

                if final_method == "static-invoke":
                    emit(("__update_context", context_var, accessor))

                # Other invocation targets gain a context and have the bound
                # version of the callable activated.

                else:
                    emit(("__replace_context", context_var, accessor))

            elif final_method not in ("assign", "static-assign"):
                emit(accessor)

            self.access_instructions[access_location] = instructions

    def get_ambiguity_for_attributes(self, attrnames):

        """
        Return a list of attribute position alternatives corresponding to each
        of the given 'attrnames'.
        """

        ambiguity = []

        for attrname in attrnames:
            position = self.attr_locations[attrname]
            ambiguity.append(len(self.locations[position]))

        return ambiguity

    def position_parameters(self):

        "Position the parameters for each function's parameter table."

        # Reverse the location mappings.

        param_locations = self.param_locations = {}

        for i, argnames in enumerate(self.arg_locations):

            # Position the arguments.

            for argname in argnames:
                param_locations[argname] = i

        for name, argnames in self.importer.function_parameters.items():

            # Allocate an extra context parameter in the table.

            l = self.parameters[name] = [None] * len(argnames)

            # Store an entry for the name along with the name's position in the
            # parameter list.

            for pos, argname in enumerate(argnames):

                # Position the argument in the table.

                position = param_locations[argname]
                if position >= len(l):
                    l.extend([None] * (position - len(l) + 1))

                # Indicate an argument list position starting from 1 (after the
                # initial context argument).

                l[position] = (argname, pos)

    def populate_tables(self):

        """
        Assign identifiers to attributes and encode structure information using
        these identifiers.
        """

        self.all_attrnames, d = self._get_name_mapping(self.attr_locations)

        # Record the numbers indicating the locations of the names.

        for key, attrnames in self.structures.items():
            l = self.attr_table[key] = []
            for attrname in attrnames:
                if attrname is None:
                    l.append(None)
                else:
                    l.append(d[attrname])

        self.all_paramnames, d = self._get_name_mapping(self.param_locations)

        # Record the numbers indicating the locations of the names.

        for key, values in self.parameters.items():
            l = self.param_table[key] = []
            for value in values:
                if value is None:
                    l.append(None)
                else:
                    name, pos = value
                    l.append((d[name], pos))

    def _get_name_mapping(self, locations):

        """
        Get a sorted list of names from 'locations', then map them to
        identifying numbers. Return the list and the mapping.
        """

        all_names = locations.keys()
        all_names.sort()
        return all_names, dict([(name, i) for i, name in enumerate(all_names)])

    def populate_constants(self):

        """
        Obtain a collection of distinct constant literals, building a mapping
        from constant references to those in this collection.
        """

        # Obtain mappings from constant values to identifiers.

        self.constants = {}

        for path, constants in self.importer.all_constants.items():
            for constant, n in constants.items():

                # Record constants and obtain a number for them.

                add_counter_item(self.constants, constant)

        self.constant_numbers = {}

        for name, (value, value_type) in self.importer.all_constant_values.items():
            self.constant_numbers[name] = self.constants[value]

def combine_rows(a, b):
    c = []
    for i, j in zip(a, b):
        if i is None or j is None:
            c.append(i or j)
        else:
            return None
    return c

def get_attributes_and_sizes(d):

    """
    Return a matrix of attributes, a list of type names corresponding to columns
    in the matrix, and a list of ranked sizes each indicating...

     * a weighted size depending on the kind of object
     * the minimum size of an object employing an attribute
     * the number of free columns in the matrix for the attribute
     * the attribute name itself
    """

    attrs = {}
    sizes = {}
    objtypes = {}

    for name, attrnames in d.items():
        objtype, _name = name

        for attrname in attrnames:

            # Record each type supporting the attribute.

            init_item(attrs, attrname, set)
            attrs[attrname].add(name)

            # Maintain a record of the smallest object size supporting the given
            # attribute.

            if not sizes.has_key(attrname):
                sizes[attrname] = len(attrnames)
            else:
                sizes[attrname] = min(sizes[attrname], len(attrnames))

            # Record the object types/kinds supporting the attribute.

            init_item(objtypes, attrname, set)
            objtypes[attrname].add(objtype)

    # Obtain attribute details in order of size and occupancy.

    names = d.keys()

    rsizes = []
    for attrname, size in sizes.items():
        priority = "<instance>" in objtypes[attrname] and 0.5 or 1
        occupied = len(attrs[attrname])
        key = (priority * size, size, len(names) - occupied, attrname)
        rsizes.append(key)

    rsizes.sort()

    # Make a matrix of attributes.

    matrix = {}
    for attrname, types in attrs.items():
        row = []
        for name in names:
            if name in types:
                row.append(attrname)
            else:
                row.append(None)
        matrix[attrname] = row

    return matrix, names, rsizes

def get_parameters_and_sizes(d):

    """
    Return a matrix of parameters, a list of functions corresponding to columns
    in the matrix, and a list of ranked sizes each indicating...

     * a weighted size depending on the kind of object
     * the minimum size of a parameter list employing a parameter
     * the number of free columns in the matrix for the parameter
     * the parameter name itself

    This is a slightly simpler version of the above 'get_attributes_and_sizes'
    function.
    """

    params = {}
    sizes = {}

    for name, argnames in d.items():
        for argname in argnames:

            # Record each function supporting the parameter.

            init_item(params, argname, set)
            params[argname].add(name)

            # Maintain a record of the smallest parameter list supporting the
            # given parameter.

            if not sizes.has_key(argname):
                sizes[argname] = len(argnames)
            else:
                sizes[argname] = min(sizes[argname], len(argnames))

    # Obtain attribute details in order of size and occupancy.

    names = d.keys()

    rsizes = []
    for argname, size in sizes.items():
        occupied = len(params[argname])
        key = (size, size, len(names) - occupied, argname)
        rsizes.append(key)

    rsizes.sort()

    # Make a matrix of parameters.

    matrix = {}
    for argname, types in params.items():
        row = []
        for name in names:
            if name in types:
                row.append(argname)
            else:
                row.append(None)
        matrix[argname] = row

    return matrix, names, rsizes

def get_allocated_locations(d, fn):

    """
    Return a list where each element corresponds to a structure location and
    contains a set of attribute names that may be stored at that location, given
    a mapping 'd' whose keys are (object type, object name) tuples and whose
    values are collections of attributes.
    """

    matrix, names, rsizes = fn(d)
    allocated = []

    x = 0
    while x < len(rsizes):
        weight, size, free, attrname = rsizes[x]
        base = matrix[attrname]
        y = x + 1
        while y < len(rsizes):
            _weight, _size, _free, _attrname = rsizes[y]
            occupied = len(names) - _free
            if occupied > free:
                break
            new = combine_rows(base, matrix[_attrname])
            if new:
                del matrix[_attrname]
                del rsizes[y]
                base = new
                free -= occupied
            else:
                y += 1
        allocated.append(base)
        x += 1

    # Return the list of attribute names from each row of the allocated
    # attributes table.

    locations = []
    for attrnames in allocated:
        l = set()
        for attrname in attrnames:
            if attrname:
                l.add(attrname)
        locations.append(l)
    return locations

# vim: tabstop=4 expandtab shiftwidth=4
