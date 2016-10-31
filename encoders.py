#!/usr/bin/env python

"""
Encoder functions, producing representations of program objects.

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

from common import first

# Output encoding and decoding for the summary files.

def encode_attrnames(attrnames):

    "Encode the 'attrnames' representing usage."

    return ", ".join(attrnames) or "{}"

def encode_constrained(constrained):

    "Encode the 'constrained' status for program summaries."

    return constrained and "constrained" or "deduced"

def encode_usage(usage):

    "Encode attribute details from 'usage'."

    all_attrnames = []
    for t in usage:
        attrname, invocation, assignment = t
        all_attrnames.append("%s%s" % (attrname, invocation and "!" or assignment and "=" or ""))
    return ", ".join(all_attrnames) or "{}"

def decode_usage(s):

    "Decode attribute details from 's'."

    all_attrnames = set()
    for attrname_str in s.split(", "):
        all_attrnames.add((attrname_str.rstrip("!="), attrname_str.endswith("!"), attrname_str.endswith("=")))

    all_attrnames = list(all_attrnames)
    all_attrnames.sort()
    return tuple(all_attrnames)

def encode_access_location(t):

    "Encode the access location 't'."

    path, name, attrname, version = t
    return "%s %s %s:%d" % (path, name or "{}", attrname, version)

def encode_location(t):

    "Encode the general location 't' in a concise form."

    path, name, attrname, version = t
    if name is not None and version is not None:
        return "%s %s:%d" % (path, name, version)
    elif name is not None:
        return "%s %s" % (path, name)
    else:
        return "%s :%s" % (path, attrname)

def encode_modifiers(modifiers):

    "Encode assignment details from 'modifiers'."

    all_modifiers = []
    for t in modifiers:
        all_modifiers.append(encode_modifier_term(t))
    return "".join(all_modifiers)

def encode_modifier_term(t):

    "Encode modifier 't' representing assignment status."

    assignment, invocation = t
    return assignment and "=" or invocation and "!" or "_"

def decode_modifier_term(s):

    "Decode modifier term 's' representing assignment status."

    return (s == "=", s == "!")



# Test generation functions.

def get_kinds(all_types):

    """ 
    Return object kind details for 'all_types', being a collection of
    references for program types.
    """

    return map(lambda ref: ref.get_kind(), all_types)

def test_for_kind(prefix, kind):

    "Return a test condition identifier featuring 'prefix' and 'kind'."

    return "%s-%s" % (prefix, kind == "<instance>" and "instance" or "type")

def test_for_kinds(prefix, all_kinds):

    """ 
    Return an identifier describing test conditions incorporating the given
    'prefix' and involving 'all_kinds', being a collection of object kinds.
    """

    return test_for_kind(prefix, first(all_kinds))

def test_for_type(prefix, ref):

    """ 
    Return an identifier describing a test condition incorporating the given
    'prefix' and involving 'ref', being a program type reference. The kind of
    the reference is employed in the identifier.
    """

    return test_for_kind(prefix, ref.get_kind())



# Instruction representation encoding.

def encode_instruction(instruction):

    """
    Encode the 'instruction' - a sequence starting with an operation and
    followed by arguments, each of which may be an instruction sequence or a
    plain value - to produce a function call string representation.
    """

    op = instruction[0]
    args = instruction[1:]

    if args:
        a = []
        for arg in args:
            if isinstance(arg, tuple):
                a.append(encode_instruction(arg))
            else:
                a.append(arg or "{}")
        argstr = "(%s)" % ", ".join(a)
        return "%s%s" % (op, argstr)
    else:
        return op



# Output program encoding.

attribute_loading_ops = (
    "__load_via_class", "__load_via_object", "__get_class_and_load",
    )

attribute_ops = attribute_loading_ops + (
    "__store_via_object",
    )

checked_loading_ops = (
    "__check_and_load_via_class", "__check_and_load_via_object", "__check_and_load_via_any",
    )

checked_ops = checked_loading_ops + (
    "__check_and_store_via_class", "__check_and_store_via_object", "__check_and_store_via_any",
    )

typename_ops = (
    "__test_common_instance", "__test_common_object", "__test_common_type",
    )

encoding_ops = (
    "__encode_callable",
    )

static_ops = (
    "__load_static",
    )

reference_acting_ops = attribute_ops + checked_ops + typename_ops
attribute_producing_ops = attribute_loading_ops + checked_loading_ops

def encode_access_instruction(instruction, subs):

    """
    Encode the 'instruction' - a sequence starting with an operation and
    followed by arguments, each of which may be an instruction sequence or a
    plain value - to produce a function call string representation.

    The 'subs' parameter defines a mapping of substitutions for special values
    used in instructions.
    """

    op = instruction[0]
    args = instruction[1:]

    if not args:
        argstr = ""

    else:
        # Encode the arguments.

        a = []
        converting_op = op
        for arg in args:
            a.append(encode_access_instruction_arg(arg, subs, converting_op))
            converting_op = None

        # Modify certain arguments.

        # Convert attribute name arguments to position symbols.

        if op in attribute_ops:
            arg = a[1]
            a[1] = encode_symbol("pos", arg)

        # Convert attribute name arguments to position and code symbols.

        elif op in checked_ops:
            arg = a[1]
            a[1] = encode_symbol("pos", arg)
            a.insert(2, encode_symbol("code", arg))

        # Convert type name arguments to position and code symbols.

        elif op in typename_ops:
            arg = encode_type_attribute(a[1])
            a[1] = encode_symbol("pos", arg)
            a.insert(2, encode_symbol("code", arg))

        # Replace encoded operations.

        elif op in encoding_ops:
            origin = a[0]
            kind = a[1]
            op = "__load_function"
            a = [kind == "<class>" and encode_instantiator_pointer(origin) or encode_function_pointer(origin)]

        # Obtain addresses of static objects.

        elif op in static_ops:
            a[0] = "&%s" % a[0]

        argstr = "(%s)" % ", ".join(a)

    # Substitute the first element of the instruction, which may not be an
    # operation at all.

    if subs.has_key(op):
        op = subs[op]
    elif not args:
        op = "&%s" % encode_path(op)

    return "%s%s" % (op, argstr)

def encode_access_instruction_arg(arg, subs, op):

    "Encode 'arg' using 'subs' to define substitutions."

    if isinstance(arg, tuple):
        encoded = encode_access_instruction(arg, subs)

        # Convert attribute results to references where required.

        if op and op in reference_acting_ops and arg[0] in attribute_producing_ops:
            return "%s.value" % encoded
        else:
            return encoded

    # Special values only need replacing, not encoding.

    elif subs.has_key(arg):
        return subs.get(arg)

    # Other values may need encoding.

    else:
        return encode_path(arg)

def encode_bound_reference(path):

    "Encode 'path' as a bound method name."

    return "__bound_%s" % encode_path(path)

def encode_function_pointer(path):

    "Encode 'path' as a reference to an output program function."

    return "__fn_%s" % encode_path(path)

def encode_initialiser_pointer(path):

    "Encode 'path' as a reference to an initialiser function structure."

    return encode_path("%s.__init__" % path)

def encode_instantiator_pointer(path):

    "Encode 'path' as a reference to an output program instantiator."

    return "__new_%s" % encode_path(path)

def encode_literal_constant(n):

    "Encode a name for the literal constant with the number 'n'."

    return "__const%d" % n

def encode_literal_constant_member(value):

    "Encode the member name for the 'value' in the final program."

    return "%svalue" % value.__class__.__name__

def encode_literal_constant_value(value):

    "Encode the given 'value' in the final program."

    if isinstance(value, (int, float)):
        return str(value)
    else:
        return '"%s"' % str(value).replace('"', '\\"')

def encode_literal_instantiator(path):

    """
    Encode a reference to an instantiator for a literal having the given 'path'.
    """

    return "__newliteral_%s" % encode_path(path)

def encode_literal_reference(n):

    "Encode a reference to a literal constant with the number 'n'."

    return "__constvalue%d" % n

def encode_path(path):

    "Encode 'path' as an output program object, translating special symbols."

    if path in reserved_words:
        return "__%s" % path
    else:
        return path.replace("#", "__").replace("$", "__").replace(".", "_")

def encode_predefined_reference(path):

    "Encode a reference to a predefined constant value for 'path'."

    return "__predefined_%s" % encode_path(path)

def encode_size(kind, path=None):

    """
    Encode a structure size reference for the given 'kind' of structure, with
    'path' indicating a specific structure name.
    """

    return "__%ssize%s" % (structure_size_prefixes.get(kind, kind), path and "_%s" % encode_path(path) or "")

def encode_symbol(symbol_type, path=None):

    "Encode a symbol with the given 'symbol_type' and optional 'path'."

    return "__%s%s" % (symbol_type, path and "_%s" % encode_path(path) or "")

def encode_tablename(kind, path):

    """
    Encode a table reference for the given 'kind' of table structure, indicating
    a 'path' for the specific object concerned.
    """

    return "__%sTable_%s" % (table_name_prefixes[kind], encode_path(path))

def encode_type_attribute(path):

    "Encode the special type attribute for 'path'."

    return "#%s" % path



# A mapping from kinds to structure size reference prefixes.

structure_size_prefixes = {
    "<class>" : "c",
    "<module>" : "m",
    "<instance>" : "i"
    }

# A mapping from kinds to table name prefixes.

table_name_prefixes = {
    "<class>" : "Class",
    "<function>" : "Function",
    "<module>" : "Module",
    "<instance>" : "Instance"
    }



# Output language reserved words.

reserved_words = [
    "break", "char", "const", "continue",
    "default", "double", "else",
    "float", "for",
    "if", "int", "long",
    "NULL",
    "return", "struct",
    "typedef",
    "void", "while",
    ]

# vim: tabstop=4 expandtab shiftwidth=4
