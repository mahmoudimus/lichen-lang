#!/usr/bin/env python

"""
Translate programs.

Copyright (C) 2015, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

from common import CommonModule, CommonOutput, InstructionSequence, \
                   first, get_builtin_class, init_item, predefined_constants
from encoders import encode_access_instruction, \
                     encode_function_pointer, encode_literal_constant, \
                     encode_literal_instantiator, encode_instantiator_pointer, \
                     encode_instructions, \
                     encode_path, encode_symbol, encode_type_attribute, \
                     is_type_attribute
from errors import InspectError, TranslateError
from os.path import exists, join
from os import makedirs
from referencing import Reference
from StringIO import StringIO
import compiler
import results

class Translator(CommonOutput):

    "A program translator."

    def __init__(self, importer, deducer, optimiser, output):
        self.importer = importer
        self.deducer = deducer
        self.optimiser = optimiser
        self.output = output
        self.modules = {}

    def to_output(self):
        output = join(self.output, "src")

        if not exists(output):
            makedirs(output)

        self.check_output()

        for module in self.importer.modules.values():
            parts = module.name.split(".")
            if parts[0] != "native":
                tm = TranslatedModule(module.name, self.importer, self.deducer, self.optimiser)
                tm.translate(module.filename, join(output, "%s.c" % module.name))
                self.modules[module.name] = tm 

# Classes representing intermediate translation results.

class TranslationResult:

    "An abstract translation result mix-in."

    def get_accessor_kinds(self):
        return None

class ReturnRef(TranslationResult):

    "Indicates usage of a return statement."

    pass

class Expression(results.Result, TranslationResult):

    "A general expression."

    def __init__(self, s):
        self.s = s
    def __str__(self):
        return self.s
    def __repr__(self):
        return "Expression(%r)" % self.s

class TrResolvedNameRef(results.ResolvedNameRef, TranslationResult):

    "A reference to a name in the translation."

    def __init__(self, name, ref, expr=None, parameter=None, unsuitable=None):
        results.ResolvedNameRef.__init__(self, name, ref, expr)
        self.parameter = parameter
        self.unsuitable = unsuitable

    def unsuitable_invocations(self):
        return self.unsuitable

    def __str__(self):

        "Return an output representation of the referenced name."

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

            if ref and isinstance(self.expr, results.ResolvedNameRef) and self.expr.static():
                return ""

            # Qualified names must be converted into parent-relative assignments.

            elif parent:
                return "__store_via_object(&%s, %s, %s)" % (
                    encode_path(parent), encode_symbol("pos", attrname), self.expr)

            # All other assignments involve the names as they were given.

            else:
                return "(%s%s) = %s" % (self.parameter and "*" or "", attrname, self.expr)

        # Expressions.

        elif static_name:
            parent = ref.parent()
            context = ref.has_kind("<function>") and encode_path(parent) or None
            return "((__attr) {.context=%s, .value=&%s})" % (context and "&%s" % context or "0", static_name)

        # Qualified names must be converted into parent-relative accesses.

        elif parent:
            return "__load_via_object(&%s, %s)" % (
                encode_path(parent), encode_symbol("pos", attrname))

        # All other accesses involve the names as they were given.

        else:
            return "(%s%s)" % (self.parameter and "*" or "", attrname)

class TrConstantValueRef(results.ConstantValueRef, TranslationResult):

    "A constant value reference in the translation."

    def __str__(self):
        return encode_literal_constant(self.number)

class TrLiteralSequenceRef(results.LiteralSequenceRef, TranslationResult):

    "A reference representing a sequence of values."

    def __str__(self):
        return str(self.node)

class TrInstanceRef(results.InstanceRef, TranslationResult):

    "A reference representing instantiation of a class."

    def __init__(self, ref, expr):

        """
        Initialise the reference with 'ref' indicating the nature of the
        reference and 'expr' being an expression used to create the instance.
        """

        results.InstanceRef.__init__(self, ref)
        self.expr = expr

    def __str__(self):
        return self.expr

    def __repr__(self):
        return "TrResolvedInstanceRef(%r, %r)" % (self.ref, self.expr)

class AttrResult(Expression, TranslationResult, InstructionSequence):

    "A translation result for an attribute access."

    def __init__(self, instructions, refs, accessor_kinds, unsuitable):
        InstructionSequence.__init__(self, instructions)
        self.refs = refs
        self.accessor_kinds = accessor_kinds
        self.unsuitable = unsuitable

    def references(self):
        return self.refs

    def unsuitable_invocations(self):
        return self.unsuitable

    def get_origin(self):
        return self.refs and len(self.refs) == 1 and first(self.refs).get_origin()

    def has_kind(self, kinds):
        if not self.refs:
            return False
        for ref in self.refs:
            if ref.has_kind(kinds):
                return True
        return False

    def get_accessor_kinds(self):
        return self.accessor_kinds

    def __str__(self):
        return encode_instructions(self.instructions)

    def __repr__(self):
        return "AttrResult(%r, %r, %r)" % (self.instructions, self.refs, self.accessor_kinds)

class InvocationResult(Expression, TranslationResult, InstructionSequence):

    "A translation result for an invocation."

    def __init__(self, instructions):
        InstructionSequence.__init__(self, instructions)

    def __str__(self):
        return encode_instructions(self.instructions)

    def __repr__(self):
        return "InvocationResult(%r)" % self.instructions

class InstantiationResult(InvocationResult, TrInstanceRef):

    "An instantiation result acting like an invocation result."

    def __init__(self, ref, instructions):
        results.InstanceRef.__init__(self, ref)
        InvocationResult.__init__(self, instructions)

    def __repr__(self):
        return "InstantiationResult(%r, %r)" % (self.ref, self.instructions)

class PredefinedConstantRef(Expression, TranslationResult):

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

class BooleanResult(Expression, TranslationResult):

    "A expression producing a boolean result."

    def __str__(self):
        return "__builtins___bool_bool(%s)" % self.s

    def __repr__(self):
        return "BooleanResult(%r)" % self.s

def make_expression(expr):

    "Make a new expression from the existing 'expr'."

    if isinstance(expr, results.Result):
        return expr
    else:
        return Expression(str(expr))



# The actual translation process itself.

class TranslatedModule(CommonModule):

    "A module translator."

    def __init__(self, name, importer, deducer, optimiser):
        CommonModule.__init__(self, name, importer)
        self.deducer = deducer
        self.optimiser = optimiser

        # Output stream.

        self.out_toplevel = self.out = None
        self.indent = 0
        self.tabstop = "    "

        # Recorded namespaces.

        self.namespaces = []
        self.in_conditional = False

        # Exception raising adjustments.

        self.in_try_finally = False
        self.in_try_except = False

        # Attribute access and accessor counting.

        self.attr_accesses = {}
        self.attr_accessors = {}

        # Special variable usage.

        self.temp_usage = {}

    def __repr__(self):
        return "TranslatedModule(%r, %r)" % (self.name, self.importer)

    def translate(self, filename, output_filename):

        """
        Parse the file having the given 'filename', writing the translation to
        the given 'output_filename'.
        """

        self.parse_file(filename)

        # Collect function namespaces for separate processing.

        self.record_namespaces(self.astnode)

        # Reset the lambda naming (in order to obtain the same names again) and
        # translate the program.

        self.reset_lambdas()

        self.out_toplevel = self.out = open(output_filename, "w")
        try:
            self.start_output()

            # Process namespaces, writing the translation.

            for path, node in self.namespaces:
                self.process_namespace(path, node)

            # Process the module namespace including class namespaces.

            self.process_namespace([], self.astnode)

        finally:
            self.out.close()

    def have_object(self):

        "Return whether a namespace is a recorded object."

        return self.importer.objects.get(self.get_namespace_path())

    def get_builtin_class(self, name):

        "Return a reference to the actual object providing 'name'."

        return self.importer.get_object(get_builtin_class(name))

    def is_method(self, path):

        "Return whether 'path' is a method."

        class_name, method_name = path.rsplit(".", 1)
        return self.importer.classes.has_key(class_name) and class_name or None

    def in_method(self):

        "Return whether the current namespace provides a method."

        return self.in_function and self.is_method(self.get_namespace_path())

    # Namespace recording.

    def record_namespaces(self, node):

        "Process the program structure 'node', recording namespaces."

        for n in node.getChildNodes():
            self.record_namespaces_in_node(n)

    def record_namespaces_in_node(self, node):

        "Process the program structure 'node', recording namespaces."

        # Function namespaces within modules, classes and other functions.
        # Functions appearing within conditional statements are given arbitrary
        # names.

        if isinstance(node, compiler.ast.Function):
            self.record_function_node(node, (self.in_conditional or self.in_function) and self.get_lambda_name() or node.name)

        elif isinstance(node, compiler.ast.Lambda):
            self.record_function_node(node, self.get_lambda_name())

        # Classes are visited, but may be ignored if inside functions.

        elif isinstance(node, compiler.ast.Class):
            self.enter_namespace(node.name)
            if self.have_object():
                self.record_namespaces(node)
            self.exit_namespace()

        # Conditional nodes are tracked so that function definitions may be
        # handled. Since "for" loops are converted to "while" loops, they are
        # included here.

        elif isinstance(node, (compiler.ast.For, compiler.ast.If, compiler.ast.While)):
            in_conditional = self.in_conditional
            self.in_conditional = True
            self.record_namespaces(node)
            self.in_conditional = in_conditional

        # All other nodes are processed depth-first.

        else:
            self.record_namespaces(node)

    def record_function_node(self, n, name):

        """
        Record the given function, lambda, if expression or list comprehension
        node 'n' with the given 'name'.
        """

        self.in_function = True
        self.enter_namespace(name)

        if self.have_object():

            # Record the namespace path and the node itself.

            self.namespaces.append((self.namespace_path[:], n))
            self.record_namespaces_in_node(n.code)

        self.exit_namespace()
        self.in_function = False

    # Constant referencing.

    def get_literal_instance(self, n, name=None):

        """
        For node 'n', return a reference for the type of the given 'name', or if
        'name' is not specified, deduce the type from the value.
        """

        # Handle stray None constants (Sliceobj seems to produce them).

        if name is None and n.value is None:
            return self.process_name_node(compiler.ast.Name("None"))

        if name in ("dict", "list", "tuple"):
            ref = self.get_builtin_class(name)
            return self.process_literal_sequence_node(n, name, ref, TrLiteralSequenceRef)
        else:
            value, typename, encoding = self.get_constant_value(n.value, n.literals)
            ref = self.get_builtin_class(typename)
            value_type = ref.get_origin()

            path = self.get_namespace_path()

            # Obtain the local numbering of the constant and thus the
            # locally-qualified name.

            local_number = self.importer.all_constants[path][(value, value_type, encoding)]
            constant_name = "$c%d" % local_number
            objpath = self.get_object_path(constant_name)

            # Obtain the unique identifier for the constant.

            number = self.optimiser.constant_numbers[objpath]
            return TrConstantValueRef(constant_name, ref.instance_of(), value, number)

    # Namespace translation.

    def process_namespace(self, path, node):

        """
        Process the namespace for the given 'path' defined by the given 'node'.
        """

        self.namespace_path = path

        if isinstance(node, (compiler.ast.Function, compiler.ast.Lambda)):
            self.in_function = True
            self.process_function_body_node(node)
        else:
            self.in_function = False
            self.function_target = 0
            self.start_module()
            self.process_structure(node)
            self.end_module()

    def process_structure(self, node):

        "Process the given 'node' or result."

        # Handle processing requests on results.

        if isinstance(node, results.Result):
            return node

        # Handle processing requests on nodes.

        else:
            l = CommonModule.process_structure(self, node)

            # Return indications of return statement usage.

            if l and isinstance(l[-1], ReturnRef):
                return l[-1]
            else:
                return None

    def process_structure_node(self, n):

        "Process the individual node 'n'."

        # Plain statements emit their expressions.

        if isinstance(n, compiler.ast.Discard):
            expr = self.process_structure_node(n.expr)
            self.statement(expr)

        # Module import declarations.

        elif isinstance(n, compiler.ast.From):
            self.process_from_node(n)

        # Nodes using operator module functions.

        elif isinstance(n, compiler.ast.Operator):
            return self.process_operator_node(n)

        elif isinstance(n, compiler.ast.AugAssign):
            self.process_augassign_node(n)

        elif isinstance(n, compiler.ast.Compare):
            return self.process_compare_node(n)

        elif isinstance(n, compiler.ast.Slice):
            return self.process_slice_node(n)

        elif isinstance(n, compiler.ast.Sliceobj):
            return self.process_sliceobj_node(n)

        elif isinstance(n, compiler.ast.Subscript):
            return self.process_subscript_node(n)

        # Classes are visited, but may be ignored if inside functions.

        elif isinstance(n, compiler.ast.Class):
            self.process_class_node(n)

        # Functions within namespaces have any dynamic defaults initialised.

        elif isinstance(n, compiler.ast.Function):
            self.process_function_node(n)

        # Lambdas are replaced with references to separately-generated
        # functions.

        elif isinstance(n, compiler.ast.Lambda):
            return self.process_lambda_node(n)

        # Assignments.

        elif isinstance(n, compiler.ast.Assign):

            # Handle each assignment node.

            for node in n.nodes:
                self.process_assignment_node(node, n.expr)

        # Accesses.

        elif isinstance(n, compiler.ast.Getattr):
            return self.process_attribute_access(n)

        # Names.

        elif isinstance(n, compiler.ast.Name):
            return self.process_name_node(n)

        # Loops and conditionals.

        elif isinstance(n, compiler.ast.For):
            self.process_for_node(n)

        elif isinstance(n, compiler.ast.While):
            self.process_while_node(n)

        elif isinstance(n, compiler.ast.If):
            self.process_if_node(n)

        elif isinstance(n, (compiler.ast.And, compiler.ast.Or)):
            return self.process_logical_node(n)

        elif isinstance(n, compiler.ast.Not):
            return self.process_not_node(n)

        # Exception control-flow tracking.

        elif isinstance(n, compiler.ast.TryExcept):
            self.process_try_node(n)

        elif isinstance(n, compiler.ast.TryFinally):
            self.process_try_finally_node(n)

        # Control-flow modification statements.

        elif isinstance(n, compiler.ast.Break):
            self.writestmt("break;")

        elif isinstance(n, compiler.ast.Continue):
            self.writestmt("continue;")

        elif isinstance(n, compiler.ast.Raise):
            self.process_raise_node(n)

        elif isinstance(n, compiler.ast.Return):
            return self.process_return_node(n)

        # Print statements.

        elif isinstance(n, (compiler.ast.Print, compiler.ast.Printnl)):
            self.statement(self.process_print_node(n))

        # Invocations.

        elif isinstance(n, compiler.ast.CallFunc):
            return self.process_invocation_node(n)

        elif isinstance(n, compiler.ast.Keyword):
            return self.process_structure_node(n.expr)

        # Constant usage.

        elif isinstance(n, compiler.ast.Const):
            return self.get_literal_instance(n)

        elif isinstance(n, compiler.ast.Dict):
            return self.get_literal_instance(n, "dict")

        elif isinstance(n, compiler.ast.List):
            return self.get_literal_instance(n, "list")

        elif isinstance(n, compiler.ast.Tuple):
            return self.get_literal_instance(n, "tuple")

        # All other nodes are processed depth-first.

        else:
            return self.process_structure(n)

    def process_assignment_node(self, n, expr):

        "Process the individual node 'n' to be assigned the contents of 'expr'."

        # Names and attributes are assigned the entire expression.

        if isinstance(n, compiler.ast.AssName):
            name_ref = self.process_name_node(n, self.process_structure_node(expr))
            self.statement(name_ref)

            # Employ guards after assignments if required.

            if expr and name_ref.is_name():
                self.generate_guard(name_ref.name)

        elif isinstance(n, compiler.ast.AssAttr):
            in_assignment = self.in_assignment
            self.in_assignment = self.process_structure_node(expr)
            self.statement(self.process_attribute_access(n))
            self.in_assignment = in_assignment

        # Lists and tuples are matched against the expression and their
        # items assigned to expression items.

        elif isinstance(n, (compiler.ast.AssList, compiler.ast.AssTuple)):
            self.process_assignment_node_items(n, expr)

        # Slices and subscripts are permitted within assignment nodes.

        elif isinstance(n, compiler.ast.Slice):
            self.statement(self.process_slice_node(n, expr))

        elif isinstance(n, compiler.ast.Subscript):
            self.statement(self.process_subscript_node(n, expr))

    def process_attribute_access(self, n):

        "Process the given attribute access node 'n'."

        # Obtain any completed chain and return the reference to it.

        attr_expr = self.process_attribute_chain(n)
        if self.have_access_expression(n):
            return attr_expr

        # Where the start of the chain of attributes has been reached, process
        # the complete access.

        name_ref = attr_expr and attr_expr.is_name() and attr_expr
        name = name_ref and self.get_name_for_tracking(name_ref.name, name_ref and name_ref.final()) or None

        location = self.get_access_location(name, self.attrs)
        refs = self.get_referenced_attributes(location)
        unsuitable = self.get_referenced_attribute_invocations(location)

        # Generate access instructions.

        subs = {
            "<expr>" : attr_expr,
            "<assexpr>" : self.in_assignment,
            }

        temp_subs = {
            "<context>" : "__tmp_context",
            "<accessor>" : "__tmp_value",
            "<target_accessor>" : "__tmp_target_value",
            "<set_accessor>" : "__tmp_value",
            "<set_target_accessor>" : "__tmp_target_value",
            }

        op_subs = {
            "<set_accessor>" : "__set_accessor",
            "<set_target_accessor>" : "__set_target_accessor",
            }

        subs.update(temp_subs)
        subs.update(op_subs)

        output = []
        substituted = set()

        # Obtain encoded versions of each instruction, accumulating temporary
        # variables.

        for instruction in self.optimiser.access_instructions[location]:
            encoded, _substituted = encode_access_instruction(instruction, subs)
            output.append(encoded)
            substituted.update(_substituted)

        # Record temporary name usage.

        for sub in substituted:
            if temp_subs.has_key(sub):
                self.record_temp(temp_subs[sub])

        del self.attrs[0]
        return AttrResult(output, refs, self.get_accessor_kinds(location), unsuitable)

    def get_referenced_attributes(self, location):

        """
        Convert 'location' to the form used by the deducer and retrieve any
        identified attributes.
        """

        access_location = self.deducer.const_accesses.get(location)
        refs = []
        for attrtype, objpath, attr in self.deducer.referenced_attrs[access_location or location]:
            refs.append(attr)
        return refs

    def get_referenced_attribute_invocations(self, location):

        """
        Convert 'location' to the form used by the deducer and retrieve any
        identified attribute invocation details.
        """

        access_location = self.deducer.const_accesses.get(location)
        return self.deducer.reference_invocations_unsuitable.get(access_location or location)

    def get_accessor_kinds(self, location):

        "Return the accessor kinds for 'location'."

        return self.optimiser.accessor_kinds[location]

    def get_access_location(self, name, attrnames=None):

        """
        Using the current namespace, the given 'name', and the 'attrnames'
        employed in an access, return the access location.
        """

        path = self.get_path_for_access()

        # Get the location used by the deducer and optimiser and find any
        # recorded access.

        attrnames = attrnames and ".".join(self.attrs)
        access_number = self.get_access_number(path, name, attrnames)
        self.update_access_number(path, name, attrnames)
        return (path, name, attrnames, access_number)

    def get_access_number(self, path, name, attrnames):
        access = name, attrnames
        if self.attr_accesses.has_key(path) and self.attr_accesses[path].has_key(access):
            return self.attr_accesses[path][access]
        else:
            return 0

    def update_access_number(self, path, name, attrnames):
        access = name, attrnames
        if name:
            init_item(self.attr_accesses, path, dict)
            init_item(self.attr_accesses[path], access, lambda: 0)
            self.attr_accesses[path][access] += 1

    def get_accessor_location(self, name):

        """
        Using the current namespace and the given 'name', return the accessor
        location.
        """

        path = self.get_path_for_access()

        # Get the location used by the deducer and optimiser and find any
        # recorded accessor.

        access_number = self.get_accessor_number(path, name)
        self.update_accessor_number(path, name)
        return (path, name, None, access_number)

    def get_accessor_number(self, path, name):
        if self.attr_accessors.has_key(path) and self.attr_accessors[path].has_key(name):
            return self.attr_accessors[path][name]
        else:
            return 0

    def update_accessor_number(self, path, name):
        if name:
            init_item(self.attr_accessors, path, dict)
            init_item(self.attr_accessors[path], name, lambda: 0)
            self.attr_accessors[path][name] += 1

    def process_class_node(self, n):

        "Process the given class node 'n'."

        class_name = self.get_object_path(n.name)

        # Where a class is set conditionally or where the name may refer to
        # different values, assign the name.

        ref = self.importer.identify(class_name)

        if not ref.static():
            self.process_assignment_for_object(
                n.name, make_expression("((__attr) {.context=0, .value=&%s})" %
                    encode_path(class_name)))

        self.enter_namespace(n.name)

        if self.have_object():
            self.write_comment("Class: %s" % class_name)

            self.initialise_inherited_members(class_name)

            self.process_structure(n)
            self.write_comment("End class: %s" % class_name)

        self.exit_namespace()

    def initialise_inherited_members(self, class_name):

        "Initialise members of 'class_name' inherited from its ancestors."

        for name, path in self.importer.all_class_attrs[class_name].items():
            target = "%s.%s" % (class_name, name)

            # Ignore attributes with definitions.

            ref = self.importer.identify(target)
            if ref:
                continue

            # Ignore special type attributes.

            if is_type_attribute(name):
                continue

            # Reference inherited attributes.

            ref = self.importer.identify(path)
            if ref and not ref.static():
                parent, attrname = path.rsplit(".", 1)

                self.writestmt("__store_via_object(&%s, %s, __load_via_object(&%s, %s));" % (
                    encode_path(class_name), encode_symbol("pos", name),
                    encode_path(parent), encode_symbol("pos", attrname)
                    ))

    def process_from_node(self, n):

        "Process the given node 'n', importing from another module."

        path = self.get_namespace_path()

        # Attempt to obtain the referenced objects.

        for name, alias in n.names:
            if name == "*":
                raise InspectError("Only explicitly specified names can be imported from modules.", path, n)

            # Obtain the path of the assigned name.

            objpath = self.get_object_path(alias or name)

            # Obtain the identity of the name.

            ref = self.importer.identify(objpath)

            # Where the name is not static, assign the value.

            if ref and not ref.static() and ref.get_name():
                self.writestmt("%s;" % 
                    TrResolvedNameRef(alias or name, Reference("<var>", None, objpath),
                                      expr=TrResolvedNameRef(name, ref)))

    def process_function_body_node(self, n):

        """
        Process the given function, lambda, if expression or list comprehension
        node 'n', generating the body.
        """

        function_name = self.get_namespace_path()
        self.start_function(function_name)

        # Process the function body.

        in_conditional = self.in_conditional
        self.in_conditional = False
        self.function_target = 0

        # Process any guards defined for the parameters.

        for name in self.importer.function_parameters.get(function_name):
            self.generate_guard(name)

        # Produce the body and any additional return statement.

        expr = self.process_structure_node(n.code) or PredefinedConstantRef("None")
        if not isinstance(expr, ReturnRef):
            self.writestmt("return %s;" % expr)

        self.in_conditional = in_conditional

        self.end_function(function_name)

    def generate_guard(self, name):

        """
        Get the accessor details for 'name', found in the current namespace, and
        generate any guards defined for it.
        """

        # Obtain the location, keeping track of assignment versions.

        location = self.get_accessor_location(name)
        test = self.deducer.accessor_guard_tests.get(location)

        # Generate any guard from the deduced information.

        if test:
            guard, guard_type = test

            if guard == "specific":
                ref = first(self.deducer.accessor_all_types[location])
                argstr = "&%s" % encode_path(ref.get_origin())
            elif guard == "common":
                ref = first(self.deducer.accessor_all_general_types[location])
                typeattr = encode_type_attribute(ref.get_origin())
                argstr = "%s, %s" % (encode_symbol("pos", typeattr), encode_symbol("code", typeattr))
            else:
                return

            # Produce an appropriate access to an attribute's value.

            parameters = self.importer.function_parameters.get(self.get_namespace_path())
            if parameters and name in parameters:
                name_to_value = "%s->value" % name
            else:
                name_to_value = "%s.value" % name

            # Write a test that raises a TypeError upon failure.

            self.writestmt("if (!__test_%s_%s(%s, %s)) __raise_type_error();" % (
                guard, guard_type, name_to_value, argstr))

    def process_function_node(self, n):

        """
        Process the given function, lambda, if expression or list comprehension
        node 'n', generating any initialisation statements.
        """

        # Where a function is declared conditionally, use a separate name for
        # the definition, and assign the definition to the stated name.

        original_name = n.name

        if self.in_conditional or self.in_function:
            name = self.get_lambda_name()
        else:
            name = n.name

        objpath = self.get_object_path(name)

        # Obtain details of the defaults.

        defaults = self.process_function_defaults(n, name, objpath)
        if defaults:
            for default in defaults:
                self.writeline("%s;" % default)

        # Where a function is set conditionally or where the name may refer to
        # different values, assign the name.

        ref = self.importer.identify(objpath)

        if self.in_conditional or self.in_function:
            self.process_assignment_for_object(original_name, compiler.ast.Name(name))
        elif not ref.static():
            context = self.is_method(objpath)

            self.process_assignment_for_object(original_name,
                make_expression("((__attr) {.context=%s, .value=&%s})" % (
                    context and "&%s" % encode_path(context) or "0",
                    encode_path(objpath))))

    def process_function_defaults(self, n, name, objpath, instance_name=None):

        """
        Process the given function or lambda node 'n', initialising defaults
        that are dynamically set. The given 'name' indicates the name of the
        function. The given 'objpath' indicates the origin of the function.
        The given 'instance_name' indicates the name of any separate instance
        of the function created to hold the defaults.

        Return a list of operations setting defaults on a function instance.
        """

        function_name = self.get_object_path(name)
        function_defaults = self.importer.function_defaults.get(function_name)
        if not function_defaults:
            return None

        # Determine whether any unidentified defaults are involved.

        for argname, default in function_defaults:
            if not default.static():
                break
        else:
            return None

        # Handle bound methods.

        if not instance_name:
            instance_name = "&%s" % encode_path(objpath)

        # Where defaults are involved but cannot be identified, obtain a new
        # instance of the lambda and populate the defaults.

        defaults = []

        # Join the original defaults with the inspected defaults.

        original_defaults = [(argname, default) for (argname, default) in compiler.ast.get_defaults(n) if default]

        for i, (original, inspected) in enumerate(map(None, original_defaults, function_defaults)):

            # Obtain any reference for the default.

            if original:
                argname, default = original
                name_ref = self.process_structure_node(default)
            elif inspected:
                argname, default = inspected
                name_ref = TrResolvedNameRef(argname, default)
            else:
                continue

            # Generate default initialisers except when constants are employed.
            # Constants should be used when populating the function structures.

            if name_ref and not isinstance(name_ref, TrConstantValueRef):
                defaults.append("__SETDEFAULT(%s, %s, %s)" % (instance_name, i, name_ref))

        return defaults

    def process_if_node(self, n):

        """
        Process the given "if" node 'n'.
        """

        first = True
        for test, body in n.tests:
            test_ref = self.process_structure_node(test)
            self.start_if(first, test_ref)

            in_conditional = self.in_conditional
            self.in_conditional = True
            self.process_structure_node(body)
            self.in_conditional = in_conditional

            self.end_if()
            first = False

        if n.else_:
            self.start_else()
            self.process_structure_node(n.else_)
            self.end_else()

    def process_invocation_node(self, n):

        "Process the given invocation node 'n'."

        expr = self.process_structure_node(n.node)
        objpath = expr.get_origin()

        # Identified target details.

        target = None
        target_structure = None

        # Specific function target information.

        function = None

        # Instantiation involvement.

        instantiation = False
        literal_instantiation = False

        # Invocation requirements.

        context_required = True
        parameters = None

        # Obtain details of the callable and of its parameters.

        # Literals may be instantiated specially.

        if expr.is_name() and expr.name.startswith("$L") and objpath:
            instantiation = literal_instantiation = objpath
            target = encode_literal_instantiator(objpath)
            context_required = False

        # Identified targets employ function pointers directly.

        elif objpath:
            parameters = self.importer.function_parameters.get(objpath)

            # Class invocation involves instantiators.

            if expr.has_kind("<class>"):
                instantiation = objpath
                target = encode_instantiator_pointer(objpath)
                init_ref = self.importer.all_class_attrs[objpath]["__init__"]
                target_structure = "&%s" % encode_path(init_ref)
                context_required = False

            # Only plain functions and bound methods employ function pointers.

            elif expr.has_kind("<function>"):
                function = objpath

                # Test for functions and methods.

                context_required = self.is_method(objpath)
                accessor_kinds = expr.get_accessor_kinds()
                instance_accessor = accessor_kinds and \
                                    len(accessor_kinds) == 1 and \
                                    first(accessor_kinds) == "<instance>"

                # Only identify certain bound methods or functions.

                if not context_required or instance_accessor:
                    target = encode_function_pointer(objpath)

                # Access bound method defaults even if it is not clear whether
                # the accessor is appropriate.

                target_structure = "&%s" % encode_path(objpath)

        # Other targets are retrieved at run-time.

        else:
            unsuitable = expr.unsuitable_invocations()

            if unsuitable:
                for ref in unsuitable:
                    _objpath = ref.get_origin()
                    num_parameters = len(self.importer.function_parameters[_objpath])
                    print "In %s, at line %d, inappropriate number of " \
                        "arguments given. Need %d arguments to call %s." % (
                        self.get_namespace_path(), n.lineno, num_parameters,
                        _objpath)

        # Arguments are presented in a temporary frame array with any context
        # always being the first argument. Where it would be unused, it may be
        # set to null.

        if context_required:
            self.record_temp("__tmp_targets")
            args = ["__CONTEXT_AS_VALUE(__tmp_targets[%d])" % self.function_target]
        else:
            args = ["__NULL"]

        # Complete the array with null values, permitting tests for a complete
        # set of arguments.

        args += [None] * (not parameters and len(n.args) or parameters and len(parameters) or 0)
        kwcodes = []
        kwargs = []

        # Any invocations in the arguments will store target details in a
        # different location.

        self.function_target += 1

        for i, arg in enumerate(n.args):
            argexpr = self.process_structure_node(arg)

            # Store a keyword argument, either in the argument list or
            # in a separate keyword argument list for subsequent lookup.

            if isinstance(arg, compiler.ast.Keyword):

                # With knowledge of the target, store the keyword
                # argument directly.

                if parameters:
                    try:
                        argnum = parameters.index(arg.name)
                    except ValueError:
                        raise TranslateError("Argument %s is not recognised." % arg.name,
                                             self.get_namespace_path(), n)
                    args[argnum+1] = str(argexpr)

                # Otherwise, store the details in a separate collection.

                else:
                    kwargs.append(str(argexpr))
                    kwcodes.append("{%s, %s}" % (
                        encode_symbol("ppos", arg.name),
                        encode_symbol("pcode", arg.name)))

            # Store non-keyword arguments in the argument list, rejecting
            # superfluous arguments.

            else:
                try:
                    args[i+1] = str(argexpr)
                except IndexError:
                    raise TranslateError("Too many arguments specified.",
                                         self.get_namespace_path(), n)

        # Reference the current target again.

        self.function_target -= 1

        # Defaults are added to the frame where arguments are missing.

        if parameters:
            function_defaults = self.importer.function_defaults.get(objpath)
            if function_defaults:

                # Visit each default and set any missing arguments.
                # Use the target structure to obtain defaults, as opposed to the
                # actual function involved.

                for i, (argname, default) in enumerate(function_defaults):
                    argnum = parameters.index(argname)
                    if not args[argnum+1]:
                        args[argnum+1] = "__GETDEFAULT(%s, %d)" % (target_structure, i)

        # Test for missing arguments.

        if None in args:
            raise TranslateError("Not all arguments supplied.",
                                 self.get_namespace_path(), n)

        # Encode the arguments.

        argstr = "__ARGS(%s)" % ", ".join(args)
        kwargstr = kwargs and ("__ARGS(%s)" % ", ".join(kwargs)) or "0"
        kwcodestr = kwcodes and ("__KWARGS(%s)" % ", ".join(kwcodes)) or "0"

        # Where literal instantiation is occurring, add an argument indicating
        # the number of values.

        if literal_instantiation:
            argstr += ", %d" % (len(args) - 1)

        # First, the invocation expression is presented.

        stages = []

        # Without a known specific callable, the expression provides the target.

        if not target or context_required:
            self.record_temp("__tmp_targets")
            stages.append("__tmp_targets[%d] = %s" % (self.function_target, expr))

        # Any specific callable is then obtained.

        if target:
            stages.append(target)

        # Methods accessed via unidentified accessors are obtained. 

        elif function:
            self.record_temp("__tmp_targets")

            if context_required:
                stages.append("__get_function(__tmp_targets[%d])" % self.function_target)
            else:
                stages.append("__load_via_object(__tmp_targets[%d].value, %s).fn" % (
                    self.function_target, encode_symbol("pos", "__fn__")))

        # With a known target, the function is obtained directly and called.
        # By putting the invocation at the end of the final element in the
        # instruction sequence (the stages), the result becomes the result of
        # the sequence. Moreover, the parameters become part of the sequence
        # and thereby participate in a guaranteed evaluation order.

        if target or function:
            stages[-1] += "(%s)" % argstr
            if instantiation:
                return InstantiationResult(instantiation, stages)
            else:
                return InvocationResult(stages)

        # With unknown targets, the generic invocation function is applied to
        # the callable and argument collections.

        else:
            self.record_temp("__tmp_targets")
            stages.append("__invoke(\n__tmp_targets[%d],\n%d, %d, %s, %s,\n%d, %s\n)" % (
                self.function_target,
                self.always_callable and 1 or 0,
                len(kwargs), kwcodestr, kwargstr,
                len(args), argstr))
            return InvocationResult(stages)

    def always_callable(self, refs):

        "Determine whether all 'refs' are callable."

        for ref in refs:
            if not ref.static():
                return False
            else:
                origin = ref.final()
                if not self.importer.get_attribute(origin, "__fn__"):
                    return False
        return True

    def need_default_arguments(self, objpath, nargs):

        """
        Return whether any default arguments are needed when invoking the object
        given by 'objpath'.
        """

        parameters = self.importer.function_parameters.get(objpath)
        return nargs < len(parameters)

    def process_lambda_node(self, n):

        "Process the given lambda node 'n'."

        name = self.get_lambda_name()
        function_name = self.get_object_path(name)

        defaults = self.process_function_defaults(n, name, function_name, "__tmp_value")

        # Without defaults, produce an attribute referring to the function.

        if not defaults:
            return make_expression("((__attr) {.context=0, .value=&%s})" % encode_path(function_name))

        # With defaults, copy the function structure and set the defaults on the
        # copy.

        else:
            self.record_temp("__tmp_value")
            return make_expression("(__tmp_value = __COPY(&%s, sizeof(%s)), %s, (__attr) {.context=0, .value=__tmp_value})" % (
                encode_path(function_name),
                encode_symbol("obj", function_name),
                ", ".join(defaults)))

    def process_logical_node(self, n):

        """
        Process the given operator node 'n'.

        Convert ... to ...

        <a> and <b>
        (__tmp_result = <a>, !__BOOL(__tmp_result)) ? __tmp_result : <b>

        <a> or <b>
        (__tmp_result = <a>, __BOOL(__tmp_result)) ? __tmp_result : <b>
        """

        self.record_temp("__tmp_result")

        if isinstance(n, compiler.ast.And):
            op = "!"
        else:
            op = ""

        results = []

        for node in n.nodes[:-1]:
            expr = self.process_structure_node(node)
            results.append("(__tmp_result = %s, %s__BOOL(__tmp_result)) ? __tmp_result : " % (expr, op))

        expr = self.process_structure_node(n.nodes[-1])
        results.append(str(expr))

        return make_expression("(%s)" % "".join(results))

    def process_name_node(self, n, expr=None):

        "Process the given name node 'n' with the optional assignment 'expr'."

        # Determine whether the name refers to a static external entity.

        if n.name in predefined_constants:
            return PredefinedConstantRef(n.name, expr)

        # Convert literal references, operator function names, and print
        # function names to references.

        elif n.name.startswith("$L") or n.name.startswith("$op") or \
             n.name.startswith("$print"):

            ref, paths = self.importer.get_module(self.name).special[n.name]
            return TrResolvedNameRef(n.name, ref)

        # Get the appropriate name for the name reference, using the same method
        # as in the inspector.

        path = self.get_namespace_path()
        objpath = self.get_object_path(n.name)

        # Determine any assigned globals.

        globals = self.importer.get_module(self.name).scope_globals.get(path)
        if globals and n.name in globals:
            objpath = self.get_global_path(n.name)

        # Get the static identity of the name.

        ref = self.importer.identify(objpath)
        if ref and not ref.get_name():
            ref = ref.alias(objpath)

        # Obtain any resolved names for non-assignment names.

        if not expr and not ref and self.in_function:
            locals = self.importer.function_locals.get(path)
            ref = locals and locals.get(n.name)

        # Determine whether the name refers to a parameter. The generation of
        # parameter references is different from other names.

        parameters = self.importer.function_parameters.get(path)
        parameter = n.name == "self" and self.in_method() or \
                    parameters and n.name in parameters

        # Find any invocation details.

        location = self.get_access_location(n.name)
        unsuitable = self.get_referenced_attribute_invocations(location)

        # Qualified names are used for resolved static references or for
        # static namespace members. The reference should be configured to return
        # such names.

        return TrResolvedNameRef(n.name, ref, expr=expr, parameter=parameter, unsuitable=unsuitable)

    def process_not_node(self, n):

        "Process the given operator node 'n'."

        return make_expression("(__BOOL(%s) ? %s : %s)" %
            (self.process_structure_node(n.expr), PredefinedConstantRef("False"),
            PredefinedConstantRef("True")))

    def process_raise_node(self, n):

        "Process the given raise node 'n'."

        # NOTE: Determine which raise statement variants should be permitted.

        if n.expr1:

            # Names with accompanying arguments are treated like invocations.

            if n.expr2:
                call = compiler.ast.CallFunc(n.expr1, [n.expr2])
                exc = self.process_structure_node(call)
                self.writestmt("__Raise(%s);" % exc)

            # Raise instances, testing the kind at run-time if necessary and
            # instantiating any non-instance.

            else:
                exc = self.process_structure_node(n.expr1)

                if isinstance(exc, TrInstanceRef):
                    self.writestmt("__Raise(%s);" % exc)
                else:
                    self.writestmt("__Raise(__ensure_instance(%s));" % exc)
        else:
            self.writestmt("__Throw(__tmp_exc);")

    def process_return_node(self, n):

        "Process the given return node 'n'."

        expr = self.process_structure_node(n.value) or PredefinedConstantRef("None")
        if self.in_try_finally or self.in_try_except:
            self.writestmt("__Return(%s);" % expr)
        else:
            self.writestmt("return %s;" % expr)

        return ReturnRef()

    def process_try_node(self, n):

        """
        Process the given "try...except" node 'n'.
        """

        in_try_except = self.in_try_except
        self.in_try_except = True

        # Use macros to implement exception handling.

        self.writestmt("__Try")
        self.writeline("{")
        self.indent += 1
        self.process_structure_node(n.body)

        # Put the else statement in another try block that handles any raised
        # exceptions and converts them to exceptions that will not be handled by
        # the main handling block.

        if n.else_:
            self.writestmt("__Try")
            self.writeline("{")
            self.indent += 1
            self.process_structure_node(n.else_)
            self.indent -= 1
            self.writeline("}")
            self.writeline("__Catch (__tmp_exc)")
            self.writeline("{")
            self.indent += 1
            self.writeline("if (__tmp_exc.raising) __RaiseElse(__tmp_exc.arg);")
            self.writeline("else if (__tmp_exc.completing) __Throw(__tmp_exc);")
            self.indent -= 1
            self.writeline("}")

        # Complete the try block and enter the finally block, if appropriate.

        if self.in_try_finally:
            self.writestmt("__Complete;")

        self.indent -= 1
        self.writeline("}")

        self.in_try_except = in_try_except

        # Handlers are tests within a common handler block.

        self.writeline("__Catch (__tmp_exc)")
        self.writeline("{")
        self.indent += 1

        # Introduce an if statement to handle the completion of a try block.

        self.process_try_completion()

        # Handle exceptions in else blocks converted to __RaiseElse, converting
        # them back to normal exceptions.

        if n.else_:
            self.writeline("else if (__tmp_exc.raising_else) __Raise(__tmp_exc.arg);")

        # Exception handling.

        for name, var, handler in n.handlers:

            # Test for specific exceptions.

            if name is not None:
                name_ref = self.process_structure_node(name)
                self.writeline("else if (__ISINSTANCE(__tmp_exc.arg, %s))" % name_ref)
            else:
                self.writeline("else if (1)")

            self.writeline("{")
            self.indent += 1

            # Establish the local for the handler.

            if var is not None:
                self.writestmt("%s;" % self.process_name_node(var, make_expression("__tmp_exc.arg")))

            if handler is not None:
                self.process_structure_node(handler)

            self.indent -= 1
            self.writeline("}")

        # Re-raise unhandled exceptions.

        self.writeline("else __Throw(__tmp_exc);")

        # End the handler block.

        self.indent -= 1
        self.writeline("}")

    def process_try_finally_node(self, n):

        """
        Process the given "try...finally" node 'n'.
        """

        in_try_finally = self.in_try_finally
        self.in_try_finally = True

        # Use macros to implement exception handling.

        self.writestmt("__Try")
        self.writeline("{")
        self.indent += 1
        self.process_structure_node(n.body)
        self.indent -= 1
        self.writeline("}")

        self.in_try_finally = in_try_finally

        # Finally clauses handle special exceptions.

        self.writeline("__Catch (__tmp_exc)")
        self.writeline("{")
        self.indent += 1
        self.process_structure_node(n.final)

        # Introduce an if statement to handle the completion of a try block.

        self.process_try_completion()
        self.writeline("else __Throw(__tmp_exc);")

        self.indent -= 1
        self.writeline("}")

    def process_try_completion(self):

        "Generate a test for the completion of a try block."

        self.writestmt("if (__tmp_exc.completing)")
        self.writeline("{")
        self.indent += 1

        # Do not return anything at the module level.

        if self.get_namespace_path() != self.name:

            # Only use the normal return statement if no surrounding try blocks
            # apply.

            if not self.in_try_finally and not self.in_try_except:
                self.writeline("if (!__ISNULL(__tmp_exc.arg)) return __tmp_exc.arg;")
            else:
                self.writeline("if (!__ISNULL(__tmp_exc.arg)) __Throw(__tmp_exc);")

        self.indent -= 1
        self.writeline("}")

    def process_while_node(self, n):

        "Process the given while node 'n'."

        self.writeline("while (1)")
        self.writeline("{")
        self.indent += 1
        test = self.process_structure_node(n.test)

        # Emit the loop termination condition unless "while <true value>" is
        # indicated.

        if not (isinstance(test, PredefinedConstantRef) and test.value):

            # NOTE: This needs to evaluate whether the operand is true or false
            # NOTE: according to Python rules.

            self.writeline("if (!__BOOL(%s))" % test)
            self.writeline("{")
            self.indent += 1
            if n.else_:
                self.process_structure_node(n.else_)
            self.writestmt("break;")
            self.indent -= 1
            self.writeline("}")

        in_conditional = self.in_conditional
        self.in_conditional = True
        self.process_structure_node(n.body)
        self.in_conditional = in_conditional

        self.indent -= 1
        self.writeline("}")

    # Special variable usage.

    def record_temp(self, name):

        """
        Record the use of the temporary 'name' in the current namespace. At the
        class or module level, the temporary name is associated with the module,
        since the variable will then be allocated in the module's own main
        program.
        """

        if self.in_function:
            path = self.get_namespace_path()
        else:
            path = self.name

        init_item(self.temp_usage, path, set)
        self.temp_usage[path].add(name)

    def uses_temp(self, path, name):

        """
        Return whether the given namespace 'path' employs a temporary variable
        with the given 'name'. Note that 'path' should only be a module or a
        function or method, not a class.
        """

        return self.temp_usage.has_key(path) and name in self.temp_usage[path]

    # Output generation.

    def start_output(self):

        "Write the declarations at the top of each source file."

        print >>self.out, """\
#include "types.h"
#include "exceptions.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
#include "main.h"
"""

    def start_unit(self):

        "Record output within a generated function for later use."

        self.out = StringIO()

    def end_unit(self, name):

        "Add declarations and generated code."

        # Restore the output stream.

        out = self.out
        self.out = self.out_toplevel

        self.write_temporaries(name)
        out.seek(0)
        self.out.write(out.read())

        self.indent -= 1
        print >>self.out, "}"

    def start_module(self):

        "Write the start of each module's main function."

        print >>self.out, "void __main_%s()" % encode_path(self.name)
        print >>self.out, "{"
        self.indent += 1
        self.start_unit()

    def end_module(self):

        "End each module by closing its main function."

        self.end_unit(self.name)

    def start_function(self, name):

        "Start the function having the given 'name'."

        print >>self.out, "__attr %s(__attr __args[])" % encode_function_pointer(name)
        print >>self.out, "{"
        self.indent += 1

        # Obtain local names from parameters.

        parameters = self.importer.function_parameters[name]
        locals = self.importer.function_locals[name].keys()
        names = []

        for n in locals:

            # Filter out special names and parameters. Note that self is a local
            # regardless of whether it originally appeared in the parameters or
            # not.

            if n.startswith("$l") or n in parameters or n == "self":
                continue
            names.append(encode_path(n))

        # Emit required local names.

        if names:
            names.sort()
            self.writeline("__attr %s;" % ", ".join(names))

        self.write_parameters(name)
        self.start_unit()

    def end_function(self, name):

        "End the function having the given 'name'."

        self.end_unit(name)
        print >>self.out

    def write_temporaries(self, name):

        "Write temporary storage employed by 'name'."

        # Provide space for the given number of targets.

        if self.uses_temp(name, "__tmp_targets"):
            targets = self.importer.function_targets.get(name)
            self.writeline("__attr __tmp_targets[%d];" % targets)

        # Add temporary variable usage details.

        if self.uses_temp(name, "__tmp_context"):
            self.writeline("__ref __tmp_context;")
        if self.uses_temp(name, "__tmp_value"):
            self.writeline("__ref __tmp_value;")
        if self.uses_temp(name, "__tmp_target_value"):
            self.writeline("__ref __tmp_target_value;")
        if self.uses_temp(name, "__tmp_result"):
            self.writeline("__attr __tmp_result;")

        module = self.importer.get_module(self.name)

        if name in module.exception_namespaces:
            self.writeline("__exc __tmp_exc;")

    def write_parameters(self, name):

        """
        For the function having the given 'name', write definitions of
        parameters found in the arguments array.
        """

        parameters = self.importer.function_parameters[name]

        # Generate any self reference.

        if self.is_method(name):
            self.writeline("__attr * const self = &__args[0];")

        # Generate aliases for the parameters.

        for i, parameter in enumerate(parameters):
            self.writeline("__attr * const %s = &__args[%d];" % (encode_path(parameter), i+1))

    def start_if(self, first, test_ref):
        self.writestmt("%sif (__BOOL(%s))" % (not first and "else " or "", test_ref))
        self.writeline("{")
        self.indent += 1

    def end_if(self):
        self.indent -= 1
        self.writeline("}")

    def start_else(self):
        self.writeline("else")
        self.writeline("{")
        self.indent += 1

    def end_else(self):
        self.indent -= 1
        self.writeline("}")

    def statement(self, expr):
        s = str(expr)
        if s:
            self.writestmt("%s;" % s)

    def statements(self, results):
        for result in results:
            self.statement(result)

    def writeline(self, s):
        print >>self.out, "%s%s" % (self.pad(), self.indenttext(s, self.indent + 1))

    def writestmt(self, s):
        print >>self.out
        self.writeline(s)

    def write_comment(self, s):
        self.writestmt("/* %s */" % s)

    def pad(self, extra=0):
        return (self.indent + extra) * self.tabstop

    def indenttext(self, s, levels):
        lines = s.split("\n")
        out = [lines[0]]
        for line in lines[1:]:
            out.append(levels * self.tabstop + line)
            if line.endswith("("):
                levels += 1
            elif line.startswith(")"):
                levels -= 1
        return "\n".join(out)

# vim: tabstop=4 expandtab shiftwidth=4
