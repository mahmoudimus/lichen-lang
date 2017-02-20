#!/usr/bin/env python

"""
Encoder functions, producing representations of program objects.

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

from common import first, InstructionSequence



# Value digest computation.

from base64 import b64encode
from hashlib import sha1

def digest(values):
    m = sha1()
    for value in values:
        m.update(str(value))
    return b64encode(m.digest()).replace("+", "__").replace("/", "_").rstrip("=")



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

    "Encode assignment and invocation details from 'modifiers'."

    all_modifiers = []
    for t in modifiers:
        all_modifiers.append(encode_modifier_term(t))
    return "".join(all_modifiers)

def encode_modifier_term(t):

    "Encode modifier 't' representing an assignment or an invocation."

    assignment, invocation = t
    if assignment:
        return "="
    elif invocation is not None:
        arguments, keywords = invocation
        return "(%d;%s)" % (arguments, ",".join(keywords))
    else:
        return "_"

def decode_modifiers(s):

    "Decode 's' containing modifiers."

    i = 0
    end = len(s)

    modifiers = []

    while i < end:
        if s[i] == "=":
            modifiers.append((True, None))
            i += 1
        elif s[i] == "(":
            j = s.index(";", i)
            arguments = int(s[i+1:j])
            i = j
            j = s.index(")", i)
            keywords = s[i+1:j]
            keywords = keywords and keywords.split(",") or []
            modifiers.append((False, (arguments, keywords)))
            i = j + 1
        else:
            modifiers.append((False, None))
            i += 1

    return modifiers



# Test generation functions.

def get_kinds(all_types):

    """ 
    Return object kind details for 'all_types', being a collection of
    references for program types.
    """

    return map(lambda ref: ref.get_kind(), all_types)

def test_label_for_kind(kind):

    "Return the label used for 'kind' in test details."

    return kind == "<instance>" and "instance" or "type"

def test_label_for_type(ref):

    "Return the label used for 'ref' in test details."

    return test_label_for_kind(ref.get_kind())



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

type_ops = (
    "__test_specific_instance", "__test_specific_object", "__test_specific_type",
    )

static_ops = (
    "__load_static_ignore", "__load_static_replace", "__load_static_test", "<test_context_static>",
    )

context_values = (
    "<context>",
    )

context_ops = (
    "<context>", "<set_context>", "<test_context_revert>", "<test_context_static>",
    )

context_op_functions = (
    "<test_context_revert>", "<test_context_static>",
    )

reference_acting_ops = attribute_ops + checked_ops + typename_ops
attribute_producing_ops = attribute_loading_ops + checked_loading_ops

def encode_access_instruction(instruction, subs, context_index):

    """
    Encode the 'instruction' - a sequence starting with an operation and
    followed by arguments, each of which may be an instruction sequence or a
    plain value - to produce a function call string representation.

    The 'subs' parameter defines a mapping of substitutions for special values
    used in instructions.

    The 'context_index' parameter defines the position in local context storage
    for the referenced context or affected by a context operation.

    Return both the encoded instruction and a collection of substituted names.
    """

    op = instruction[0]
    args = instruction[1:]
    substituted = set()

    # Encode the arguments.

    a = []
    if args:
        converting_op = op
        for arg in args:
            s, _substituted = encode_access_instruction_arg(arg, subs, converting_op, context_index)
            substituted.update(_substituted)
            a.append(s)
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
        arg = encode_type_attribute(args[1])
        a[1] = encode_symbol("pos", arg)
        a.insert(2, encode_symbol("code", arg))

    # Obtain addresses of type arguments.

    elif op in type_ops:
        a[1] = "&%s" % a[1]

    # Obtain addresses of static objects.

    elif op in static_ops:
        a[-1] = "&%s" % a[-1]

    # Add context storage information to certain operations.

    if op in context_ops:
        a.insert(0, context_index)

    # Add the local context array to certain operations.

    if op in context_op_functions:
        a.append("__tmp_contexts")

    # Define any argument string.

    if a:
        argstr = "(%s)" % ", ".join(map(str, a))
    else:
        argstr = ""

    # Substitute the first element of the instruction, which may not be an
    # operation at all.

    if subs.has_key(op):
        substituted.add(op)

        # Break accessor initialisation into initialisation and value-yielding
        # parts:

        if op == "<set_accessor>" and isinstance(a[0], InstructionSequence):
            ops = []
            ops += a[0].get_init_instructions()
            ops.append("%s(%s)" % (subs[op], a[0].get_value_instruction()))
            return ", ".join(map(str, ops)), substituted

        op = subs[op]

    elif not args:
        op = "&%s" % encode_path(op)

    return "%s%s" % (op, argstr), substituted

def encode_access_instruction_arg(arg, subs, op, context_index):

    """
    Encode 'arg' using 'subs' to define substitutions, 'op' to indicate the
    operation to which the argument belongs, and 'context_index' to indicate any
    affected context storage.

    Return a tuple containing the encoded form of 'arg' along with a collection
    of any substituted values.
    """

    if isinstance(arg, tuple):
        encoded, substituted = encode_access_instruction(arg, subs, context_index)

        # Convert attribute results to references where required.

        if op and op in reference_acting_ops and arg[0] in attribute_producing_ops:
            return "%s.value" % encoded, substituted
        else:
            return encoded, substituted

    # Special values only need replacing, not encoding.

    elif subs.has_key(arg):

        # Handle values modified by storage details.

        if arg in context_values:
            return "%s(%s)" % (subs.get(arg), context_index), set([arg])
        else:
            return subs.get(arg), set([arg])

    # Convert static references to the appropriate type.

    elif op and op in reference_acting_ops and arg != "<accessor>":
        return "&%s" % encode_path(arg), set()

    # Other values may need encoding.

    else:
        return encode_path(arg), set()

def encode_function_pointer(path):

    "Encode 'path' as a reference to an output program function."

    return "__fn_%s" % encode_path(path)

def encode_instantiator_pointer(path):

    "Encode 'path' as a reference to an output program instantiator."

    return "__new_%s" % encode_path(path)

def encode_instructions(instructions):

    "Encode 'instructions' as a sequence."

    if len(instructions) == 1:
        return instructions[0]
    else:
        return "(\n%s\n)" % ",\n".join(instructions)

def encode_literal_constant(n):

    "Encode a name for the literal constant with the number 'n'."

    return "__const%s" % n

def encode_literal_constant_size(value):

    "Encode a size for the literal constant with the given 'value'."

    if isinstance(value, basestring):
        return len(value)
    else:
        return 0

def encode_literal_constant_member(value):

    "Encode the member name for the 'value' in the final program."

    return "%svalue" % value.__class__.__name__

def encode_literal_constant_value(value):

    "Encode the given 'value' in the final program."

    if isinstance(value, (int, float)):
        return str(value)
    else:
        l = []

        # Encode characters including non-ASCII ones.

        for c in str(value):
            if c == '"': l.append('\\"')
            elif c == '\n': l.append('\\n')
            elif c == '\t': l.append('\\t')
            elif c == '\r': l.append('\\r')
            elif c == '\\': l.append('\\\\')
            elif 0x20 <= ord(c) < 0x80: l.append(c)
            else: l.append("\\x%02x" % ord(c))

        return '"%s"' % "".join(l)

def encode_literal_data_initialiser(style):

    """
    Encode a reference to a function populating the data for a literal having
    the given 'style' ("mapping" or "sequence").
    """

    return "__newdata_%s" % style

def encode_literal_instantiator(path):

    """
    Encode a reference to an instantiator for a literal having the given 'path'.
    """

    return "__newliteral_%s" % encode_path(path)

def encode_literal_reference(n):

    "Encode a reference to a literal constant with the number 'n'."

    return "__constvalue%s" % n



# Track all encoded paths, detecting and avoiding conflicts.

all_encoded_paths = {}

def encode_path(path):

    "Encode 'path' as an output program object, translating special symbols."

    if path in reserved_words:
        return "__%s" % path
    else:
        part_encoded = path.replace("#", "__").replace("$", "__")

        if "." not in path:
            return part_encoded

        encoded = part_encoded.replace(".", "_")

        # Test for a conflict with the encoding of a different path, re-encoding
        # if necessary.

        previous = all_encoded_paths.get(encoded)
        replacement = "_"

        while previous:
            if path == previous:
                return encoded
            replacement += "_"
            encoded = part_encoded.replace(".", replacement)
            previous = all_encoded_paths.get(encoded)

        # Store any new or re-encoded path.

        all_encoded_paths[encoded] = path
        return encoded

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

def decode_type_attribute(s):

    "Decode the special type attribute 's'."

    return s[1:]

def is_type_attribute(s):

    "Return whether 's' is a type attribute name."

    return s.startswith("#")



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
