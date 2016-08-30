#!/usr/bin/env python

"""
Type objects.

Copyright (C) 2012, 2015 Paul Boddie <paul@boddie.org.uk>

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

# Built-in type duplication.

type = type
NoneType = NoneType
NotImplementedType = NotImplementedType

# Synonyms for built-in types.

BooleanType = bool
BufferType = buffer
BuiltinFunctionType = function
BuiltinMethodType = function
ComplexType = complex
DictType = dict
EllipsisType = ellipsis
FileType = file
FloatType = float
FunctionType = function
IntType = int
LambdaType = function
ListType = list
LongType = long
MethodType = function
ObjectType = object
SliceType = slice
StringType = str
TupleType = tuple
UnboundMethodType = function
UnicodeType = unicode
XRangeType = xrange

StringTypes = (StringType, UnicodeType)

# Types without special definitions.

ClassType = object
GeneratorType = object
InstanceType = object
ModuleType = object
TracebackType = object

# Implementation-specific definitions not relevant to micropython.

DictProxyType = object
FrameType = object
GetSetDescriptorType = object
MemberDescriptorType = object

# vim: tabstop=4 expandtab shiftwidth=4
