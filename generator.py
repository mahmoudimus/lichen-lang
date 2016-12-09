#!/usr/bin/env python

"""
Generate C code from object layouts and other deduced information.

Copyright (C) 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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

from common import CommonOutput
from encoders import encode_bound_reference, encode_function_pointer, \
                     encode_instantiator_pointer, \
                     encode_literal_constant, encode_literal_constant_member, \
                     encode_literal_constant_value, \
                     encode_literal_data_initialiser, \
                     encode_literal_instantiator, encode_literal_reference, \
                     encode_path, \
                     encode_predefined_reference, encode_size, \
                     encode_symbol, encode_tablename, \
                     encode_type_attribute, decode_type_attribute, \
                     is_type_attribute
from os import listdir, mkdir
from os.path import exists, isdir, join, split
from referencing import Reference

def copy(source, target):

    "Copy a text file from 'source' to 'target'."

    if isdir(target):
        target = join(target, split(source)[-1])
    infile = open(source)
    outfile = open(target, "w")
    try:
        outfile.write(infile.read())
    finally:
        outfile.close()
        infile.close()

class Generator(CommonOutput):

    "A code generator."

    # NOTE: These must be synchronised with the library.

    function_type = "__builtins__.core.function"
    string_type = "__builtins__.str.string"
    type_type = "__builtins__.core.type"

    predefined_constant_members = (
        ("__builtins__.boolean", "False"),
        ("__builtins__.boolean", "True"),
        ("__builtins__.none", "None"),
        ("__builtins__.notimplemented", "NotImplemented"),
        )

    literal_mapping_types = (
        "__builtins__.dict.dict",
        )

    literal_sequence_types = (
        "__builtins__.list.list",
        "__builtins__.tuple.tuple",
        )

    literal_instantiator_types = literal_mapping_types + literal_sequence_types

    def __init__(self, importer, optimiser, output):

        """
        Initialise the generator with the given 'importer', 'optimiser' and
        'output' directory.
        """

        self.importer = importer
        self.optimiser = optimiser
        self.output = output

    def to_output(self, debug=False):

        "Write the generated code."

        self.check_output()
        self.write_structures()
        self.copy_templates(debug)

    def copy_templates(self, debug=False):

        "Copy template files to the generated output directory."

        templates = join(split(__file__)[0], "templates")

        for filename in listdir(templates):
            target = self.output

            # Handle debug resources.

            if filename.endswith("-debug"):
                if debug:
                    target = join(self.output, filename[:-len("-debug")])
                else:
                    continue

            # Handle non-debug resources.

            if debug and exists(join(templates, "%s-debug" % filename)):
                continue

            pathname = join(templates, filename)

            # Copy files into the target directory.

            if not isdir(pathname):
                copy(pathname, target)

            # Copy directories (such as the native code directory).

            else:
                target = join(self.output, filename)

                if not exists(target):
                    mkdir(target)

                for filename in listdir(pathname):
                    copy(join(pathname, filename), target)

    def write_structures(self):

        "Write structures used by the program."

        f_consts = open(join(self.output, "progconsts.h"), "w")
        f_defs = open(join(self.output, "progtypes.c"), "w")
        f_decls = open(join(self.output, "progtypes.h"), "w")
        f_signatures = open(join(self.output, "main.h"), "w")
        f_code = open(join(self.output, "main.c"), "w")

        try:
            # Output boilerplate.

            print >>f_consts, """\
#ifndef __PROGCONSTS_H__
#define __PROGCONSTS_H__
"""
            print >>f_decls, """\
#ifndef __PROGTYPES_H__
#define __PROGTYPES_H__

#include "progconsts.h"
#include "types.h"
"""
            print >>f_defs, """\
#include "progtypes.h"
#include "progops.h"
#include "main.h"
"""
            print >>f_signatures, """\
#ifndef __MAIN_H__
#define __MAIN_H__

#include "types.h"
"""
            print >>f_code, """\
#include <string.h>
#include <stdio.h>
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progtypes.h"
#include "progops.h"
#include "main.h"
"""

            # Generate table and structure data.

            function_instance_attrs = None
            objects = self.optimiser.attr_table.items()
            objects.sort()

            self.callables = {}

            for ref, indexes in objects:
                attrnames = self.get_attribute_names(indexes)

                kind = ref.get_kind()
                path = ref.get_origin()
                table_name = encode_tablename(kind, path)
                structure_size = encode_size(kind, path)

                # Generate structures for classes and modules.

                if kind != "<instance>":
                    structure = []
                    attrs = self.get_static_attributes(kind, path, attrnames)

                    # Set a special instantiator on the class.

                    if kind == "<class>":

                        # Write instantiator declarations based on the
                        # applicable initialiser.

                        init_ref = attrs["__init__"]

                        # Write instantiator definitions.

                        self.write_instantiator(f_code, f_signatures, path, init_ref)

                        # Record the callable for parameter table generation.

                        self.callables[path] = init_ref.get_origin()

                        # Define special attributes.

                        signature = self.get_signature_for_callable(path)
                        attrs["__fn__"] = path
                        attrs["__args__"] = encode_size("pmin", signature)

                    self.populate_structure(Reference(kind, path), attrs, kind, structure)

                    if kind == "<class>":
                        self.write_instance_structure(f_decls, path, structure_size)

                    self.write_structure(f_decls, f_defs, path, table_name, structure,
                        kind == "<class>" and path)

                # Record function instance details for function generation below.

                else:
                    attrs = self.get_instance_attributes(path, attrnames)
                    if path == self.function_type:
                        function_instance_attrs = attrs

                        # Record the callable for parameter table generation.

                        self.callables[path] = path

                # Write a table for all objects.

                table = []
                self.populate_table(Reference(kind, path), table)
                self.write_table(f_decls, f_defs, table_name, structure_size, table)

            # Generate function instances.

            functions = self.importer.function_parameters.keys()
            functions.sort()
            extra_function_instances = []

            for path in functions:

                # Instantiators are generated above.

                if self.importer.classes.has_key(path) or not self.importer.get_object(path):
                    continue

                # Record the callable for parameter table generation.

                self.callables[path] = path

                # Define the structure details.

                cls = self.function_type
                table_name = encode_tablename("<instance>", cls)
                structure_size = encode_size("<instance>", path)

                # Set a special callable attribute on the instance.

                signature = self.get_signature_for_callable(path)
                function_instance_attrs["__fn__"] = path
                function_instance_attrs["__args__"] = encode_size("pmin", signature)

                # Produce two structures where a method is involved.

                parent, name = path.rsplit(".", 1)
                parent_ref = self.importer.get_object(parent)
                parent_kind = parent_ref and parent_ref.get_kind()

                # Populate and write each structure.

                if parent_kind == "<class>":

                    # A bound version of a method.

                    structure = self.populate_function(path, function_instance_attrs, False)
                    self.write_structure(f_decls, f_defs, encode_bound_reference(path), table_name, structure)

                    # An unbound version of a method.

                    structure = self.populate_function(path, function_instance_attrs, True)
                    self.write_structure(f_decls, f_defs, path, table_name, structure)

                else:
                    # A normal function.

                    structure = self.populate_function(path, function_instance_attrs, False)
                    self.write_structure(f_decls, f_defs, path, table_name, structure)

                # Functions with defaults need to declare instance structures.

                if self.importer.function_defaults.get(path):
                    self.write_instance_structure(f_decls, path, structure_size)
                    extra_function_instances.append(path)

                # Write function declarations.
                # Signature: __attr <name>(__attr[]);

                print >>f_signatures, "__attr %s(__attr args[]);" % encode_function_pointer(path)

            # Consolidate parameter tables for instantiators and functions.

            parameter_tables = set()

            for path, function_path in self.callables.items():
                parameters = self.optimiser.parameters[function_path]
                if not parameters:
                    parameters = ()
                else:
                    parameters = tuple(parameters)
                parameter_tables.add(parameters)

            # Generate parameter tables for distinct function signatures.

            for parameters in parameter_tables:
                self.make_parameter_table(f_decls, f_defs, parameters)

            # Generate predefined constants.

            for path, name in self.predefined_constant_members:
                self.make_predefined_constant(f_decls, f_defs, path, name)

            # Generate literal constants.

            for value, n in self.optimiser.constants.items():
                self.make_literal_constant(f_decls, f_defs, n, value)

            # Finish the main source file.

            self.write_main_program(f_code, f_signatures)

            # Record size information for certain function instances as well as
            # for classes, modules and other instances.

            size_tables = {}

            for kind in ["<class>", "<module>", "<instance>"]:
                size_tables[kind] = {}

            # Generate structure size data.

            for ref, structure in self.optimiser.structures.items():
                size_tables[ref.get_kind()][ref.get_origin()] = len(structure)

            for path in extra_function_instances:
                defaults = self.importer.function_defaults[path]
                size_tables["<instance>"][path] = size_tables["<instance>"][self.function_type] + len(defaults)

            size_tables = size_tables.items()
            size_tables.sort()

            for kind, sizes in size_tables:
                self.write_size_constants(f_consts, kind, sizes, 0)

            # Generate parameter table size data.

            min_sizes = {}
            max_sizes = {}

            for path, parameters in self.optimiser.parameters.items():
                argmin, argmax = self.get_argument_limits(path)

                # Use the parameter signature in the constant names.

                signature = self.get_parameter_signature(parameters)
                min_sizes[signature] = argmin
                max_sizes[signature] = argmax

                # Record instantiator limits.

                if path.endswith(".__init__"):
                    path = path[:-len(".__init__")]

            self.write_size_constants(f_consts, "pmin", min_sizes, 0)
            self.write_size_constants(f_consts, "pmax", max_sizes, 0)

            # Generate parameter codes.

            self.write_code_constants(f_consts, self.optimiser.all_paramnames, self.optimiser.arg_locations, "pcode", "ppos")

            # Generate attribute codes.

            self.write_code_constants(f_consts, self.optimiser.all_attrnames, self.optimiser.locations, "code", "pos")

            # Output more boilerplate.

            print >>f_consts, """\

#endif /* __PROGCONSTS_H__ */"""

            print >>f_decls, """\

#define __FUNCTION_TYPE %s
#define __FUNCTION_INSTANCE_SIZE %s
#define __TYPE_CLASS_TYPE %s
#define __TYPE_CLASS_POS %s
#define __TYPE_CLASS_CODE %s

#endif /* __PROGTYPES_H__ */""" % (
    encode_path(self.function_type),
    encode_size("<instance>", self.function_type),
    encode_path(self.type_type),
    encode_symbol("pos", encode_type_attribute(self.type_type)),
    encode_symbol("code", encode_type_attribute(self.type_type)),
    )

            print >>f_signatures, """\

#endif /* __MAIN_H__ */"""

        finally:
            f_consts.close()
            f_defs.close()
            f_decls.close()
            f_signatures.close()
            f_code.close()

    def make_literal_constant(self, f_decls, f_defs, n, value):

        """
        Write literal constant details to 'f_decls' (to declare a structure) and
        to 'f_defs' (to define the contents) for the constant with the number
        'n' with the given literal 'value'.
        """

        const_path = encode_literal_constant(n)
        structure_name = encode_literal_reference(n)

        # NOTE: This makes assumptions about the __builtins__ structure.

        modname = value.__class__.__name__
        typename = modname == "str" and "string" or modname
        ref = Reference("<instance>", "__builtins__.%s.%s" % (modname, typename))

        self.make_constant(f_decls, f_defs, ref, const_path, structure_name, value)

    def make_predefined_constant(self, f_decls, f_defs, path, name):

        """
        Write predefined constant details to 'f_decls' (to declare a structure)
        and to 'f_defs' (to define the contents) for the constant located in
        'path' with the given 'name'.
        """

        # Determine the details of the constant.

        attr_path = "%s.%s" % (path, name)
        structure_name = encode_predefined_reference(attr_path)
        ref = self.importer.get_object(attr_path)

        self.make_constant(f_decls, f_defs, ref, attr_path, structure_name)

    def make_constant(self, f_decls, f_defs, ref, const_path, structure_name, data=None):

        """
        Write constant details to 'f_decls' (to declare a structure) and to
        'f_defs' (to define the contents) for the constant described by 'ref'
        having the given 'path' and 'structure_name' (for the constant structure
        itself).
        """

        # Obtain the attributes.

        cls = ref.get_origin()
        indexes = self.optimiser.attr_table[ref]
        attrnames = self.get_attribute_names(indexes)
        attrs = self.get_instance_attributes(cls, attrnames)

        # Set the data, if provided.

        if data is not None:
            attrs["__data__"] = data

            # Also set a key for dynamic attribute lookup, if a string.

            if cls == self.string_type:
                if data in self.optimiser.all_attrnames:
                    attrs["__key__"] = data
                else:
                    attrs["__key__"] = None

        # Define the structure details. An object is created for the constant,
        # but an attribute is provided, referring to the object, for access to
        # the constant in the program.

        structure = []
        table_name = encode_tablename("<instance>", cls)
        self.populate_structure(ref, attrs, ref.get_kind(), structure)
        self.write_structure(f_decls, f_defs, structure_name, table_name, structure)

        # Define a macro for the constant.

        attr_name = encode_path(const_path)
        print >>f_decls, "#define %s ((__attr) {&%s, &%s})" % (attr_name, structure_name, structure_name)

    def make_parameter_table(self, f_decls, f_defs, parameters):

        """
        Write parameter table details to 'f_decls' (to declare a table) and to
        'f_defs' (to define the contents) for the given 'parameters'.
        """

        # Use a signature for the table name instead of a separate name for each
        # function.

        signature = self.get_parameter_signature(parameters)
        table_name = encode_tablename("<function>", signature)
        structure_size = encode_size("pmax", signature)

        table = []
        self.populate_parameter_table(parameters, table)
        self.write_parameter_table(f_decls, f_defs, table_name, structure_size, table)

    def get_parameter_signature(self, parameters):

        "Return a signature for the given 'parameters'."

        l = []
        for parameter in parameters:
            if parameter is None:
                l.append("")
            else:
                name, pos = parameter
                l.append("%s_%s" % (name, pos))
        return l and "__".join(l) or "__void"

    def get_signature_for_callable(self, path):

        "Return the signature for the callable with the given 'path'."

        function_path = self.callables[path]
        parameters = self.optimiser.parameters[function_path]
        return self.get_parameter_signature(parameters)

    def write_size_constants(self, f_consts, size_prefix, sizes, padding):

        """
        Write size constants to 'f_consts' for the given 'size_prefix', using
        the 'sizes' dictionary to populate the definition, adding the given
        'padding' to the basic sizes.
        """

        print >>f_consts, "enum %s {" % encode_size(size_prefix)
        first = True
        for path, size in sizes.items():
            if not first:
                print >>f_consts, ","
            else:
                first = False
            f_consts.write("    %s = %d" % (encode_size(size_prefix, path), size + padding))
        print >>f_consts, "\n    };"

    def write_code_constants(self, f_consts, attrnames, locations, code_prefix, pos_prefix):

        """
        Write code constants to 'f_consts' for the given 'attrnames' and
        attribute 'locations'.
        """

        print >>f_consts, "enum %s {" % encode_symbol(code_prefix)
        first = True
        for i, attrname in enumerate(attrnames):
            if not first:
                print >>f_consts, ","
            else:
                first = False
            f_consts.write("    %s = %d" % (encode_symbol(code_prefix, attrname), i))
        print >>f_consts, "\n    };"

        print >>f_consts, "enum %s {" % encode_symbol(pos_prefix)
        first = True
        for i, attrnames in enumerate(locations):
            for attrname in attrnames:
                if not first:
                    print >>f_consts, ","
                else:
                    first = False
                f_consts.write("    %s = %d" % (encode_symbol(pos_prefix, attrname), i))
        print >>f_consts, "\n    };"

    def write_table(self, f_decls, f_defs, table_name, structure_size, table):

        """
        Write the declarations to 'f_decls' and definitions to 'f_defs' for
        the object having the given 'table_name' and the given 'structure_size',
        with 'table' details used to populate the definition.
        """

        print >>f_decls, "extern const __table %s;\n" % table_name

        # Write the corresponding definition.

        print >>f_defs, "const __table %s = {\n    %s,\n    {\n        %s\n        }\n    };\n" % (
            table_name, structure_size,
            ",\n        ".join(table))

    def write_parameter_table(self, f_decls, f_defs, table_name, structure_size, table):

        """
        Write the declarations to 'f_decls' and definitions to 'f_defs' for
        the object having the given 'table_name' and the given 'structure_size',
        with 'table' details used to populate the definition.
        """

        print >>f_decls, "extern const __ptable %s;\n" % table_name

        # Write the corresponding definition.

        print >>f_defs, "const __ptable %s = {\n    %s,\n    {\n        %s\n        }\n    };\n" % (
            table_name, structure_size,
            ",\n        ".join([("{%s, %s}" % t) for t in table]))

    def write_instance_structure(self, f_decls, path, structure_size):

        """
        Write a declaration to 'f_decls' for the object having the given 'path'
        and the given 'structure_size'.
        """

        # Write an instance-specific type definition for instances of classes.
        # See: templates/types.h

        print >>f_decls, """\
typedef struct {
    const __table * table;
    unsigned int pos;
    __attr attrs[%s];
} %s;
""" % (structure_size, encode_symbol("obj", path))

    def write_structure(self, f_decls, f_defs, structure_name, table_name, structure, path=None):

        """
        Write the declarations to 'f_decls' and definitions to 'f_defs' for
        the object having the given 'structure_name', the given 'table_name',
        and the given 'structure' details used to populate the definition.
        """

        if f_decls:
            print >>f_decls, "extern __obj %s;\n" % encode_path(structure_name)

        is_class = path and self.importer.get_object(path).has_kind("<class>")
        pos = is_class and encode_symbol("pos", encode_type_attribute(path)) or "0"

        print >>f_defs, """\
__obj %s = {
    &%s,
    %s,
    {
        %s
    }};
""" % (
            encode_path(structure_name), table_name, pos,
            ",\n        ".join(structure))

    def get_argument_limits(self, path):

        """
        Return the argument minimum and maximum for the callable at 'path',
        adding an argument position for a universal context.
        """

        parameters = self.importer.function_parameters[path]
        defaults = self.importer.function_defaults.get(path)
        num_parameters = len(parameters) + 1
        return num_parameters - (defaults and len(defaults) or 0), num_parameters

    def get_attribute_names(self, indexes):

        """
        Given a list of attribute table 'indexes', return a list of attribute
        names.
        """

        all_attrnames = self.optimiser.all_attrnames
        attrnames = []
        for i in indexes:
            if i is None:
                attrnames.append(None)
            else:
                attrnames.append(all_attrnames[i])
        return attrnames

    def get_static_attributes(self, kind, name, attrnames):

        """
        Return a mapping of attribute names to paths for attributes belonging
        to objects of the given 'kind' (being "<class>" or "<module>") with
        the given 'name' and supporting the given 'attrnames'.
        """

        attrs = {}

        for attrname in attrnames:
            if attrname is None:
                continue
            if kind == "<class>":
                path = self.importer.all_class_attrs[name][attrname]
            elif kind == "<module>":
                path = "%s.%s" % (name, attrname)
            else:
                continue

            # The module may be hidden.

            attr = self.importer.get_object(path)
            if not attr:
                module = self.importer.hidden.get(path)
                if module:
                    attr = Reference(module.name, "<module>")
            attrs[attrname] = attr

        return attrs

    def get_instance_attributes(self, name, attrnames):

        """
        Return a mapping of attribute names to references for attributes
        belonging to instances of the class with the given 'name', where the
        given 'attrnames' are supported.
        """

        consts = self.importer.all_instance_attr_constants[name]
        attrs = {}
        for attrname in attrnames:
            if attrname is None:
                continue
            const = consts.get(attrname)
            attrs[attrname] = const or Reference("<var>", "%s.%s" % (name, attrname))
        return attrs

    def populate_table(self, path, table):

        """
        Traverse the attributes in the determined order for the structure having
        the given 'path', adding entries to the attribute 'table'.
        """

        for attrname in self.optimiser.structures[path]:

            # Handle gaps in the structure.

            if attrname is None:
                table.append("0")
            else:
                table.append(encode_symbol("code", attrname))

    def populate_parameter_table(self, parameters, table):

        """
        Traverse the 'parameters' in the determined order, adding entries to the
        attribute 'table'.
        """

        for value in parameters:

            # Handle gaps in the structure.

            if value is None:
                table.append(("0", "0"))
            else:
                name, pos = value
                table.append((encode_symbol("pcode", name), pos))

    def populate_function(self, path, function_instance_attrs, unbound=False):

        """
        Populate a structure for the function with the given 'path'. The given
        'attrs' provide the instance attributes, and if 'unbound' is set to a
        true value, an unbound method structure is produced (as opposed to a
        callable bound method structure).
        """

        structure = []
        self.populate_structure(Reference("<function>", path), function_instance_attrs, "<instance>", structure, unbound)

        # Append default members.

        self.append_defaults(path, structure)
        return structure

    def populate_structure(self, ref, attrs, kind, structure, unbound=False):

        """
        Traverse the attributes in the determined order for the structure having
        the given 'ref' whose members are provided by the 'attrs' mapping, in a
        structure of the given 'kind', adding entries to the object 'structure'.
        If 'unbound' is set to a true value, an unbound method function pointer
        will be employed, with a reference to the bound method incorporated into
        the special __fn__ attribute.
        """

        # Populate function instance structures for functions.

        if ref.has_kind("<function>"):
            origin = self.function_type
            structure_ref = Reference("<instance>", self.function_type)

        # Otherwise, just populate the appropriate structures.

        else:
            origin = ref.get_origin()
            structure_ref = ref

        for attrname in self.optimiser.structures[structure_ref]:

            # Handle gaps in the structure.

            if attrname is None:
                structure.append("{0, 0}")

            # Handle non-constant and constant members.

            else:
                attr = attrs[attrname]

                # Special function pointer member.

                if attrname == "__fn__":

                    # Provide bound method references and the unbound function
                    # pointer if populating methods in a class.

                    bound_attr = None

                    # Classes offer instantiators.

                    if kind == "<class>":
                        attr = encode_instantiator_pointer(attr)

                    # Methods offers references to bound versions and an unbound
                    # method function.

                    elif unbound:
                        bound_attr = encode_bound_reference(attr)
                        attr = "__unbound_method"

                    # Other functions just offer function pointers.

                    else:
                        attr = encode_function_pointer(attr)

                    structure.append("{%s, .fn=%s}" % (bound_attr and ".b=&%s" % bound_attr or "0", attr))
                    continue

                # Special argument specification member.

                elif attrname == "__args__":
                    signature = self.get_signature_for_callable(ref.get_origin())
                    ptable = encode_tablename("<function>", signature)

                    structure.append("{.min=%s, .ptable=&%s}" % (attr, ptable))
                    continue

                # Special internal data member.

                elif attrname == "__data__":
                    structure.append("{0, .%s=%s}" % (encode_literal_constant_member(attr),
                                                      encode_literal_constant_value(attr)))
                    continue

                # Special internal key member.

                elif attrname == "__key__":
                    structure.append("{.code=%s, .pos=%s}" % (attr and encode_symbol("code", attr) or "0",
                                                              attr and encode_symbol("pos", attr) or "0"))
                    continue

                # Special cases.

                elif attrname in ("__file__", "__fname__",  "__mname__", "__name__"):
                    path = ref.get_origin()

                    if attrname == "__file__":
                        module = self.importer.get_module(path)
                        value = module.filename
                    else:
                        value = path

                    local_number = self.importer.all_constants[path][value]
                    constant_name = "$c%d" % local_number
                    attr_path = "%s.%s" % (path, constant_name)
                    constant_number = self.optimiser.constant_numbers[attr_path]
                    constant_value = "__const%d" % constant_number
                    structure.append("%s /* %s */" % (constant_value, attrname))
                    continue

                # Special class relationship attributes.

                elif is_type_attribute(attrname):
                    structure.append("{0, &%s}" % encode_path(decode_type_attribute(attrname)))
                    continue

                structure.append(self.encode_member(origin, attrname, attr, kind))

    def encode_member(self, path, name, ref, structure_type):

        """
        Encode within the structure provided by 'path', the member whose 'name'
        provides 'ref', within the given 'structure_type'.
        """

        kind = ref.get_kind()
        origin = ref.get_origin()

        # References to constant literals.

        if kind == "<instance>" and ref.is_constant_alias():
            alias = ref.get_name()

            # Obtain a constant value directly assigned to the attribute.

            if self.optimiser.constant_numbers.has_key(alias):
                constant_number = self.optimiser.constant_numbers[alias]
                constant_value = "__const%d" % constant_number
                return "%s /* %s */" % (constant_value, name)

        # Predefined constant references.

        if (path, name) in self.predefined_constant_members:
            attr_path = encode_predefined_reference("%s.%s" % (path, name))
            return "{&%s, &%s} /* %s */" % (attr_path, attr_path, name)

        # General undetermined members.

        if kind in ("<var>", "<instance>"):
            return "{0, 0} /* %s */" % name

        # Set the context depending on the kind of attribute.
        # For methods:          {&<parent>, &<attr>}
        # For other attributes: {&<attr>, &<attr>}

        else:
            if kind == "<function>" and structure_type == "<class>":
                parent = origin.rsplit(".", 1)[0]
                context = "&%s" % encode_path(parent)
            elif kind == "<instance>":
                context = "&%s" % encode_path(origin)
            else:
                context = "0"
            return "{%s, &%s}" % (context, encode_path(origin))

    def append_defaults(self, path, structure):

        """
        For the given 'path', append default parameter members to the given
        'structure'.
        """

        for name, default in self.importer.function_defaults.get(path):
            structure.append(self.encode_member(path, name, default, "<instance>"))

    def write_instantiator(self, f_code, f_signatures, path, init_ref):

        """
        Write an instantiator to 'f_code', with a signature to 'f_signatures',
        for instances of the class with the given 'path', with 'init_ref' as the
        initialiser function reference.

        NOTE: This also needs to initialise any __fn__ and __args__ members
        NOTE: where __call__ is provided by the class.
        """

        parameters = self.importer.function_parameters[init_ref.get_origin()]

        print >>f_code, """\
__attr %s(__attr __args[])
{
    /* Allocate the structure. */
    __args[0] = __new(&%s, &%s, sizeof(%s));

    /* Call the initialiser. */
    %s(__args);

    /* Return the allocated object details. */
    return __args[0];
}
""" % (
    encode_instantiator_pointer(path),
    encode_tablename("<instance>", path),
    encode_path(path),
    encode_symbol("obj", path),
    encode_function_pointer(init_ref.get_origin())
    )

        print >>f_signatures, "#define __HAVE_%s" % encode_path(path)
        print >>f_signatures, "__attr %s(__attr[]);" % encode_instantiator_pointer(path)

        # Write additional literal instantiators. These do not call the
        # initialisers but instead populate the structures directly.

        if path in self.literal_instantiator_types:
            if path in self.literal_mapping_types:
                style = "mapping"
            else:
                style = "sequence"

            print >>f_code, """\
__attr %s(__attr __args[], unsigned int number)
{
    /* Allocate the structure. */
    __args[0] = __new(&%s, &%s, sizeof(%s));

    /* Allocate a structure for the data and set it on the __data__ attribute. */
    %s(__args, number);

    /* Return the allocated object details. */
    return __args[0];
}
""" % (
    encode_literal_instantiator(path),
    encode_tablename("<instance>", path),
    encode_path(path),
    encode_symbol("obj", path),
    encode_literal_data_initialiser(style)
    )

            print >>f_signatures, "__attr %s(__attr[], unsigned int);" % encode_literal_instantiator(path)

    def write_main_program(self, f_code, f_signatures):

        """
        Write the main program to 'f_code', invoking the program's modules. Also
        write declarations for module main functions to 'f_signatures'.
        """

        print >>f_code, """\
int main(int argc, char *argv[])
{
    __exc __tmp_exc;

    __Try
    {"""

        for name in self.importer.order_modules():
            function_name = "__main_%s" % encode_path(name)
            print >>f_signatures, "void %s();" % function_name

            # Omit the native modules.

            parts = name.split(".")

            if parts[0] != "native":
                print >>f_code, """\
        %s();""" % function_name

        print >>f_code, """\
        return 0;
    }
    __Catch(__tmp_exc)
    {
        fprintf(stderr, "Program terminated due to exception: %%s.\\n",
                __load_via_object(
                    %s((__attr[]) {{0, 0}, __tmp_exc.arg}).value,
                    %s).strvalue);
        return 1;
    }
}
""" % (
    encode_function_pointer("__builtins__.str.str"),
    encode_symbol("pos", "__data__")
    )

# vim: tabstop=4 expandtab shiftwidth=4
