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
        all_attrnames.append(t)
    return ", ".join(all_attrnames) or "{}"

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

    assignment = t
    return assignment and "A" or "_"

def decode_modifier_term(s):

    "Decode modifier term 's' representing assignment status."

    return s == "A"



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



# Output program encoding.

def encode_function_pointer(path):

    "Encode 'path' as a reference to an output program function."

    return "__fn_%s" % encode_path(path)

def encode_instantiator_pointer(path):

    "Encode 'path' as a reference to an output program instantiator."

    return "__new_%s" % encode_path(path)

def encode_path(path):

    "Encode 'path' as an output program object, translating special symbols."

    if path in reserved_words:
        return "__%s" % path
    else:
        return path.replace("#", "__").replace("$", "__").replace(".", "_")

def encode_symbol(symbol_type, path=None):

    "Encode a symbol with the given 'symbol_type' and optional 'path'."

    return "__%s%s" % (symbol_type, path and "_%s" % encode_path(path) or "")



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
