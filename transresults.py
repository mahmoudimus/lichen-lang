#!/usr/bin/env python

"""
Translation result abstractions.

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
from encoders import encode_instructions, encode_literal_constant, encode_path
from results import ConstantValueRef, InstanceRef, LiteralSequenceRef, NameRef, \
                    ResolvedNameRef, Result

# Classes representing intermediate translation results.

class ReturnRef:

    "Indicates usage of a return statement."

    pass

class Expression(Result):

    "A general expression."

    def __init__(self, s):
        if isinstance(s, Result):
            self.s = str(s)
            self.expr = s
        else:
            self.s = s
            self.expr = None

    def discards_temporary(self, test=True):

        """
        Return a list of temporary names that can be discarded if 'test' is
        specified as a true value (or omitted).
        """

        return self.expr and self.expr.discards_temporary(False)

    def __str__(self):
        return self.s

    def __repr__(self):
        return "Expression(%r)" % self.s

class TrResolvedNameRef(ResolvedNameRef):

    "A reference to a name in the translation."

    def __init__(self, name, ref, expr=None, is_global=False, parameter=None, location=None):
        ResolvedNameRef.__init__(self, name, ref, expr, is_global)
        self.parameter = parameter
        self.location = location

    def access_location(self):
        return self.location

    def __str__(self):

        "Return an output representation of the referenced name."

        # Temporary names are output program locals.

        if self.name.startswith("$t"):
            if self.expr:
                return "%s = %s" % (encode_path(self.name), self.expr)
            else:
                return encode_path(self.name)

        # For sources, any identified static origin will be constant and thus
        # usable directly. For targets, no constant should be assigned and thus
        # the alias (or any plain name) will be used.

        ref = self.static()
        origin = ref and self.get_origin()
        static_name = origin and encode_path(origin)

        # Determine whether a qualified name is involved.

        t = (not self.is_constant_alias() and self.get_name() or self.name).rsplit(".", 1)
        parent = len(t) > 1 and t[0] or None
        attrname = t[-1] and encode_path(t[-1])

        # Assignments.

        if self.expr:

            # Eliminate assignments between constants.

            if ref and self.expr.static():
                return ""

            # Qualified names must be converted into parent-relative assignments.

            elif parent:
                return "__store_via_object(&%s, %s, %s)" % (
                    encode_path(parent), attrname, self.expr)

            # All other assignments involve the names as they were given.

            else:
                return "(%s%s) = %s" % (self.parameter and "*" or "", attrname, self.expr)

        # Expressions.

        elif static_name:
            parent = ref.parent()
            context = ref.has_kind("<function>") and encode_path(parent) or None
            return "__ATTRVALUE(&%s)" % static_name

        # Qualified names must be converted into parent-relative accesses.

        elif parent:
            return "__load_via_object(&%s, %s)" % (
                encode_path(parent), attrname)

        # All other accesses involve the names as they were given.

        else:
            return "(%s%s)" % (self.parameter and "*" or "", attrname)

class TrConstantValueRef(ConstantValueRef):

    "A constant value reference in the translation."

    def __str__(self):
        return encode_literal_constant(self.number)

class TrLiteralSequenceRef(LiteralSequenceRef):

    "A reference representing a sequence of values."

    def __str__(self):
        return str(self.node)

class TrInstanceRef(InstanceRef):

    "A reference representing instantiation of a class."

    def __init__(self, ref, expr):

        """
        Initialise the reference with 'ref' indicating the nature of the
        reference and 'expr' being an expression used to create the instance.
        """

        InstanceRef.__init__(self, ref)
        self.expr = expr

    def __str__(self):
        return self.expr

    def __repr__(self):
        return "TrResolvedInstanceRef(%r, %r)" % (self.ref, self.expr)

class AttrResult(Result, InstructionSequence):

    "A translation result for an attribute access."

    def __init__(self, instructions, refs, location, context_identity):
        InstructionSequence.__init__(self, instructions)
        self.refs = refs
        self.location = location
        self.context_identity = context_identity

    def references(self):
        return self.refs

    def access_location(self):
        return self.location

    def context(self):
        return self.context_identity

    def get_origin(self):
        return self.refs and len(self.refs) == 1 and first(self.refs).get_origin()

    def has_kind(self, kinds):
        if not self.refs:
            return False
        for ref in self.refs:
            if ref.has_kind(kinds):
                return True
        return False

    def __nonzero__(self):
        return bool(self.instructions)

    def __str__(self):
        return encode_instructions(self.instructions)

    def __repr__(self):
        return "AttrResult(%r, %r, %r)" % (self.instructions, self.refs, self.location)

class AliasResult(NameRef, Result):

    "An alias for other values."

    def __init__(self, name_ref, refs, location):
        NameRef.__init__(self, name_ref.name, is_global=name_ref.is_global_name())
        self.name_ref = name_ref
        self.refs = refs
        self.location = location

    def references(self):
        ref = self.name_ref.reference()
        return self.refs or ref and [ref] or None

    def reference(self):
        refs = self.references()
        return len(refs) == 1 and first(refs) or None

    def access_location(self):
        return self.location

    def get_name(self):
        ref = self.reference()
        return ref and ref.get_name()

    def get_origin(self):
        ref = self.reference()
        return ref and ref.get_origin()

    def static(self):
        ref = self.reference()
        return ref and ref.static()

    def final(self):
        ref = self.reference()
        return ref and ref.final()

    def has_kind(self, kinds):
        if not self.refs:
            return self.name_ref.has_kind(kinds)

        for ref in self.refs:
            if ref.has_kind(kinds):
                return True

        return False

    def __str__(self):
        return str(self.name_ref)

    def __repr__(self):
        return "AliasResult(%r, %r)" % (self.name_ref, self.refs)

class InvocationResult(Result, InstructionSequence):

    "A translation result for an invocation."

    def __str__(self):
        return encode_instructions(self.instructions)

    def __repr__(self):
        return "InvocationResult(%r)" % self.instructions

class InstantiationResult(InvocationResult, TrInstanceRef):

    "An instantiation result acting like an invocation result."

    def __init__(self, ref, instructions):
        InstanceRef.__init__(self, ref)
        InvocationResult.__init__(self, instructions)

    def __repr__(self):
        return "InstantiationResult(%r, %r)" % (self.ref, self.instructions)

class PredefinedConstantRef(Result):

    "A predefined constant reference."

    def __init__(self, value, expr=None):
        self.value = value
        self.expr = expr

    def __str__(self):

        # Eliminate predefined constant assignments.

        if self.expr:
            return ""

        # Generate the specific constants.

        if self.value in ("False", "True"):
            return encode_path("__builtins__.boolean.%s" % self.value)
        elif self.value == "None":
            return encode_path("__builtins__.none.%s" % self.value)
        elif self.value == "NotImplemented":
            return encode_path("__builtins__.notimplemented.%s" % self.value)
        else:
            return self.value

    def __repr__(self):
        return "PredefinedConstantRef(%r)" % self.value

class LogicalResult(Result):

    "A logical expression result."

    def _convert(self, expr):

        "Return 'expr' converted to a testable value."

        if isinstance(expr, LogicalResult):
            return expr.apply_test()
        else:
            return "__BOOL(%s)" % expr

class NegationResult(LogicalResult):

    "A negation expression result."

    def __init__(self, expr):
        self.expr = expr

    def apply_test(self):

        "Return the result in a form suitable for direct testing."

        expr = self._convert(self.expr)
        return "(!%s)" % expr

    def discards_temporary(self, test=True):

        """
        Negations should have discarded their operand's temporary names when
        being instantiated.
        """

        return None

    def __str__(self):
        return "(%s ? %s : %s)" % (
            self._convert(self.expr),
            PredefinedConstantRef("False"),
            PredefinedConstantRef("True"))

    def __repr__(self):
        return "NegationResult(%r)" % self.expr

class LogicalOperationResult(LogicalResult):

    "A logical operation result."

    def __init__(self, exprs, conjunction):
        self.exprs = exprs
        self.conjunction = conjunction

    def apply_test(self):

        """
        Return the result in a form suitable for direct testing.

        Convert ... to ...

        <a> and <b>
        ((__BOOL(<a>)) && (__BOOL(<b>)))

        <a> or <b>
        ((__BOOL(<a>)) || (__BOOL(<b>)))
        """

        results = []
        for expr in self.exprs:
            results.append(self._convert(expr))

        if self.conjunction:
            return "(%s)" % " && ".join(results)
        else:
            return "(%s)" % " || ".join(results)

    def discards_temporary(self, test=True):

        """
        Return a list of temporary names that can be discarded if 'test' is
        specified as a true value (or omitted).
        """

        if not test:
            return None

        temps = ["__tmp_result"]

        for expr in self.exprs:
            t = expr.discards_temporary(test)
            if t:
                temps += t

        return temps

    def __str__(self):

        """
        Convert ... to ...

        <a> and <b>
        (__tmp_result = <a>, !__BOOL(__tmp_result)) ? __tmp_result : <b>

        <a> or <b>
        (__tmp_result = <a>, __BOOL(__tmp_result)) ? __tmp_result : <b>
        """

        results = []
        for expr in self.exprs[:-1]:
            results.append("(__tmp_result = %s, %s__BOOL(__tmp_result)) ? __tmp_result : " % (expr, self.conjunction and "!" or ""))
        results.append(str(self.exprs[-1]))

        return "(%s)" % "".join(results)

    def __repr__(self):
        return "LogicalOperationResult(%r, %r)" % (self.exprs, self.conjunction)

# vim: tabstop=4 expandtab shiftwidth=4
