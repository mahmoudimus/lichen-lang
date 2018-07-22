#!/usr/bin/env python

"""
Translate programs.

Copyright (C) 2015, 2016, 2017, 2018 Paul Boddie <paul@boddie.org.uk>

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

from common import AccessLocation, CommonModule, CommonOutput, Location, \
                   first, get_builtin_class, init_item, is_newer, \
                   predefined_constants
from encoders import encode_access_instruction, encode_access_instruction_arg, \
                     encode_function_pointer, encode_literal_instantiator, \
                     encode_instantiator_pointer, encode_path, encode_symbol, \
                     encode_type_attribute, is_type_attribute, \
                     type_ops, typename_ops
from errors import InspectError, TranslateError
from os.path import exists, join
from os import makedirs
from referencing import Reference, combine_types
from results import Result
from transresults import TrConstantValueRef, TrInstanceRef, \
                         TrLiteralSequenceRef, TrResolvedNameRef, \
                         AliasResult, AttrResult, Expression, InstantiationResult, \
                         InvocationResult, LogicalOperationResult, \
                         LogicalResult, NegationResult, PredefinedConstantRef, \
                         ReturnRef
from StringIO import StringIO
import compiler
import sys

class Translator(CommonOutput):

    "A program translator."

    def __init__(self, importer, deducer, optimiser, output):
        self.importer = importer
        self.deducer = deducer
        self.optimiser = optimiser
        self.output = output

    def to_output(self, reset=False, debug=False, gc_sections=False):

        "Write a program to the configured output directory."

        # Make a directory for the final sources.

        output = join(self.output, "src")

        if not exists(output):
            makedirs(output)

        # Clean the output directory of irrelevant data.

        self.check_output("debug=%r gc_sections=%r" % (debug, gc_sections))

        for module in self.importer.modules.values():
            output_filename = join(output, "%s.c" % module.name)

            # Do not generate modules in the native package. They are provided
            # by native functionality source files.

            parts = module.name.split(".")

            if parts[0] != "native" and \
               (reset or is_newer(module.filename, output_filename)):

                tm = TranslatedModule(module.name, self.importer, self.deducer, self.optimiser)
                tm.translate(module.filename, output_filename)



def make_expression(expr):

    "Make a new expression from the existing 'expr'."

    if isinstance(expr, Result):
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
        self.in_parameter_list = False

        # Exception raising adjustments.

        self.in_try_finally = False
        self.in_try_except = False

        # Attribute access and accessor counting.

        self.attr_accesses = {}
        self.attr_accessors = {}

        # Special variable usage.

        self.temp_usage = {}

        # Initialise some data used for attribute access generation.

        self.init_substitutions()

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
            self.max_function_target = 0
            self.context_index = 0
            self.max_context_index = 0
            self.accessor_index = 0
            self.max_accessor_index = 0
            self.start_module()
            self.process_structure(node)
            self.end_module()

    def process_structure(self, node):

        "Process the given 'node' or result."

        # Handle processing requests on results.

        if isinstance(node, Result):
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
        name = name_ref and self.get_name_for_tracking(name_ref.name, name_ref) or None

        location = self.get_access_location(name, self.attrs)
        refs = self.get_referenced_attributes(location)

        # Generate access instructions.

        subs = {
            "<expr>" : attr_expr,
            "<name>" : attr_expr,
            "<assexpr>" : self.in_assignment,
            }

        subs.update(self.temp_subs)
        subs.update(self.op_subs)

        output = []
        substituted = set()

        # The context set or retrieved will be that used by any enclosing
        # invocation.

        accessor_index = self.accessor_index
        context_index = self.context_index
        context_identity = None
        context_identity_verified = False
        final_identity = None
        accessor_test = False
        accessor_stored = False

        # Obtain encoded versions of each instruction, accumulating temporary
        # variables.

        for instruction in self.deducer.access_instructions[location]:

            # Intercept a special instruction identifying the context.

            if instruction[0] in ("<context_identity>", "<context_identity_verified>"):
                context_identity, _substituted = \
                    encode_access_instruction_arg(instruction[1], subs, instruction[0],
                                                  accessor_index, context_index)
                context_identity_verified = instruction[0] == "<context_identity_verified>"
                continue

            # Intercept a special instruction identifying the target. The value
            # is not encoded since it is used internally.

            elif instruction[0] == "<final_identity>":
                final_identity = instruction[1]
                continue

            # Modify test instructions.

            elif instruction[0] in typename_ops or instruction[0] in type_ops:
                instruction = ("__to_error", instruction)
                accessor_test = True

            # Intercept accessor storage.

            elif instruction[0] == "<set_accessor>":
                accessor_stored = True

            # Collect the encoded instruction, noting any temporary variables
            # required by it.

            encoded, _substituted = encode_access_instruction(instruction, subs,
                                        accessor_index, context_index)
            output.append(encoded)
            substituted.update(_substituted)

        # Record temporary name usage.

        for sub in substituted:
            if self.temp_subs.has_key(sub):
                self.record_temp(self.temp_subs[sub])

        # Get full final identity details.

        if final_identity and not refs:
            refs = set([self.importer.identify(final_identity)])

        del self.attrs[0]
        return AttrResult(output, refs, location,
                          context_identity, context_identity_verified,
                          accessor_test, accessor_stored)

    def init_substitutions(self):

        """
        Initialise substitutions, defining temporary variable mappings, some of
        which are also used as substitutions, together with operation mappings
        used as substitutions in instructions defined by the optimiser.
        """

        self.temp_subs = {

            # Substitutions used by instructions.

            "<private_context>" : "__tmp_private_context",
            "<target_accessor>" : "__tmp_target_value",

            # Mappings to be replaced by those given below.

            "<accessor>" : "__tmp_values",
            "<context>" : "__tmp_contexts",
            "<test_context_revert>" : "__tmp_contexts",
            "<test_context_static>" : "__tmp_contexts",
            "<set_context>" : "__tmp_contexts",
            "<set_private_context>" : "__tmp_private_context",
            "<set_accessor>" : "__tmp_values",
            "<set_target_accessor>" : "__tmp_target_value",
            }

        self.op_subs = {
            "<accessor>" : "__get_accessor",
            "<context>" : "__get_context",
            "<test_context_revert>" : "__test_context_revert",
            "<test_context_static>" : "__test_context_static",
            "<set_context>" : "__set_context",
            "<set_private_context>" : "__set_private_context",
            "<set_accessor>" : "__set_accessor",
            "<set_target_accessor>" : "__set_target_accessor",
            }

    def get_referenced_attributes(self, location):

        """
        Convert 'location' to the form used by the deducer and retrieve any
        identified attributes.
        """

        # Determine whether any deduced references refer to the accessed
        # attribute.

        attrnames = location.attrnames
        attrnames = attrnames and attrnames.split(".")
        remaining = attrnames and len(attrnames) > 1

        access_location = self.deducer.const_accesses.get(location)

        if remaining and not access_location:
            return set()

        return self.deducer.get_references_for_access(access_location or location)

    def get_referenced_attribute_invocations(self, location):

        """
        Convert 'location' to the form used by the deducer and retrieve any
        identified attribute invocation details.
        """

        access_location = self.deducer.const_accesses.get(location)
        return self.deducer.reference_invocations_unsuitable.get(access_location or location)

    def get_accessor_kinds(self, location):

        "Return the accessor kinds for 'location'."

        return self.deducer.accessor_kinds.get(location)

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
        return AccessLocation(path, name, attrnames, access_number)

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

        version = self.get_accessor_number(path, name)
        self.update_accessor_number(path, name)
        return Location(path, name, None, version)

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
            self.process_assignment_for_object(n.name,
                make_expression("__ATTRVALUE(&%s)" % encode_path(class_name)))

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
                    encode_path(class_name), name,
                    encode_path(parent), attrname
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
        self.max_function_target = 0
        self.context_index = 0
        self.max_context_index = 0
        self.accessor_index = 0
        self.max_accessor_index = 0

        # Volatile locals for exception handling.

        self.volatile_locals = set()

        # Process any guards defined for the parameters.

        for name in self.importer.function_parameters.get(function_name):
            self.generate_guard(name)

        # Also support self in methods, since some mix-in methods may only work
        # with certain descendant classes.

        if self.in_method():
            self.generate_guard("self")

        # Make assignments for .name entries in the parameters, provided this is
        # a method.

        if self.in_method():
            for name in self.importer.function_attr_initialisers.get(function_name) or []:
                self.process_assignment_node(
                    compiler.ast.AssAttr(compiler.ast.Name("self"), name, "OP_ASSIGN"),
                    compiler.ast.Name(name))

        # Produce the body and any additional return statement.

        expr = self.process_structure_node(n.code) or \
               self.in_method() and \
                   function_name.rsplit(".", 1)[-1] == "__init__" and \
                   TrResolvedNameRef("self", self.importer.function_locals[function_name]["self"]) or \
               PredefinedConstantRef("None")

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
                argstr = encode_path(encode_type_attribute(ref.get_origin()))
            else:
                return

            # Write a test that raises a TypeError upon failure.

            self.writestmt("if (!__test_%s_%s(__VALUE(%s), %s)) __raise_type_error();" % (
                guard, guard_type, encode_path(name), argstr))

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
                make_expression("__ATTRVALUE(&%s)" % encode_path(objpath)))

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
        else:
            instance_name = "__VALUE(%s)" % instance_name

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

        print >>self.out

    def process_invocation_node(self, n):

        "Process the given invocation node 'n'."

        # Process the expression.

        expr = self.process_structure_node(n.node)

        # Obtain details of the invocation expression.

        objpath = expr.get_origin()
        location = expr.access_location()
        refs = expr.references()

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
        have_access_context = isinstance(expr, AttrResult)

        # The context identity is merely the thing providing the context.
        # A verified context is one that does not need further testing for
        # suitability.

        context_identity = have_access_context and expr.context()
        context_verified = have_access_context and expr.context_verified()

        # The presence of any test operations in the accessor expression.
        # With such operations present, the expression cannot be eliminated.

        tests_accessor = have_access_context and expr.tests_accessor()
        stores_accessor = have_access_context and expr.stores_accessor()

        # Parameter details and parameter list dimensions.

        parameters = None
        num_parameters = None
        num_defaults = None

        # Obtain details of the callable and of its parameters.

        # Literals may be instantiated specially.

        if expr.is_name() and expr.name.startswith("$L") and objpath:
            instantiation = literal_instantiation = objpath
            target = encode_literal_instantiator(objpath)
            context_required = False

        # Identified targets employ function pointers directly.

        elif objpath:
            parameters = self.importer.function_parameters.get(objpath)
            function_defaults = self.importer.function_defaults.get(objpath)
            num_parameters = parameters and len(parameters) or 0
            num_defaults = function_defaults and len(function_defaults) or 0

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

                accessor_kinds = location and self.get_accessor_kinds(location)

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
            if location:
                attrnames = location.attrnames
                attrname = attrnames and attrnames.rsplit(".", 1)[-1]

                # Determine common aspects of any identifiable targets.

                if attrname or refs:
                    all_params = set()
                    all_defaults = set()
                    min_params = set()
                    max_params = set()

                    # Employ references from the expression or find all
                    # possible attributes for the given attribute name.

                    refs = refs or self.get_attributes_for_attrname(attrname)

                    # Obtain parameters and defaults for each possible target.

                    for ref in refs:
                        origin = ref.get_origin()
                        params = self.importer.function_parameters.get(origin)

                        defaults = self.importer.function_defaults.get(origin)
                        if defaults is not None:
                            all_defaults.add(tuple(defaults))

                        if params is not None:
                            all_params.add(tuple(params))
                            min_params.add(len(params) - (defaults and len(defaults) or 0))
                            max_params.add(len(params))
                        else:
                            refs = set()
                            break

                    # Where the parameters and defaults are always the same,
                    # permit populating them in advance.

                    if refs:
                        if self.uses_keyword_arguments(n):
                            if len(all_params) == 1 and (not all_defaults or len(all_defaults) == 1):
                                parameters = first(all_params)
                                function_defaults = all_defaults and first(all_defaults) or []
                                num_parameters = parameters and len(parameters) or 0
                                num_defaults = function_defaults and len(function_defaults) or 0
                        else:
                            if len(min_params) == 1 and len(max_params) == 1:
                                num_parameters = first(max_params)
                                num_defaults = first(max_params) - first(min_params)

            # Some information about the target may be available and be used to
            # provide warnings about argument compatibility.

            if self.importer.give_warning("args"):
                unsuitable = self.get_referenced_attribute_invocations(location)

                if unsuitable:
                    for ref in unsuitable:
                        _objpath = ref.get_origin()
                        print >>sys.stderr, \
                            "In %s, at line %d, inappropriate number of " \
                            "arguments given. Need %d arguments to call %s." % (
                            self.get_namespace_path(), n.lineno,
                            len(self.importer.function_parameters[_objpath]),
                            _objpath)

        # Logical statement about available parameter information.

        known_parameters = num_parameters is not None

        # The source of context information: target or temporary.

        need_context_target = context_required and not have_access_context

        need_context_stored = context_required and context_identity and \
                              context_identity.startswith("__get_context")

        # Determine any readily-accessible target identity.

        target_named = expr.is_name() and str(expr) or None
        target_identity = target or target_named

        # Use of target information to populate defaults.

        defaults_target_var = not (parameters and function_defaults is not None) and \
                              known_parameters and len(n.args) < num_parameters

        # Use of a temporary target variable in these situations:
        #
        # A target provided by an expression needed for defaults.
        #
        # A target providing the context but not using a name to do so.
        #
        # A target expression involving the definition of a context which may
        # then be evaluated and stored to ensure that the context is available
        # during argument evaluation.
        #
        # An expression featuring an accessor test.

        need_target_stored = defaults_target_var and not target_identity or \
                             need_context_target and not target_identity or \
                             need_context_stored or \
                             tests_accessor and not target

        # Define stored target details.

        target_stored = "__tmp_targets[%d]" % self.function_target
        target_var = need_target_stored and target_stored or target_identity

        if need_target_stored:
            self.record_temp("__tmp_targets")

        if need_context_stored:
            self.record_temp("__tmp_contexts")

        if stores_accessor:
            self.record_temp("__tmp_values")

        # Arguments are presented in a temporary frame array with any context
        # always being the first argument. Where it would be unused, it may be
        # set to null.

        if context_required:
            if have_access_context:
                context_arg = context_identity
            else:
                context_arg = "__CONTEXT_AS_VALUE(%s)" % target_var
        else:
            context_arg = "__NULL"

        args = [context_arg]

        # Complete the array with null values, permitting tests for a complete
        # set of arguments.

        args += [None] * (num_parameters is None and len(n.args) or num_parameters is not None and num_parameters or 0)
        kwcodes = []
        kwargs = []

        # Any invocations in the arguments will store target details in a
        # different location.

        function_target = self.function_target
        context_index = self.context_index
        accessor_index = self.accessor_index

        if need_target_stored:
            self.next_target()

        if need_context_stored:
            self.next_context()

        if stores_accessor:
            self.next_accessor()

        in_parameter_list = self.in_parameter_list
        self.in_parameter_list = True

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
                        encode_ppos(arg.name), encode_pcode(arg.name)))

            # Store non-keyword arguments in the argument list, rejecting
            # superfluous arguments.

            else:
                try:
                    args[i+1] = str(argexpr)
                except IndexError:
                    raise TranslateError("Too many arguments specified.",
                                         self.get_namespace_path(), n)

        # Reference the current target again.

        self.in_parameter_list = in_parameter_list

        if not self.in_parameter_list:
            self.function_target = function_target
            self.context_index = context_index
            self.accessor_index = accessor_index

        # Defaults are added to the frame where arguments are missing.

        if parameters and function_defaults is not None:

            # Visit each default and set any missing arguments. Where keyword
            # arguments have been used, the defaults must be inspected and, if
            # necessary, inserted into gaps in the argument list.

            for i, (argname, default) in enumerate(function_defaults):
                argnum = parameters.index(argname)
                if not args[argnum+1]:
                    args[argnum+1] = "__GETDEFAULT(%s, %d)" % (target_structure, i)

        elif known_parameters:

            # No specific parameter details are provided, but no keyword
            # arguments are used. Thus, defaults can be supplied using position
            # information only.

            i = len(n.args)
            pos = i - (num_parameters - num_defaults)
            while i < num_parameters:
                args[i+1] = "__GETDEFAULT(%s.value, %d)" % (target_var, pos)
                i += 1
                pos += 1

        # Test for missing arguments.

        if None in args:
            raise TranslateError("Not all arguments supplied.",
                                 self.get_namespace_path(), n)

        # Encode the arguments.

        # Where literal instantiation is occurring, add an argument indicating
        # the number of values. The context is excluded.

        if literal_instantiation:
            argstr = "%d, %s" % (len(args) - 1, ", ".join(args[1:]))
        else:
            argstr = ", ".join(args)

        kwargstr = kwargs and ("__ARGS(%s)" % ", ".join(kwargs)) or "0"
        kwcodestr = kwcodes and ("__KWARGS(%s)" % ", ".join(kwcodes)) or "0"

        # First, the invocation expression is presented.

        stages = []
        emit = stages.append

        # Assign and yield any stored target.
        # The context may be set in the expression.

        if need_target_stored:
            emit("%s = %s" % (target_var, expr))
            target_expr = target_var

        # Otherwise, retain the expression for later use.

        else:
            target_expr = str(expr)

        # Any specific callable is then obtained for invocation.

        if target:

            # An expression involving a test of the accessor providing the target.
            # This must be emitted in order to perform the test.

            if tests_accessor:
                emit(str(expr))

            emit(target)

        # Methods accessed via unidentified accessors are obtained for
        # invocation.

        elif function:
            if context_required:

                # Avoid further context testing if appropriate.

                if have_access_context and context_verified:
                    emit("__get_function_member(%s)" % target_expr)

                # Otherwise, test the context for the function/method.

                else:
                    emit("__get_function(%s, %s)" % (context_arg, target_expr))
            else:
                emit("_get_function_member(%s)" % target_expr)

        # With known parameters, the target can be tested.

        elif known_parameters:
            if self.always_callable(refs):
                if context_verified:
                    emit("__get_function_member(%s)" % target_expr)
                else:
                    emit("__get_function(%s, %s)" % (context_arg, target_expr))
            else:
                emit("__check_and_get_function(%s, %s)" % (context_arg, target_expr))

        # With a known target, the function is obtained directly and called.
        # By putting the invocation at the end of the final element in the
        # instruction sequence (the stages), the result becomes the result of
        # the sequence. Moreover, the parameters become part of the sequence
        # and thereby participate in a guaranteed evaluation order.

        if target or function or known_parameters:
            stages[-1] += "(%s)" % argstr
            if instantiation:
                return InstantiationResult(instantiation, stages)
            else:
                return InvocationResult(stages)

        # With unknown targets, the generic invocation function is applied to
        # the callable and argument collections.

        else:
            emit("__invoke(\n%s,\n%d, %d, %s, %s,\n%d, %s\n)" % (
                target_expr,
                self.always_callable(refs) and 1 or 0,
                len(kwargs), kwcodestr, kwargstr,
                len(args), "__ARGS(%s)" % argstr))
            return InvocationResult(stages)

    def next_target(self):

        "Allocate the next function target storage."

        self.function_target += 1
        self.max_function_target = max(self.function_target, self.max_function_target)

    def next_context(self):

        "Allocate the next context value storage."

        self.context_index += 1
        self.max_context_index = max(self.context_index, self.max_context_index)

    def next_accessor(self):

        "Allocate the next accessor value storage."

        self.accessor_index += 1
        self.max_accessor_index = max(self.accessor_index, self.max_accessor_index)

    def always_callable(self, refs):

        "Determine whether all 'refs' are callable."

        if not refs:
            return False

        for ref in refs:
            if not ref.has_kind("<function>") and not self.importer.get_attributes(ref, "__fn__"):
                return False

        return True

    def need_default_arguments(self, objpath, nargs):

        """
        Return whether any default arguments are needed when invoking the object
        given by 'objpath'.
        """

        parameters = self.importer.function_parameters.get(objpath)
        return nargs < len(parameters)

    def uses_keyword_arguments(self, n):

        "Return whether invocation node 'n' uses keyword arguments."

        for arg in enumerate(n.args):
            if isinstance(arg, compiler.ast.Keyword):
                return True

        return False

    def get_attributes_for_attrname(self, attrname):

        "Return a set of all attributes exposed by 'attrname'."

        usage = [(attrname, True, False)]
        class_types = self.deducer.get_class_types_for_usage(usage)
        instance_types = self.deducer.get_instance_types_for_usage(usage)
        module_types = self.deducer.get_module_types_for_usage(usage)
        attrs = set()

        for ref in combine_types(class_types, instance_types, module_types):
            attrs.update(self.importer.get_attributes(ref, attrname))

        return attrs

    def process_lambda_node(self, n):

        "Process the given lambda node 'n'."

        name = self.get_lambda_name()
        function_name = self.get_object_path(name)
        instance_name = "__get_accessor(%d)" % self.accessor_index

        defaults = self.process_function_defaults(n, name, function_name, instance_name)

        # Without defaults, produce an attribute referring to the function.

        if not defaults:
            return make_expression("__ATTRVALUE(&%s)" % encode_path(function_name))

        # With defaults, copy the function structure and set the defaults on the
        # copy.

        else:
            self.record_temp("__tmp_values")
            return make_expression("""\
(__set_accessor(%d, __ATTRVALUE(__COPY(&%s, sizeof(%s)))),
 %s,
 __get_accessor(%d))""" % (
                self.accessor_index,
                encode_path(function_name),
                encode_symbol("obj", function_name),
                ", ".join(defaults),
                self.accessor_index))

    def process_logical_node(self, n):

        "Process the given operator node 'n'."

        self.record_temp("__tmp_result")

        conjunction = isinstance(n, compiler.ast.And)
        results = []

        for node in n.nodes:
            results.append(self.process_structure_node(node))

        return LogicalOperationResult(results, conjunction)

    def process_name_node(self, n, expr=None):

        "Process the given name node 'n' with the optional assignment 'expr'."

        # Determine whether the name refers to a static external entity.

        if n.name in predefined_constants:
            return PredefinedConstantRef(n.name, expr)

        # Convert literal references, operator function names, and print
        # function names to references.

        elif n.name.startswith("$L") or n.name.startswith("$op") or \
             n.name.startswith("$seq") or n.name.startswith("$print"):

            ref, paths = self.importer.get_module(self.name).special[n.name]
            return TrResolvedNameRef(n.name, ref)

        # Get the appropriate name for the name reference, using the same method
        # as in the inspector.

        path = self.get_namespace_path()
        objpath = self.get_object_path(n.name)

        # Determine any assigned globals.

        globals = self.importer.get_module(self.name).scope_globals.get(path)

        # Explicitly declared globals.

        if globals and n.name in globals:
            objpath = self.get_global_path(n.name)
            is_global = True

        # Implicitly referenced globals in functions.

        elif self.in_function:
            is_global = n.name not in self.importer.function_locals[path]

        # Implicitly referenced globals elsewhere.

        else:
            namespace = self.importer.identify(path)
            is_global = not self.importer.get_attributes(namespace, n.name)

        # Get the static identity of the name.

        ref = self.importer.identify(objpath)
        if ref and not ref.get_name():
            ref = ref.alias(objpath)

        # Obtain any resolved names for non-assignment names.

        if not expr and not ref and self.in_function:
            locals = self.importer.function_locals.get(path)
            ref = locals and locals.get(n.name)

        # Find any invocation or alias details.

        name = self.get_name_for_tracking(n.name, is_global=is_global)
        location = not expr and self.get_access_location(name) or None

        # Mark any local assignments as volatile in exception blocks.

        if expr and self.in_function and not is_global and self.in_try_except:
            self.make_volatile(n.name)

        # Qualified names are used for resolved static references or for
        # static namespace members. The reference should be configured to return
        # such names.

        name_ref = TrResolvedNameRef(n.name, ref, expr=expr, is_global=is_global,
                                     location=location)
        return not expr and self.get_aliases(name_ref) or name_ref

    def get_aliases(self, name_ref):

        "Return alias references for the given 'name_ref'."

        location = name_ref.access_location()
        accessor_locations = self.deducer.access_index.get(location)

        if not accessor_locations:
            return None

        refs = set()

        for accessor_location in accessor_locations:
            alias_refs = self.deducer.referenced_objects.get(accessor_location)
            if alias_refs:
                refs.update(alias_refs)

        if refs:
            return AliasResult(name_ref, refs, location)
        else:
            return None

    def make_volatile(self, name):

        "Record 'name' as volatile in the current namespace."

        self.volatile_locals.add(name)

    def process_not_node(self, n):

        "Process the given operator node 'n'."

        return self.make_negation(self.process_structure_node(n.expr))

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
        print >>self.out

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
        print >>self.out

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

            # Emit a negated test of the continuation condition.

            self.start_if(True, self.make_negation(test))
            if n.else_:
                self.process_structure_node(n.else_)
            self.writestmt("break;")
            self.end_if()

        in_conditional = self.in_conditional
        self.in_conditional = True
        self.process_structure_node(n.body)
        self.in_conditional = in_conditional

        self.indent -= 1
        self.writeline("}")
        print >>self.out

    # Special variable usage.

    def get_temp_path(self):

        """
        Return the appropriate namespace path for temporary names in the current
        namespace.
        """

        if self.in_function:
            return self.get_namespace_path()
        else:
            return self.name

    def record_temp(self, name):

        """
        Record the use of the temporary 'name' in the current namespace. At the
        class or module level, the temporary name is associated with the module,
        since the variable will then be allocated in the module's own main
        program.
        """

        path = self.get_temp_path()

        init_item(self.temp_usage, path, list)
        self.temp_usage[path].append(name)

    def remove_temps(self, names):

        """
        Remove 'names' from temporary storage allocations, each instance
        removing each request for storage.
        """

        path = self.get_temp_path()

        for name in names:
            if self.uses_temp(path, name):
                self.temp_usage[path].remove(name)

    def uses_temp(self, path, name):

        """
        Return whether the given namespace 'path' employs a temporary variable
        with the given 'name'. Note that 'path' should only be a module or a
        function or method, not a class.
        """

        return self.temp_usage.has_key(path) and name in self.temp_usage[path]

    def make_negation(self, expr):

        "Return a negated form of 'expr'."

        result = NegationResult(expr)

        # Negation discards the temporary results of its operand.

        temps = expr.discards_temporary()
        if temps:
            self.remove_temps(temps)

        return result

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

    def end_unit(self):

        "Restore the output stream."

        out = self.out
        self.out = self.out_toplevel
        return out

    def flush_unit(self, name, out):

        "Add declarations and generated code."

        self.write_temporaries(name)
        print >>self.out
        out.seek(0)
        self.out.write(out.read())

    def start_module(self):

        "Write the start of each module's main function."

        print >>self.out, "void __main_%s()" % encode_path(self.name)
        print >>self.out, "{"
        self.indent += 1

        # Define temporary variables, excluded from the module structure itself.

        tempnames = []

        for n in self.importer.all_module_attrs[self.name]:
            if n.startswith("$t"):
                tempnames.append(encode_path(n))

        if tempnames:
            tempnames.sort()
            self.writeline("__attr %s;" % ", ".join(tempnames))

        self.start_unit()

    def end_module(self):

        "End each module by closing its main function."

        out = self.end_unit()
        self.flush_unit(self.name, out)

        self.indent -= 1
        print >>self.out, "}"

    def start_function(self, name):

        "Start the function having the given 'name'."

        self.indent += 1

        self.start_unit()

    def end_function(self, name):

        "End the function having the given 'name'."

        out = self.end_unit()

        # Write the signature at the top indentation level.

        self.indent -= 1
        self.write_parameters(name)
        print >>self.out, "{"

        # Obtain local names from parameters.

        parameters = self.importer.function_parameters[name]
        locals = self.importer.function_locals[name].keys()
        names = []
        volatile_names = []

        for n in locals:

            # Filter out special names and parameters. Note that self is a local
            # regardless of whether it originally appeared in the parameters or
            # not.

            if n.startswith("$l") or n in parameters or n == "self":
                continue
            if n in self.volatile_locals:
                volatile_names.append(encode_path(n))
            else:
                names.append(encode_path(n))

        # Emit required local names at the function indentation level.

        self.indent += 1

        if names:
            names.sort()
            self.writeline("__attr %s;" % ", ".join(names))

        if volatile_names:
            volatile_names.sort()
            self.writeline("volatile __attr %s;" % ", ".join(volatile_names))

        self.flush_unit(name, out)

        self.indent -= 1
        print >>self.out, "}"
        print >>self.out

    def write_parameters(self, name):

        """
        For the function having the given 'name', write definitions of
        parameters found in the arguments array.
        """

        # Generate any self reference.

        l = []

        if self.is_method(name):
            l.append("__attr self")
        else:
            l.append("__attr __self")

        # Generate aliases for the parameters.

        for parameter in self.importer.function_parameters[name]:
            l.append("%s__attr %s" % (
                parameter in self.volatile_locals and "volatile " or "",
                encode_path(parameter)))

        self.writeline("__attr %s(%s)" % (
            encode_function_pointer(name), ", ".join(l)))

    def write_temporaries(self, name):

        "Write temporary storage employed by 'name'."

        # Provide space for the recorded number of temporary variables.

        if self.uses_temp(name, "__tmp_targets"):
            self.writeline("__attr __tmp_targets[%d];" % self.max_function_target)

        if self.uses_temp(name, "__tmp_contexts"):
            self.writeline("__attr __tmp_contexts[%d];" % self.max_context_index)

        if self.uses_temp(name, "__tmp_values"):
            self.writeline("__attr __tmp_values[%d];" % self.max_accessor_index)

        # Add temporary variable usage details.

        if self.uses_temp(name, "__tmp_private_context"):
            self.writeline("__attr __tmp_private_context;")
        if self.uses_temp(name, "__tmp_target_value"):
            self.writeline("__attr __tmp_target_value;")
        if self.uses_temp(name, "__tmp_result"):
            self.writeline("__attr __tmp_result;")

        module = self.importer.get_module(self.name)

        if name in module.exception_namespaces:
            self.writeline("__exc __tmp_exc;")

    def start_if(self, first, test_ref):
        statement = "%sif" % (not first and "else " or "")

        # Consume logical results directly.

        if isinstance(test_ref, LogicalResult):
            self.writeline("%s %s" % (statement, test_ref.apply_test()))
            temps = test_ref.discards_temporary()
            if temps:
                self.remove_temps(temps)
        else:
            self.writeline("%s (__BOOL(%s))" % (statement, test_ref))

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
