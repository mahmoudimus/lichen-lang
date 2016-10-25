#!/usr/bin/env python

"""
Translate programs.

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

from common import *
from encoders import *
from os.path import exists, join
from os import makedirs
import compiler
import results

class Translator(CommonOutput):

    "A program translator."

    def __init__(self, importer, deducer, optimiser, output):
        self.importer = importer
        self.deducer = deducer
        self.optimiser = optimiser
        self.output = output

    def to_output(self):
        output = join(self.output, "src")

        if not exists(output):
            makedirs(output)

        self.check_output()

        for module in self.importer.modules.values():
            tm = TranslatedModule(module.name, self.importer, self.deducer, self.optimiser)
            tm.translate(module.filename, join(output, "%s.c" % module.name))

# Classes representing intermediate translation results.

class TranslationResult:

    "An abstract translation result mix-in."

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

    def __str__(self):

        "Return an output representation of the referenced name."

        # Use any alias in preference to the origin of the name.

        name = self.get_name()

        # Use any static origin in preference to any alias.
        # For sources, any identified static origin will be constant and thus
        # usable directly. For targets, no constant should be assigned and thus
        # the alias (or any plain name) will be used.

        origin = self.static() and self.get_origin()
        name = origin and encode_path(origin) or name and encode_path(name) or encode_path(self.name)

        # Assignments.

        if self.expr:

            # Eliminate assignments between constants.

            if self.static() and isinstance(self.expr, results.ResolvedNameRef) and self.expr.static():
                return ""
            else:
                return "%s = %s" % (name, self.expr)

        # Expressions.

        else:
            return name

class TrConstantValueRef(results.ConstantValueRef, TranslationResult):

    "A constant value reference in the translation."

    def __str__(self):
        return encode_literal_constant(self.number)

class TrLiteralSequenceRef(results.LiteralSequenceRef, TranslationResult):

    "A reference representing a sequence of values."

    def __str__(self):
        return str(self.node)

class AttrResult(Expression, TranslationResult):

    "A translation result for an attribute access."

    def __init__(self, s, refs):
        Expression.__init__(self, s)
        self.refs = refs

    def get_origin(self):
        return self.refs and len(self.refs) == 1 and first(self.refs).get_origin()

    def has_kind(self, kinds):
        if not self.refs:
            return False
        for ref in self.refs:
            if ref.has_kind(kinds):
                return True
        return False

    def __repr__(self):
        return "AttrResult(%r, %r)" % (self.s, self.get_origin())

class PredefinedConstantRef(AttrResult):

    "A predefined constant reference."

    def __init__(self, value):
        self.value = value

    def __str__(self):
        if self.value in ("False", "True"):
            return encode_path("__builtins__.bool.%s" % self.value)
        elif self.value == "None":
            return encode_path("__builtins__.none.%s" % self.value)
        elif self.value == "NotImplemented":
            return encode_path("__builtins__.notimplemented.%s" % self.value)
        else:
            return self.value

    def __repr__(self):
        return "PredefinedConstantRef(%r)" % self.value

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

        self.out = None
        self.indent = 0
        self.tabstop = "    "

        # Recorded namespaces.

        self.namespaces = []
        self.in_conditional = False

        # Attribute access counting.

        self.attr_accesses = {}

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

        self.out = open(output_filename, "w")
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

    def get_builtin(self, name):
        return self.importer.get_object("__builtins__.%s" % name)

    def in_method(self, path):
        class_name, method_name = path.rsplit(".", 1)
        return self.importer.classes.has_key(class_name) and class_name

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

    def get_literal_instance(self, n, name):

        """
        For node 'n', return a reference for the type of the given 'name'.
        """

        ref = self.get_builtin(name)

        if name in ("dict", "list", "tuple"):
            return self.process_literal_sequence_node(n, name, ref, TrLiteralSequenceRef)
        else:
            path = self.get_namespace_path()
            local_number = self.importer.all_constants[path][n.value]
            constant_name = "$c%d" % local_number
            objpath = self.get_object_path(constant_name)
            number = self.optimiser.constant_numbers[objpath]
            return TrConstantValueRef(constant_name, ref.instance_of(), n.value, number)

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
            self.start_module()
            self.process_structure(node)
            self.end_module()

    def process_structure(self, node):

        "Process the given 'node' or result."

        if isinstance(node, results.Result):
            return node
        else:
            return CommonModule.process_structure(self, node)

    def process_structure_node(self, n):

        "Process the individual node 'n'."

        # Plain statements emit their expressions.

        if isinstance(n, compiler.ast.Discard):
            expr = self.process_structure_node(n.expr)
            self.statement(expr)

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

        # Assignments within non-Assign nodes.
        # NOTE: Cover all possible nodes employing these.

        elif isinstance(n, compiler.ast.AssName):
            self.process_assignment_node(n, compiler.ast.Name("$temp"))

        elif isinstance(n, compiler.ast.AssAttr):
            self.process_attribute_access(n)

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

        elif isinstance(n, compiler.ast.Return):
            expr = self.process_structure_node(n.value)
            if expr:
                self.writestmt("return %s;" % expr)
            else:
                self.writestmt("return;")

        # Invocations.

        elif isinstance(n, compiler.ast.CallFunc):
            return self.process_invocation_node(n)

        elif isinstance(n, compiler.ast.Keyword):
            return self.process_structure_node(n.expr)

        # Constant usage.

        elif isinstance(n, compiler.ast.Const):
            return self.get_literal_instance(n, n.value.__class__.__name__)

        elif isinstance(n, compiler.ast.Dict):
            return self.get_literal_instance(n, "dict")

        elif isinstance(n, compiler.ast.List):
            return self.get_literal_instance(n, "list")

        elif isinstance(n, compiler.ast.Tuple):
            return self.get_literal_instance(n, "tuple")

        # All other nodes are processed depth-first.

        else:
            self.process_structure(n)

    def process_assignment_node(self, n, expr):

        "Process the individual node 'n' to be assigned the contents of 'expr'."

        # Names and attributes are assigned the entire expression.

        if isinstance(n, compiler.ast.AssName):
            name_ref = self.process_name_node(n, self.process_structure_node(expr))
            self.statement(name_ref)

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

        """
        Process the given attribute access node 'n'.

        Where a name is provided, a single access should be recorded
        involving potentially many attributes, thus providing a path to an
        object. The remaining attributes are then accessed dynamically.
        The remaining accesses could be deduced and computed, but they would
        also need to be tested.

        Where no name is provided, potentially many accesses should be
        recorded, one per attribute name. These could be used to provide
        computed accesses, but the accessors would need to be tested in each
        case.
        """

        # Obtain any completed chain and return the reference to it.

        attr_expr = self.process_attribute_chain(n)
        if self.have_access_expression(n):
            return attr_expr

        # Where the start of the chain of attributes has been reached, process
        # the complete access.

        name_ref = attr_expr and attr_expr.is_name() and attr_expr
        name = name_ref and name_ref.name or None

        location = self.get_access_location(name)
        refs = self.get_referenced_attributes(location)

        # Generate access instructions.

        subs = {
            "<expr>" : str(attr_expr),
            "<assexpr>" : str(self.in_assignment),
            "<context>" : "__tmp_context",
            "<accessor>" : "__tmp_value",
            }

        output = []

        for instruction in self.optimiser.access_instructions[location]:
            output.append(encode_access_instruction(instruction, subs))

        if len(output) == 1:
            out = output[0]
        else:
            out = "(\n%s\n)" % ",\n".join(output)

        del self.attrs[0]
        return AttrResult(out, refs)

    def get_referenced_attributes(self, location):

        """
        Convert 'location' to the form used by the deducer and retrieve any
        identified attribute.
        """

        access_location = self.deducer.const_accesses.get(location)
        refs = []
        for attrtype, objpath, attr in self.deducer.referenced_attrs[access_location or location]:
            refs.append(attr)
        return refs

    def get_access_location(self, name):

        """
        Using the current namespace and the given 'name', return the access
        location.
        """

        path = self.get_path_for_access()

        # Get the location used by the deducer and optimiser and find any
        # recorded access.

        attrnames = ".".join(self.attrs)
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
            init_item(self.attr_accesses[path], access, lambda: 1)

    def process_class_node(self, n):

        "Process the given class node 'n'."

        self.enter_namespace(n.name)

        if self.have_object():
            class_name = self.get_namespace_path()
            self.write_comment("Class: %s" % class_name)

            self.process_structure(n)

        self.exit_namespace()

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

        expr = self.process_structure_node(n.code)
        if expr:
            self.writestmt("return %s;" % expr)

        self.in_conditional = in_conditional

        self.end_function()

    def process_function_node(self, n):

        """
        Process the given function, lambda, if expression or list comprehension
        node 'n', generating any initialisation statements.
        """

        # Where a function is declared conditionally, use a separate name for
        # the definition, and assign the definition to the stated name.

        if self.in_conditional or self.in_function:
            original_name = n.name
            name = self.get_lambda_name()
        else:
            original_name = None
            name = n.name

        # Obtain details of the defaults.

        defaults = self.process_function_defaults(n, name, self.get_object_path(name))
        if defaults:
            for default in defaults:
                self.writeline("%s;" % default)

        # Where a function is set conditionally, assign the name.

        if original_name:
            self.process_assignment_for_function(original_name, name)

    def process_function_defaults(self, n, name, instance_name):

        """
        Process the given function or lambda node 'n', initialising defaults
        that are dynamically set. The given 'name' indicates the name of the
        function. The given 'instance_name' indicates the name of any separate
        instance of the function created to hold the defaults.

        Return a list of operations setting defaults on a function instance.
        """

        function_name = self.get_object_path(name)
        function_defaults = self.importer.function_defaults.get(function_name)
        if not function_defaults:
            return None

        # Determine whether any unidentified defaults are involved.

        need_defaults = [argname for argname, default in function_defaults if default.has_kind("<var>")]
        if not need_defaults:
            return None

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

            if name_ref:
                defaults.append("__SETDEFAULT(%s, %s, %s)" % (encode_path(instance_name), i, name_ref))

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
        target = None

        # Obtain details of the callable.

        if objpath:
            parameters = self.importer.function_parameters.get(objpath)
            if expr.has_kind("<class>"):
                target = encode_instantiator_pointer(objpath)
            elif expr.has_kind("<function>"):
                target = encode_function_pointer(objpath)
        else:
            parameters = None

        stages = []

        # First, the invocation target is presented.

        stages.append("__tmp_target = %s" % expr)

        # Arguments are presented in a temporary frame array with any context
        # always being the first argument (although it may be set to null for
        # invocations where it would be unused).

        args = ["__CONTEXT_AS_VALUE(__tmp_target)"]
        args += [None] * (not parameters and len(n.args) or parameters and len(parameters) or 0)
        kwcodes = []
        kwargs = []

        for i, arg in enumerate(n.args):
            argexpr = self.process_structure_node(arg)

            # Store a keyword argument, either in the argument list or
            # in a separate keyword argument list for subsequent lookup.

            if isinstance(arg, compiler.ast.Keyword):

                # With knowledge of the target, store the keyword
                # argument directly.

                if parameters:
                    argnum = parameters.index(arg.name)
                    args[argnum+1] = str(argexpr)

                # Otherwise, store the details in a separate collection.

                else:
                    kwargs.append(str(argexpr))
                    kwcodes.append("{%s, %s}" % (
                        encode_symbol("ppos", arg.name),
                        encode_symbol("pcode", arg.name)))

            else:
                args[i+1] = str(argexpr)

        # Defaults are added to the frame where arguments are missing.

        if parameters:
            function_defaults = self.importer.function_defaults.get(objpath)
            if function_defaults:

                # Visit each default and set any missing arguments.

                for i, (argname, default) in enumerate(function_defaults):
                    argnum = parameters.index(argname)
                    if not args[argnum+1]:
                        args[argnum+1] = "__GETDEFAULT(%s, %d)" % (target, i)

        argstr = "__ARGS(%s)" % ", ".join(args)
        kwargstr = kwargs and ("__ARGS(%s)" % ", ".join(kwargs)) or "0"
        kwcodestr = kwcodes and ("__KWARGS(%s)" % ", ".join(kwcodes)) or "0"

        # The callable is then obtained.

        if target:
            callable = target

        elif self.always_callable:
            callable = "__load_via_object(__tmp_target.value, %s).fn" % \
                     encode_symbol("pos", "__fn__")
        else:
            callable = "__check_and_load_via_object(__tmp_target.value, %s, %s).fn" % (
                     encode_symbol("pos", "__fn__"), encode_symbol("code", "__fn__"))

        stages.append(callable)

        # With a known target, the function is obtained directly and called.

        if target:
            output = "(\n%s\n)(%s)" % (",\n".join(stages), argstr)

        # With unknown targets, the generic invocation function is applied to
        # the callable and argument collections.

        else:
            output = "__invoke(\n(\n%s\n),\n%d, %s, %s,\n%d, %s\n)" % (
                ",\n".join(stages),
                len(kwargs), kwcodestr, kwargstr,
                len(args), argstr)

        return make_expression(output)

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

        defaults = self.process_function_defaults(n, name, "__tmp")
        if not defaults:
            return make_expression(encode_path(function_name))
        else:
            return make_expression("(__COPY(%s, __tmp), %s)" % (encode_path(function_name), ", ".join(defaults)))

    def process_logical_node(self, n):

        "Process the given operator node 'n'."

        if isinstance(n, compiler.ast.And):
            op = " && "
        else:
            op = " || "

        # NOTE: This needs to evaluate whether the operands are true or false
        # NOTE: according to Python rules.

        results = [("(%s)" % self.process_structure_node(node)) for node in n.nodes]
        return make_expression("(%s)" % op.join(results))

    def process_name_node(self, n, expr=None):

        "Process the given name node 'n' with the optional assignment 'expr'."

        # Determine whether the name refers to a static external entity.

        if n.name in predefined_constants:
            return PredefinedConstantRef(n.name)

        # Convert literal references.

        elif n.name.startswith("$L"):
            literal_name = n.name[len("$L"):]
            ref = self.importer.get_object("__builtins__.%s" % literal_name)
            return TrResolvedNameRef(n.name, ref)

        # Convert operator function names to references.

        elif n.name.startswith("$op"):
            ref = self.importer.get_module(self.name).special.get(n.name)
            return TrResolvedNameRef(n.name, ref)

        # Get the appropriate name for the name reference, using the same method
        # as in the inspector.

        path = self.get_object_path(n.name)
        ref = self.importer.get_object(path)
        name = self.get_name_for_tracking(n.name, ref and ref.final())

        # Get the static identity of the name.

        ref = self.importer.identify(path)

        # Obtain any resolved names for non-assignment names.

        if not expr and not ref and self.in_function:
            locals = self.importer.function_locals.get(self.get_namespace_path())
            ref = locals and locals.get(n.name)

        # Qualified names are used for resolved static references or for
        # static namespace members. The reference should be configured to return
        # such names.

        return TrResolvedNameRef(name, ref, expr=expr)

    def process_not_node(self, n):

        "Process the given operator node 'n'."

        # NOTE: This needs to evaluate whether the operand is true or false
        # NOTE: according to Python rules.

        return make_expression("(!(%s))" % n.expr)

    def process_try_node(self, n):

        """
        Process the given "try...except" node 'n'.
        """

        # NOTE: Placeholders/macros.

        self.writeline("TRY")
        self.writeline("{")
        self.indent += 1
        self.process_structure_node(n.body)
        self.indent -= 1
        self.writeline("}")

        for name, var, handler in n.handlers:
            if name is not None:
                name_ref = self.process_structure_node(name)
                self.writeline("EXCEPT(%s)" % name_ref)

            self.writeline("{")
            self.indent += 1

            # Establish the local for the handler.
            # NOTE: Need to provide the exception value.

            if var is not None:
                var_ref = self.process_structure_node(var)

            if handler is not None:
                self.process_structure_node(handler)

            self.indent -= 1
            self.writeline("}")

        if n.else_:
            self.process_structure_node(n.else_)

    def process_try_finally_node(self, n):

        """
        Process the given "try...finally" node 'n'.
        """

        # NOTE: Placeholders/macros.

        self.writeline("TRY")
        self.writeline("{")
        self.indent += 1
        self.process_structure_node(n.body)
        self.indent -= 1
        self.writeline("}")
        self.writeline("FINALLY")
        self.writeline("{")
        self.indent += 1
        self.process_structure_node(n.final)
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

            self.writeline("if (!(%s))" % test)
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

    # Output generation.

    def start_output(self):
        print >>self.out, """\
#include "types.h"
#include "ops.h"
#include "progconsts.h"
#include "progops.h"
#include "progtypes.h"
"""

    def start_module(self):
        print >>self.out, "void __main_%s()" % encode_path(self.name)
        print >>self.out, "{"
        self.indent += 1

    def end_module(self):
        self.indent -= 1
        self.end_function()

    def start_function(self, name):
        print >>self.out, "__attr %s(__attr __args[])" % encode_function_pointer(name)
        print >>self.out, "{"
        self.indent += 1
        self.writeline("__ref __tmp_context, __tmp_value;")
        self.writeline("__attr __tmp_target;")

        # Obtain local names from parameters.

        parameters = self.importer.function_parameters[name]
        names = []
        locals = self.importer.function_locals[name].keys()

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

        # Generate any self reference.

        if self.in_method(name):
            self.writeline("#define self (__args[0])")

        # Generate aliases for the parameters.

        for i, parameter in enumerate(parameters):
            self.writeline("#define %s (__args[%d])" % (encode_path(parameter), i+1))

    def end_function(self):
        self.indent -= 1
        print >>self.out, "}"
        print >>self.out

    def start_if(self, first, test_ref):

        # NOTE: This needs to evaluate whether the operand is true or false
        # NOTE: according to Python rules.

        self.writestmt("%sif (%s)" % (not first and "else " or "", test_ref))
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
        # NOTE: Should never be None.
        if not expr:
            self.writestmt("...;")
        s = str(expr)
        if s:
            self.writestmt("%s;" % s)

    def statements(self, results):
        for result in results:
            self.statement(result)

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

    def writeline(self, s):
        print >>self.out, "%s%s" % (self.pad(), self.indenttext(s, self.indent + 1))

    def writestmt(self, s):
        print >>self.out
        self.writeline(s)

    def write_comment(self, s):
        self.writestmt("/* %s */" % s)

# vim: tabstop=4 expandtab shiftwidth=4
