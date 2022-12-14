#!/usr/bin/env python

"""
Optimise object layouts and generate access instruction plans.

Copyright (C) 2014, 2015, 2016, 2017, 2018 Paul Boddie <paul@boddie.org.uk>

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

from common import init_item, sorted_output, CommonOutput
from encoders import digest
from errors import OptimiseError
from os.path import exists, join
from os import makedirs
from referencing import decode_reference, Reference

class Optimiser(CommonOutput):

    "Optimise objects in a program."

    def __init__(self, importer, deducer, output,
        attrnames_filename=None, locations_filename=None,
        paramnames_filename=None, parameter_locations_filename=None):

        """
        Initialise an instance using the given 'importer' and 'deducer' that
        will perform the arrangement of attributes for program objects, writing
        the results to the given 'output' directory.

        If 'attrnames_filename', 'locations_filename', 'paramnames_filename', or
        'parameter_locations_filename' are given, they will be used to
        explicitly indicate existing attribute code, attribute position,
        parameter code, and parameter position information respectively.
        """

        self.importer = importer
        self.deducer = deducer
        self.output = output

        # Explicitly-specified attribute and parameter sources.

        self.attrnames_filename = attrnames_filename
        self.locations_filename = locations_filename
        self.paramnames_filename = paramnames_filename
        self.parameter_locations_filename = parameter_locations_filename

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
        self.indicated_attrnames = None

        # Locations of parameters in parameter tables.

        self.arg_locations = None
        self.existing_arg_locations = None

        self.param_locations = None

        # Parameter code assignments.

        self.all_paramnames = None
        self.existing_paramnames = None
        self.indicated_paramnames = None

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

        # Existing attribute and parameter positioning information. This
        # influences the positions of attributes and parameters found in the
        # program.

        locations_filename = self.locations_filename or \
                             join(self.output, "locations")

        parameter_locations_filename = self.parameter_locations_filename or \
                                       join(self.output, "parameter_locations")

        self.existing_locations = self.read_data(locations_filename, self._line_to_list, list)
        self.existing_arg_locations = self.read_data(parameter_locations_filename, self._line_to_list, list)

        # Existing attribute and parameter code information. This is used to
        # check the compatibility of the output against any assignments
        # previously made.

        identity = lambda x: x
        none = lambda x: None

        attrnames_filename = join(self.output, "attrnames")
        paramnames_filename = join(self.output, "paramnames")

        self.existing_attrnames = self.read_data(attrnames_filename, identity, none)
        self.existing_paramnames = self.read_data(paramnames_filename, identity, none)

        # Explicitly-specified attribute name and parameter name codes. These
        # direct assignment of codes in the program.

        self.indicated_attrnames = self.attrnames_filename and \
                                   self.read_data(self.attrnames_filename, identity, none)

        self.indicated_paramnames = self.paramnames_filename and \
                                    self.read_data(self.paramnames_filename, identity, none)

        # Existing structure and signature information. This is used to check
        # the output and detect whether structures or signatures have changed.

        structures_filename = join(self.output, "structures")
        parameters_filename = join(self.output, "parameters")

        self.existing_structures = dict(self.read_data(structures_filename, self._line_to_structure_pairs, list))
        self.existing_parameters = dict(self.read_data(parameters_filename, self._line_to_signature_pairs, list))

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

    def read_data(self, filename, decode, empty):

        """
        Read location details from 'filename', using 'decode' to convert each
        line and 'empty' to produce an empty result where no data is given on a
        line, returning a collection.
        """

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

    def is_allocated_attribute(self, attrname):

        "Return whether 'attrname' is to be allocated in an object."

        return not attrname.startswith("$t")

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

                attrnames = filter(self.is_allocated_attribute, attrnames)
                self.all_attrs[Reference(objkind, name)] = attrnames

        try:
            self.locations = get_allocated_locations(self.all_attrs,
                get_attributes_and_sizes, self.existing_locations)

        # Uphold positioning conflicts only if the existing locations were
        # explicitly specified.

        except OptimiseError:
            if self.locations_filename:
                raise

            # Otherwise, reposition attributes, causing the program to be
            # regenerated.

            self.locations = get_allocated_locations(self.all_attrs,
                get_attributes_and_sizes)

    def populate_parameters(self):

        "Populate parameter tables using parameter information."

        # Allocate positions from 1 onwards, ignoring the context argument.

        try:
            self.arg_locations = [set()] + get_allocated_locations(
                self.importer.function_parameters, get_parameters_and_sizes,
                self.existing_arg_locations[1:])

        # Uphold positioning conflicts only if the existing locations were
        # explicitly specified.

        except OptimiseError:
            if self.parameter_locations_filename:
                raise

            # Otherwise, reposition parameters, causing the program to be
            # regenerated.

            self.arg_locations = [set()] + get_allocated_locations(
                self.importer.function_parameters, get_parameters_and_sizes)

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

        for key, attrnames in self.all_attrs.items():
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

        # Initialise the mapping from attribute names to codes.

        l = self.all_attrnames = []; d = {}
        self._init_name_mapping(l, d, self.existing_attrnames)
        if self.indicated_attrnames:
            self._init_name_mapping(l, d, self.indicated_attrnames)
        self._update_name_mapping(l, d, self.attr_locations)

        # Record the numbers indicating the locations of the names.

        for key, attrnames in self.structures.items():
            l = self.attr_table[key] = []
            for attrname in attrnames:
                if attrname is None:
                    l.append(None)
                else:
                    l.append(d[attrname])

        # Initialise the mapping from parameter names to codes.

        l = self.all_paramnames = []; d = {}
        self._init_name_mapping(l, d, self.existing_paramnames)
        if self.indicated_paramnames:
            self._init_name_mapping(l, d, self.indicated_paramnames)
        self._update_name_mapping(l, d, self.param_locations)

        # Record the numbers indicating the locations of the names.

        for key, values in self.parameters.items():
            l = self.param_table[key] = []
            for value in values:
                if value is None:
                    l.append(None)
                else:
                    name, pos = value
                    l.append((d[name], pos))

    def _init_name_mapping(self, l, d, existing):

        """
        Initialise the name collection 'l', with mapping 'd', using the
        'existing' mapping.
        """

        i = 0

        for name in existing:

            # Test for the name in another position.

            if d.has_key(name):
                if d[name] != i:
                    raise OptimiseError, "Name %s has conflicting codes: %d and %d." % \
                                         (name, d[name], i)
            else:

                # Test for other usage of the position.

                if i < len(l):
                    if l[i] != name:
                        raise OptimiseError, "Position %d has conflicting names: %s and %s." % \
                                             (i, name, d[name])
                    l[i] = name
                else:
                    l.append(name)

                d[name] = i

            i += 1

    def _update_name_mapping(self, l, d, locations):

        """
        Using any existing identifiers supplied by 'l' and 'd', update the
        identifiers using a sorted list of names from 'locations'.
        """

        all_names = list(locations.keys())
        all_names.sort()

        i = len(l)

        for name in all_names:
            if not d.has_key(name):
                d[name] = i
                l.append(name)
                i += 1

    def populate_constants(self):

        """
        Obtain a collection of distinct constant literals, building a mapping
        from constant references to those in this collection.
        """

        # Obtain mappings from constant values to identifiers.

        self.constants = {}

        # Establish a mapping from local constant identifiers to consolidated
        # constant identifiers.

        self.constant_numbers = {}

        for name, constant in self.importer.all_constant_values.items():

            # Each constant is actually (value, value_type, encoding).

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
    providing a mapping from object references to attribute names.

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

    for ref, attrnames in d.items():
        objkind = ref.get_kind()

        for attrname in attrnames:

            # Record each type supporting the attribute.

            init_item(attrs, attrname, set)
            attrs[attrname].add(ref)

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

    all_refs = d.keys()

    rsizes = []
    for attrname, size in sizes.items():
        priority = "<instance>" in objkinds[attrname] and 0.5 or 1
        occupied = len(attrs[attrname])
        key = (priority * size, size, len(all_refs) - occupied, attrname)
        rsizes.append(key)

    rsizes.sort()

    # Make a matrix of attributes.

    matrix = {}
    for attrname, refs in attrs.items():

        # Traverse the object types, adding the attribute name if the object
        # type supports the attribute, adding None otherwise.

        row = []
        for ref in all_refs:
            if ref in refs:
                row.append(attrname)
            else:
                row.append(None)
        matrix[attrname] = row

    return matrix, all_refs, rsizes

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
