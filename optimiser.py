#!/usr/bin/env python

"""
Optimise object layouts and generate access instruction plans.

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

from common import add_counter_item, get_attrname_from_location, init_item, \
                   sorted_output, CommonOutput
from encoders import digest, encode_access_location, encode_instruction, get_kinds
from errors import OptimiseError
from os.path import exists, join
from os import makedirs
from referencing import decode_reference, Reference

class Optimiser(CommonOutput):

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

        # Detection of differences between any existing structure or signature
        # information and the generated information.

        self.differing_structures = []
        self.differing_parameters = []

        # Locations/offsets of attributes in objects.

        self.locations = None
        self.existing_locations = None

        self.attr_locations = None

        # Attribute code assignments.

        self.all_attrnames = None
        self.existing_attrnames = None

        # Locations of parameters in parameter tables.

        self.arg_locations = None
        self.existing_arg_locations = None

        self.param_locations = None

        # Parameter code assignments.

        self.all_paramnames = None
        self.existing_paramnames = None

        # Specific attribute access information.

        self.access_instructions = {}
        self.accessor_kinds = {}

        # Object structure information.

        self.structures = {}
        self.existing_structures = None
        self.attr_table = {}

        # Parameter list information.

        self.parameters = {}
        self.existing_parameters = None
        self.param_table = {}

        # Constant literal information.

        self.constants = []
        self.constant_numbers = {}
        self.digests = {}

        # Optimiser activities.

        self.from_output()

        # Define or redefine structure information.

        self.populate_objects()
        self.position_attributes()
        self.populate_parameters()
        self.position_parameters()
        self.populate_tables()
        self.populate_constants()
        self.initialise_access_instructions()

    def need_reset(self):

        """
        Return whether attribute or parameter information has changed, requiring
        the reset/recompilation of all source files.
        """

        return self.differing_structures or self.differing_parameters

    def from_output(self):

        "Read input files that influence optimisation."

        # Remove any output for a different program.

        self.check_output()

        # Existing attribute and parameter positioning information.

        self.existing_locations = self.read_locations("locations", self._line_to_list, list)
        self.existing_arg_locations = self.read_locations("parameter_locations", self._line_to_list, list)

        # Existing attribute and parameter code information.

        self.existing_attrnames = self.read_locations("attrnames", lambda x: x, lambda x: None)
        self.existing_paramnames = self.read_locations("paramnames", lambda x: x, lambda x: None)

        # Existing structure and signature information.

        self.existing_structures = dict(self.read_locations("structures", self._line_to_structure_pairs, list))
        self.existing_parameters = dict(self.read_locations("parameters", self._line_to_signature_pairs, list))

    def _line_to_list(self, line):

        "Convert comma-separated values in 'line' to a list of values."

        return line.split(", ")

    def _line_to_signature_pairs(self, line):

        "Convert comma-separated values in 'line' to a list of pairs of values."

        l = []
        objpath, line = line.split(" ", 1)
        for values in line.split(", "):
            if values != "-":
                name, pos = values.split(":")
                l.append((name, int(pos)))
            else:
                l.append(None)
        return (objpath, l)

    def _line_to_structure_pairs(self, line):

        "Convert comma-separated values in 'line' to a list of pairs of values."

        l = []
        ref, line = line.split(" ", 1)
        values = map(lambda x: x != '-' and x or None, line.split(", "))
        return (decode_reference(ref), values)

    def read_locations(self, filename, decode, empty):

        """
        Read location details from 'filename', using 'decode' to convert each
        line and 'empty' to produce an empty result where no data is given on a
        line, returning a collection.
        """

        filename = join(self.output, filename)
        collection = []

        if exists(filename):
            f = open(filename)
            try:
                for line in f.readlines():
                    line = line.rstrip()
                    if line:
                        attrnames = decode(line)
                    else:
                        attrnames = empty()

                    collection.append(attrnames)
            finally:
                f.close()

        return collection

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
                l = []
                for s in argnames:
                    l.append(s and ("%s:%d" % s) or "-")
                print >>f, name, ", ".join(l)

        finally:
            f.close()

        f = open(join(self.output, "attrtable"), "w")
        try:
            attr_table = self.attr_table.items()
            attr_table.sort()

            for name, attrcodes in attr_table:
                l = []
                for i in attrcodes:
                    l.append(i is not None and str(i) or "-")
                print >>f, name, ", ".join(l)

        finally:
            f.close()

        f = open(join(self.output, "paramtable"), "w")
        try:
            param_table = self.param_table.items()
            param_table.sort()

            for name, paramcodes in param_table:
                l = []
                for s in paramcodes:
                    l.append(s and ("%d:%d" % s) or "-")
                print >>f, name, ", ".join(l)

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
            constants = []
            for (value, value_type, encoding), n in self.constants.items():
                constants.append((n, value_type, encoding, value))
            constants.sort()
            for n, value_type, encoding, value in constants:
                print >>f, value_type, encoding or "{}", repr(value)

        finally:
            f.close()

    def populate_objects(self):

        "Populate objects using attribute and usage information."

        self.all_attrs = {}

        # Partition attributes into separate sections so that class and instance
        # attributes are treated separately.

        for source, objkind in [
            (self.importer.all_class_attrs, "<class>"),
            (self.importer.all_instance_attrs, "<instance>"),
            (self.importer.all_module_attrs, "<module>")
            ]:

            for name, attrnames in source.items():

                # Remove temporary names from structures.

                attrnames = filter(lambda x: not x.startswith("$t"), attrnames)
                self.all_attrs[(objkind, name)] = attrnames

        self.locations = get_allocated_locations(self.all_attrs,
            get_attributes_and_sizes, self.existing_locations)

    def populate_parameters(self):

        "Populate parameter tables using parameter information."

        # Allocate positions from 1 onwards, ignoring the context argument.

        self.arg_locations = [set()] + get_allocated_locations(
            self.importer.function_parameters, get_parameters_and_sizes,
            self.existing_arg_locations[1:])

    def position_attributes(self):

        "Position specific attribute references."

        # Reverse the location mappings, producing a mapping from attribute
        # names to positions.

        attr_locations = self.attr_locations = {}
        self._position_attributes(attr_locations, self.locations)

        # Add any previously-known attribute locations. This prevents attributes
        # from being assigned different identifying codes by preserving obsolete
        # attribute codes.

        if self.existing_locations:
            self._position_attributes(attr_locations, self.existing_locations)

        # Record the structures.

        for (objkind, name), attrnames in self.all_attrs.items():
            key = Reference(objkind, name)
            l = self.structures[key] = [None] * len(attrnames)

            for attrname in attrnames:
                position = attr_locations[attrname]
                if position >= len(l):
                    l.extend([None] * (position - len(l) + 1))
                l[position] = attrname

            # Test the structure against any existing attributes.

            if self.existing_structures:
                if self.existing_structures.has_key(key) and self.existing_structures[key] != l:
                    self.differing_structures.append(key)

    def _position_attributes(self, d, l):

        """
        For each attribute, store a mapping in 'd' to the index in 'l' at which
        it can be found.
        """

        for i, attrnames in enumerate(l):
            for attrname in attrnames:
                if not d.has_key(attrname):
                    d[attrname] = i

    def initialise_access_instructions(self):

        "Expand access plans into instruction sequences."

        for access_location, access_plan in self.deducer.access_plans.items():

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

                        if assigning:
                            emit(("__check_and_store_via_any", accessor, attrname, "<assexpr>"))
                        else:
                            accessor = ("__check_and_load_via_any", accessor, attrname)

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

        # Reverse the location mappings, producing a mapping from parameter
        # names to positions.

        param_locations = self.param_locations = {}
        self._position_attributes(param_locations, self.arg_locations)

        for name, argnames in self.importer.function_parameters.items():

            # Allocate an extra context parameter in the table.

            l = self.parameters[name] = [None] + [None] * len(argnames)

            # Store an entry for the name along with the name's position in the
            # parameter list.

            for pos, argname in enumerate(argnames):

                # Position the argument in the table.

                position = param_locations[argname]
                if position >= len(l):
                    l.extend([None] * (position - len(l) + 1))

                # Indicate an argument list position starting from 1 (after the
                # initial context argument).

                l[position] = (argname, pos + 1)

            # Test the structure against any existing parameters.

            if self.existing_parameters:
                if self.existing_parameters.has_key(name) and self.existing_parameters[name] != l:
                    self.differing_parameters.append(name)

    def populate_tables(self):

        """
        Assign identifiers to attributes and encode structure information using
        these identifiers.
        """

        self.all_attrnames, d = self._get_name_mapping(self.attr_locations, self.existing_attrnames)

        # Record the numbers indicating the locations of the names.

        for key, attrnames in self.structures.items():
            l = self.attr_table[key] = []
            for attrname in attrnames:
                if attrname is None:
                    l.append(None)
                else:
                    l.append(d[attrname])

        self.all_paramnames, d = self._get_name_mapping(self.param_locations, self.existing_paramnames)

        # Record the numbers indicating the locations of the names.

        for key, values in self.parameters.items():
            l = self.param_table[key] = []
            for value in values:
                if value is None:
                    l.append(None)
                else:
                    name, pos = value
                    l.append((d[name], pos))

    def _get_name_mapping(self, locations, existing=None):

        """
        Get a sorted list of names from 'locations', then map them to
        identifying numbers. Preserve the identifiers from the 'existing' list,
        if specified. Return the list and the mapping.
        """

        d = {}
        l = []

        i = 0
        all_names = set(locations.keys())

        # Preserve the existing identifiers, if available.

        if existing:
            for name in existing:
                d[name] = i
                l.append(name)
                if name in all_names:
                    all_names.remove(name)
                i += 1

        # Include all remaining names in order.

        all_names = list(all_names)
        all_names.sort()

        for name in all_names:
            if not d.has_key(name):
                d[name] = i
                l.append(name)
                i += 1

        return l, d

    def populate_constants(self):

        """
        Obtain a collection of distinct constant literals, building a mapping
        from constant references to those in this collection.
        """

        # Obtain mappings from constant values to identifiers.

        self.constants = {}

        for path, constants in self.importer.all_constants.items():

            # Record constants and obtain a number for them.
            # Each constant is actually (value, value_type, encoding).

            for constant, n in constants.items():
                d = digest(constant)
                self.constants[constant] = d

                # Make sure the digests are really distinct for different
                # constants.

                if self.digests.has_key(d):
                    if self.digests[d] != constant:
                        raise OptimiseError, "Digest %s used for distinct constants %r and %r." % (
                                             d, self.digests[d], constant)
                else:
                    self.digests[d] = constant

        # Establish a mapping from local constant identifiers to consolidated
        # constant identifiers.

        self.constant_numbers = {}

        for name, constant in self.importer.all_constant_values.items():
            self.constant_numbers[name] = self.constants[constant]

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
    Get attribute and size information for the object attributes defined by 'd'
    providing a mapping from (object kind, type name) to attribute names.

    Return a matrix of attributes (each row entry consisting of column values
    providing attribute names, with value positions corresponding to types
    providing such attributes), a list of the type names corresponding to the
    columns in the matrix, and a list of ranked sizes each indicating...

     * a weighted size depending on the kind of object
     * the minimum size of an object employing an attribute
     * the number of free columns in the matrix for the attribute
     * the attribute name itself
    """

    attrs = {}
    sizes = {}
    objkinds = {}

    for objtype, attrnames in d.items():
        objkind, _name = objtype

        for attrname in attrnames:

            # Record each type supporting the attribute.

            init_item(attrs, attrname, set)
            attrs[attrname].add(objtype)

            # Maintain a record of the smallest object size supporting the given
            # attribute.

            if not sizes.has_key(attrname):
                sizes[attrname] = len(attrnames)
            else:
                sizes[attrname] = min(sizes[attrname], len(attrnames))

            # Record the object types/kinds supporting the attribute.

            init_item(objkinds, attrname, set)
            objkinds[attrname].add(objkind)

    # Obtain attribute details in order of size and occupancy.

    all_objtypes = d.keys()

    rsizes = []
    for attrname, size in sizes.items():
        priority = "<instance>" in objkinds[attrname] and 0.5 or 1
        occupied = len(attrs[attrname])
        key = (priority * size, size, len(all_objtypes) - occupied, attrname)
        rsizes.append(key)

    rsizes.sort()

    # Make a matrix of attributes.

    matrix = {}
    for attrname, objtypes in attrs.items():

        # Traverse the object types, adding the attribute name if the object
        # type supports the attribute, adding None otherwise.

        row = []
        for objtype in all_objtypes:
            if objtype in objtypes:
                row.append(attrname)
            else:
                row.append(None)
        matrix[attrname] = row

    return matrix, all_objtypes, rsizes

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

def get_allocated_locations(d, fn, existing=None):

    """
    Return a list where each element corresponds to a structure location and
    contains a set of attribute names that may be stored at that location, given
    a mapping 'd' whose keys are (object kind, object name) tuples and whose
    values are collections of attributes.
    """

    matrix, names, rsizes = fn(d)
    allocated = []

    # Verify any existing allocation.

    allocated_attrnames = set()

    if existing:
        for attrnames in existing:

            # Handle empty positions.

            if not attrnames:
                allocated.append([None] * len(names))
                continue

            base = None

            for attrname in attrnames:

                # Skip presumably-removed attribute names.

                if not matrix.has_key(attrname):
                    continue

                # Handle the first attribute name.

                if base is None:
                    base = matrix[attrname]
                    allocated_attrnames.add(attrname)
                    continue

                # Combine existing and new attribute positioning.

                new = combine_rows(base, matrix[attrname])

                if new:
                    base = new
                    allocated_attrnames.add(attrname)
                else:
                    raise OptimiseError, "Attribute %s cannot be explicitly positioned at %d." % \
                                         (attrname, len(allocated))

            # Handle empty positions.

            if base:
                allocated.append(base)
            else:
                allocated.append([None] * len(names))

    # Try to allocate each attribute name in turn.

    x = 0
    pos = 0

    while x < len(rsizes):

        # Obtain any previous allocation at the current position. Start at the
        # current attribute looking for allocations to combine.

        if pos < len(allocated):
            base = allocated[pos]
            free = base.count(None)
            y = x

        # Obtain the object information for the attribute name.

        else:
            weight, size, free, attrname = rsizes[x]

            # Ignore allocated attribute names.

            if attrname in allocated_attrnames:
                x += 1
                continue

            # Start at the next attribute looking for allocations to combine.

            base = matrix[attrname]
            y = x + 1

        # Examine attribute names that follow in the ranking, attempting to
        # accumulate compatible attributes that can co-exist in the same
        # position within structures.

        while y < len(rsizes):
            _weight, _size, _free, _attrname = rsizes[y]

            # Ignore allocated attribute names.

            if _attrname in allocated_attrnames:
                y += 1
                continue

            # Determine whether this attribute is supported by too many types
            # to co-exist.

            occupied = len(names) - _free
            if occupied > free:
                break

            # Merge the attribute support for both this and the currently
            # considered attribute, testing for conflicts. Adopt the merged row
            # details if they do not conflict.

            new = combine_rows(base, matrix[_attrname])
            if new:
                del matrix[_attrname]
                del rsizes[y]
                base = new
                free -= occupied

            # Otherwise, look for other compatible attributes.

            else:
                y += 1

        # Allocate the merged details at the current position.

        if pos < len(allocated):
            allocated[pos] = base
            pos += 1
        else:
            x += 1
            allocated.append(base)

    return allocations_to_sets(allocated)

def allocations_to_sets(allocated):

    """
    Return the list of attribute names from each row of the 'allocated'
    attributes table.
    """

    locations = []

    for attrnames in allocated:
        l = set()

        # Convert populated allocations.

        if attrnames:
            for attrname in attrnames:
                if attrname:
                    l.add(attrname)

        locations.append(l)

    return locations

# vim: tabstop=4 expandtab shiftwidth=4
