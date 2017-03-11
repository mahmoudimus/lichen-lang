#!/usr/bin/env python

"""
Inspect and obtain module structure.

Copyright (C) 2007, 2008, 2009, 2010, 2011, 2012, 2013,
              2014, 2015, 2016, 2017 Paul Boddie <paul@boddie.org.uk>

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

from branching import BranchTracker
from common import CommonModule, get_argnames, init_item, predefined_constants
from modules import BasicModule, CacheWritingModule, InspectionNaming
from errors import InspectError
from referencing import Reference
from resolving import NameResolving
from results import AccessRef, InstanceRef, InvocationRef, LiteralSequenceRef, \
                    LocalNameRef, NameRef, ResolvedNameRef, VariableRef
import compiler
import sys

class InspectedModule(BasicModule, CacheWritingModule, NameResolving, InspectionNaming):

    "A module inspector."

    def __init__(self, name, importer):

        "Initialise the module with basic details."

        BasicModule.__init__(self, name, importer)

        self.in_class = False
        self.in_conditional = False

        # Accesses to global attributes.

        self.global_attr_accesses = {}

        # Usage tracking.

        self.trackers = []
        self.attr_accessor_branches = {}

    def __repr__(self):
        return "InspectedModule(%r, %r)" % (self.name, self.importer)

    # Principal methods.

    def parse(self, filename):

        "Parse the file having the given 'filename'."

        self.parse_file(filename)

        # Inspect the module.

        self.start_tracking_in_module()

        # Detect and record imports and globals declared in the module.

        self.process_structure(self.astnode)

        # Set the class of the module after the definition has occurred.

        ref = self.get_builtin("module")
        self.set_name("__class__", ref)
        self.set_name("__name__", self.get_constant("string", self.name).reference())
        self.set_name("__file__", self.get_constant("string", filename).reference())

        # Reserve a constant for the encoding.

        if self.encoding:
            self.get_constant("string", self.encoding)

        # Get module-level attribute usage details.

        self.stop_tracking_in_module()

        # Collect external name references.

        self.collect_names()

    def complete(self):

        "Complete the module inspection."

        # Resolve names not definitively mapped to objects.

        self.resolve()

        # Propagate to the importer information needed in subsequent activities.

        self.propagate()

    # Accessory methods.

    def collect_names(self):

        "Collect the names used by each scope."

        for path in self.names_used.keys():
            self.collect_names_for_path(path)

    def collect_names_for_path(self, path):

        """
        Collect the names used by the given 'path'. These are propagated to the
        importer in advance of any dependency resolution.
        """

        names = self.names_used.get(path)
        if not names:
            return

        in_function = self.function_locals.has_key(path)

        for name in names:
            if in_function and name in self.function_locals[path]:
                continue

            key = "%s.%s" % (path, name)

            # Find local definitions (within dynamic namespaces).

            ref = self.get_resolved_object(key)
            if ref:
                self.set_name_reference(key, ref)
                continue

            # Find global.

            ref = self.get_global(name)
            if ref:
                self.set_name_reference(key, ref)
                continue

            # Find presumed built-in definitions.

            ref = self.get_builtin(name)
            self.set_name_reference(key, ref)

    def set_name_reference(self, path, ref):

        "Map the given name 'path' to 'ref'."

        self.importer.all_name_references[path] = self.name_references[path] = ref

    # Module structure traversal.

    def process_structure_node(self, n):

        "Process the individual node 'n'."

        path = self.get_namespace_path()

        # Module global detection.

        if isinstance(n, compiler.ast.Global):
            self.process_global_node(n)

        # Module import declarations.

        elif isinstance(n, compiler.ast.From):
            self.process_from_node(n)

        elif isinstance(n, compiler.ast.Import):
            self.process_import_node(n)

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

        # Namespaces within modules.

        elif isinstance(n, compiler.ast.Class):
            self.process_class_node(n)

        elif isinstance(n, compiler.ast.Function):
            self.process_function_node(n, n.name)

        elif isinstance(n, compiler.ast.Lambda):
            return self.process_lambda_node(n)

        # Assignments.

        elif isinstance(n, compiler.ast.Assign):

            # Handle each assignment node.

            for node in n.nodes:
                self.process_assignment_node(node, n.expr)

        # Assignments within non-Assign nodes.

        elif isinstance(n, compiler.ast.AssName):
            raise InspectError("Name assignment appearing outside assignment statement.", path, n)

        elif isinstance(n, compiler.ast.AssAttr):
            raise InspectError("Attribute assignment appearing outside assignment statement.", path, n)

        # Accesses.

        elif isinstance(n, compiler.ast.Getattr):
            return self.process_attribute_access(n)

        # Name recording for later testing.

        elif isinstance(n, compiler.ast.Name):
            return self.process_name_node(n)

        # Conditional statement tracking.

        elif isinstance(n, compiler.ast.For):
            self.process_for_node(n)

        elif isinstance(n, compiler.ast.While):
            self.process_while_node(n)

        elif isinstance(n, compiler.ast.If):
            self.process_if_node(n)

        elif isinstance(n, (compiler.ast.And, compiler.ast.Or)):
            return self.process_logical_node(n)

        # Exception control-flow tracking.

        elif isinstance(n, compiler.ast.TryExcept):
            self.process_try_node(n)

        elif isinstance(n, compiler.ast.TryFinally):
            self.process_try_finally_node(n)

        # Control-flow modification statements.

        elif isinstance(n, compiler.ast.Break):
            self.trackers[-1].suspend_broken_branch()

        elif isinstance(n, compiler.ast.Continue):
            self.trackers[-1].suspend_continuing_branch()

        elif isinstance(n, compiler.ast.Raise):
            self.process_structure(n)
            self.trackers[-1].abandon_branch()

        elif isinstance(n, compiler.ast.Return):
            self.record_return_value(self.process_structure_node(n.value))
            self.trackers[-1].abandon_returning_branch()

        # Print statements.

        elif isinstance(n, (compiler.ast.Print, compiler.ast.Printnl)):
            self.process_print_node(n)

        # Invocations.

        elif isinstance(n, compiler.ast.CallFunc):
            return self.process_invocation_node(n)

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
            self.process_structure(n)

        # By default, no expression details are returned.

        return None

    # Specific node handling.

    def process_assignment_node(self, n, expr):

        "Process the individual node 'n' to be assigned the contents of 'expr'."

        # Names and attributes are assigned the entire expression.

        if isinstance(n, compiler.ast.AssName):
            if n.name == "self":
                raise InspectError("Redefinition of self is not allowed.", self.get_namespace_path(), n)

            name_ref = expr and self.process_structure_node(expr)

            # Name assignments populate either function namespaces or the
            # general namespace hierarchy.

            self.assign_general_local(n.name, name_ref)

            # Record usage of the name.

            self.record_name(n.name)

        elif isinstance(n, compiler.ast.AssAttr):
            if expr:
                expr = self.process_structure_node(expr)

            in_assignment = self.in_assignment
            self.in_assignment = True
            self.process_attribute_access(n)
            self.in_assignment = in_assignment

        # Lists and tuples are matched against the expression and their
        # items assigned to expression items.

        elif isinstance(n, (compiler.ast.AssList, compiler.ast.AssTuple)):
            self.process_assignment_node_items(n, expr)

        # Slices and subscripts are permitted within assignment nodes.

        elif isinstance(n, compiler.ast.Slice):
            self.process_slice_node(n, expr)

        elif isinstance(n, compiler.ast.Subscript):
            self.process_subscript_node(n, expr)

    def process_attribute_access(self, n):

        "Process the given attribute access node 'n'."

        # Obtain any completed chain and return the reference to it.

        name_ref = self.process_attribute_chain(n)

        if self.have_access_expression(n):
            return name_ref

        # Where the start of the chain of attributes has been reached, determine
        # the complete access.

        # Given a non-access node, this chain can be handled in its entirety,
        # either being name-based and thus an access rooted on a name, or being
        # based on some other node and thus an anonymous access of some kind.

        path = self.get_namespace_path()

        # Start with the the full attribute chain.

        remaining = self.attrs
        attrnames = ".".join(remaining)

        # If the accessor cannot be identified, or where attributes
        # remain in an attribute chain, record the anonymous accesses.

        if not isinstance(name_ref, NameRef): # includes ResolvedNameRef

            init_item(self.attr_accesses, path, set)
            self.attr_accesses[path].add(attrnames)

            self.record_access_details(None, attrnames, self.in_assignment,
                self.in_invocation)
            del self.attrs[0]
            return

        # Name-based accesses will handle the first attribute in a
        # chain.

        else:
            attrname = remaining[0]

            # Attribute assignments are used to identify instance attributes.

            if isinstance(n, compiler.ast.AssAttr) and \
                self.in_class and self.in_function and n.expr.name == "self":

                self.set_instance_attr(attrname)

            # Record attribute usage using any name local to this namespace,
            # if assigned in the namespace, or using an external name
            # (presently just globals within classes).

            name = self.get_name_for_tracking(name_ref.name, name_ref)
            tracker = self.trackers[-1]

            immediate_access = len(self.attrs) == 1
            assignment = immediate_access and isinstance(n, compiler.ast.AssAttr)

            # Record global-based chains for subsequent resolution.

            if name_ref.is_global_name():
                self.record_global_access_details(name, attrnames)

            # Make sure the name is being tracked: global names will not
            # already be initialised in a branch and must be added
            # explicitly.

            if not tracker.have_name(name):
                tracker.assign_names([name])
                if self.in_function:
                    self.scope_globals[path].add(name)

            # Record attribute usage in the tracker, and record the branch
            # information for the access.

            branches = tracker.use_attribute(name, attrname,
                self.in_invocation is not None, assignment)

            if not branches:
                raise InspectError("Name %s is accessed using %s before an assignment." % (
                    name, attrname), path, n)

            self.record_branches_for_access(branches, name, attrnames)
            access_number = self.record_access_details(name, attrnames,
                self.in_assignment, self.in_invocation)

            del self.attrs[0]
            return AccessRef(name, attrnames, access_number)

    def process_class_node(self, n):

        "Process the given class node 'n'."

        path = self.get_namespace_path()

        # To avoid notions of class "versions" where the same definition
        # might be parameterised with different state and be referenced
        # elsewhere (as base classes, for example), classes in functions or
        # conditions are forbidden.

        if self.in_function or self.in_conditional:
            print >>sys.stderr, "In %s, class %s in function or conditional statement ignored." % (
                path, n.name)
            return

        # Resolve base classes.

        bases = []

        for base in n.bases:
            base_class = self.get_class(base)

            if not base_class:
                print >>sys.stderr, "In %s, class %s has unidentifiable base class: %s" % (
                    path, n.name, base)
                return
            else:
                bases.append(base_class)

        # Detect conflicting definitions. Such definitions cause conflicts in
        # the storage of namespace-related information.

        class_name = self.get_object_path(n.name)
        ref = self.get_object(class_name, defer=False)

        if ref and ref.static():
            raise InspectError("Multiple definitions for the same name are not permitted.", class_name, n)

        # Record bases for the class and retain the class name.
        # Note that the function class does not inherit from the object class.

        if not bases and class_name != "__builtins__.core.object" and \
                         class_name != "__builtins__.core.function":

            ref = self.get_object("__builtins__.object")
            bases.append(ref)

        self.importer.classes[class_name] = self.classes[class_name] = bases
        self.importer.subclasses[class_name] = set()
        self.scope_globals[class_name] = set()

        # Set the definition before entering the namespace rather than
        # afterwards because methods may reference it. In normal Python,
        # a class is not accessible until the definition is complete, but
        # methods can generally reference it since upon being called the
        # class will already exist.

        self.set_definition(n.name, "<class>")

        in_class = self.in_class
        self.in_class = class_name
        self.set_instance_attr("__class__", Reference("<class>", class_name))
        self.enter_namespace(n.name)

        # Do not provide the special instantiator attributes on the function
        # class. Function instances provide these attributes.

        if class_name != "__builtins__.core.function":

            self.set_name("__fn__") # special instantiator attribute
            self.set_name("__args__") # special instantiator attribute

        # Provide leafname, parent and context attributes.

        parent, leafname = class_name.rsplit(".", 1)
        self.set_name("__name__", self.get_constant("string", leafname).reference())

        if class_name != "__builtins__.core.function":
            self.set_name("__parent__")

        self.process_structure_node(n.code)
        self.exit_namespace()
        self.in_class = in_class

    def process_from_node(self, n):

        "Process the given node 'n', importing from another module."

        path = self.get_namespace_path()

        module_name, names = self.get_module_name(n)
        if module_name == self.name:
            raise InspectError("Cannot import from the current module.", path, n)

        self.queue_module(module_name)

        # Attempt to obtain the referenced objects.

        for name, alias in n.names:
            if name == "*":
                raise InspectError("Only explicitly specified names can be imported from modules.", path, n)

            # Explicit names.

            ref = self.import_name_from_module(name, module_name)
            value = ResolvedNameRef(alias or name, ref)
            self.set_general_local(alias or name, value)

    def process_function_node(self, n, name):

        """
        Process the given function or lambda node 'n' with the given 'name'.
        """

        is_lambda = isinstance(n, compiler.ast.Lambda)

        # Where a function is declared conditionally, use a separate name for
        # the definition, and assign the definition to the stated name.

        if (self.in_conditional or self.in_function) and not is_lambda:
            original_name = name
            name = self.get_lambda_name()
        else:
            original_name = None

        # Detect conflicting definitions. Such definitions cause conflicts in
        # the storage of namespace-related information.

        function_name = self.get_object_path(name)
        ref = self.get_object(function_name, defer=False)

        if ref and ref.static():
            raise InspectError("Multiple definitions for the same name are not permitted.", function_name, n)

        # Initialise argument and local records.

        argnames = get_argnames(n.argnames)
        is_method = self.in_class and not self.in_function

        # Remove explicit "self" from method parameters.

        if is_method and argnames and argnames[0] == "self":
            del argnames[0]

        # Copy and propagate the parameters.

        self.importer.function_parameters[function_name] = \
            self.function_parameters[function_name] = argnames[:]

        # Define all arguments/parameters in the local namespace.

        locals = \
            self.importer.function_locals[function_name] = \
            self.function_locals[function_name] = {}

        # Insert "self" into method locals.

        if is_method:
            argnames.insert(0, "self")

        # Define "self" in terms of the class if in a method.
        # This does not diminish the need for type-narrowing in the deducer.

        if argnames:
            if self.in_class and not self.in_function and argnames[0] == "self":
                locals[argnames[0]] = Reference("<instance>", self.in_class)
            else:
                locals[argnames[0]] = Reference("<var>")

        for argname in argnames[1:]:
            locals[argname] = Reference("<var>")

        globals = self.scope_globals[function_name] = set()

        # Process the defaults.

        defaults = self.importer.function_defaults[function_name] = \
                   self.function_defaults[function_name] = []

        for argname, default in compiler.ast.get_defaults(n):
            if default:

                # Obtain any reference for the default.

                name_ref = self.process_structure_node(default)
                defaults.append((argname, name_ref.is_name() and name_ref.reference() or Reference("<var>")))

        # Reset conditional tracking to focus on the function contents.

        in_conditional = self.in_conditional
        self.in_conditional = False

        in_function = self.in_function
        self.in_function = function_name

        self.enter_namespace(name)

        # Define a leafname attribute value for the function instance.

        ref = self.get_builtin_class("string")
        self.reserve_constant(function_name, name, ref.get_origin())

        # Track attribute usage within the namespace.

        path = self.get_namespace_path()

        self.start_tracking(locals)
        self.process_structure_node(n.code)
        returns_value = self.stop_tracking()

        # Record any null result.

        is_initialiser = is_method and name == "__init__"

        if not returns_value and not is_initialiser:
            self.record_return_value(ResolvedNameRef("None", self.get_builtin("None")))

        # Exit to the parent.

        self.exit_namespace()

        # Update flags.

        self.in_function = in_function
        self.in_conditional = in_conditional

        # Define the function using the appropriate name.

        self.set_definition(name, "<function>")

        # Where a function is set conditionally, assign the name.

        if original_name:
            self.process_assignment_for_object(original_name, compiler.ast.Name(name))

    def process_global_node(self, n):

        """
        Process the given "global" node 'n'.
        """

        path = self.get_namespace_path()

        if path != self.name:
            self.scope_globals[path].update(n.names)

    def process_if_node(self, n):

        """
        Process the given "if" node 'n'.
        """

        tracker = self.trackers[-1]
        tracker.new_branchpoint()

        for test, body in n.tests:
            self.process_structure_node(test)

            tracker.new_branch()

            in_conditional = self.in_conditional
            self.in_conditional = True
            self.process_structure_node(body)
            self.in_conditional = in_conditional

            tracker.shelve_branch()

        # Maintain a branch for the else clause.

        tracker.new_branch()
        if n.else_:
            self.process_structure_node(n.else_)
        tracker.shelve_branch()

        tracker.merge_branches()

    def process_import_node(self, n):

        "Process the given import node 'n'."

        path = self.get_namespace_path()

        # Load the mentioned module.

        for name, alias in n.names:
            if name == self.name:
                raise InspectError("Cannot import the current module.", path, n)

            self.set_module(alias or name.split(".")[-1], name)
            self.queue_module(name, True)

    def process_invocation_node(self, n):

        "Process the given invocation node 'n'."

        path = self.get_namespace_path()

        in_invocation = self.in_invocation
        self.in_invocation = None

        # Process the arguments.

        keywords = set()

        for arg in n.args:
            self.process_structure_node(arg)
            if isinstance(arg, compiler.ast.Keyword):
                keywords.add(arg.name)

        keywords = list(keywords)
        keywords.sort()

        # Communicate to the invocation target expression that it forms the
        # target of an invocation, potentially affecting attribute accesses.

        self.in_invocation = len(n.args), keywords

        # Process the expression, obtaining any identified reference.

        name_ref = self.process_structure_node(n.node)
        self.in_invocation = in_invocation

        # Detect class invocations.

        if isinstance(name_ref, ResolvedNameRef) and name_ref.has_kind("<class>"):
            return InstanceRef(name_ref.reference().instance_of())

        elif isinstance(name_ref, NameRef):
            return InvocationRef(name_ref)

        # Provide a general reference to indicate that something is produced
        # by the invocation, useful for retaining assignment expression
        # details.

        return VariableRef()

    def process_lambda_node(self, n):

        "Process the given lambda node 'n'."

        name = self.get_lambda_name()
        self.process_function_node(n, name)

        origin = self.get_object_path(name)

        if self.function_defaults.get(origin):
            return None
        else:
            return ResolvedNameRef(name, Reference("<function>", origin))

    def process_logical_node(self, n):

        "Process the given operator node 'n'."

        self.process_operator_chain(n.nodes, self.process_structure_node)

    def process_name_node(self, n):

        "Process the given name node 'n'."

        path = self.get_namespace_path()

        # Find predefined constant names before anything else.

        if n.name in predefined_constants:
            ref = self.get_builtin(n.name)
            value = ResolvedNameRef(n.name, ref)
            return value

        # Special names that have already been identified.

        if n.name.startswith("$"):
            value = self.get_special(n.name)
            if value:
                return value

        # Special case for operator functions introduced through code
        # transformations.

        if n.name.startswith("$op"):

            # Obtain the location of the actual function defined in the operator
            # package.

            op = n.name[len("$op"):]

            # Attempt to get a reference.

            ref = self.import_name_from_module(op, "operator")

            # Record the imported name and provide the resolved name reference.

            value = ResolvedNameRef(n.name, ref)
            self.set_special(n.name, value)
            return value

        # Special case for print operations.

        elif n.name.startswith("$print"):

            # Attempt to get a reference.

            ref = self.get_builtin("print_")

            # Record the imported name and provide the resolved name reference.

            value = ResolvedNameRef(n.name, ref)
            self.set_special(n.name, value)
            return value

        # Test for self usage, which is only allowed in methods.

        if n.name == "self" and not (self.in_function and self.in_class):
            raise InspectError("Use of self is only allowed in methods.", path, n)

        # Record usage of the name.

        self.record_name(n.name)

        # Search for unknown names in non-function scopes immediately.
        # External names in functions are resolved later.

        ref = self.find_name(n.name)
        if ref:
            self.record_name_access(n.name, True)
            return ResolvedNameRef(n.name, ref, is_global=True)

        # Explicitly-declared global names.

        elif self.in_function and n.name in self.scope_globals[path]:
            self.record_name_access(n.name, True)
            return NameRef(n.name, is_global=True)

        # Examine other names.

        else:

            # Check local names.

            access_number = self.record_name_access(n.name)

            # Local name.

            if access_number is not None:
                return LocalNameRef(n.name, access_number)

            # Possible global or built-in name.

            else:
                self.record_name_access(n.name, True)
                return NameRef(n.name, is_global=True)

    def record_name_access(self, name, is_global=False):

        """
        Record an access involving 'name' if the name is being tracked, using
        'is_global' to indicate whether the name is global.
        """

        name = self.get_name_for_tracking(name, is_global=is_global)
        branches = self.trackers[-1].tracking_name(name)
        if branches:
            self.record_branches_for_access(branches, name, None)
            return self.record_access_details(name, None, None, None)
        return None

    def process_operator_chain(self, nodes, fn):

        """
        Process the given chain of 'nodes', applying 'fn' to each node or item.
        Each node starts a new conditional region, effectively making a deeply-
        nested collection of if-like statements.
        """

        tracker = self.trackers[-1]

        for item in nodes:
            tracker.new_branchpoint()
            tracker.new_branch()
            fn(item)

        for item in nodes[:-1]:
            tracker.shelve_branch()
            tracker.new_branch()
            tracker.shelve_branch()
            tracker.merge_branches()

        tracker.shelve_branch()
        tracker.merge_branches()

    def process_try_node(self, n):

        """
        Process the given "try...except" node 'n'.
        """

        self.record_exception_handler()

        tracker = self.trackers[-1]
        tracker.new_branchpoint()

        self.process_structure_node(n.body)

        for name, var, handler in n.handlers:
            if name is not None:
                self.process_structure_node(name)

            # Any abandoned branches from the body can now be resumed in a new
            # branch.

            tracker.resume_abandoned_branches()

            # Establish the local for the handler.

            if var is not None:
                self.process_assignment_node(var, None)
            if handler is not None:
                self.process_structure_node(handler)

            tracker.shelve_branch()

        # The else clause maintains the usage from the body but without the
        # abandoned branches since they would never lead to the else clause
        # being executed.

        if n.else_:
            tracker.new_branch()
            self.process_structure_node(n.else_)
            tracker.shelve_branch()

        # Without an else clause, a null branch propagates the successful
        # outcome.

        else:
            tracker.new_branch()
            tracker.shelve_branch()

        tracker.merge_branches()

    def process_try_finally_node(self, n):

        """
        Process the given "try...finally" node 'n'.
        """

        self.record_exception_handler()

        tracker = self.trackers[-1]
        self.process_structure_node(n.body)

        # Any abandoned branches from the body can now be resumed.

        branches = tracker.resume_all_abandoned_branches()
        self.process_structure_node(n.final)

        # At the end of the finally clause, abandoned branches are discarded.

        tracker.restore_active_branches(branches)

    def process_while_node(self, n):

        "Process the given while node 'n'."

        tracker = self.trackers[-1]
        tracker.new_branchpoint(loop_node=True)

        # Evaluate any test or iterator outside the loop.

        self.process_structure_node(n.test)

        # Propagate attribute usage to branches.

        tracker.new_branch(loop_node=True)

        # Enter the loop.

        in_conditional = self.in_conditional
        self.in_conditional = True
        self.process_structure_node(n.body)
        self.in_conditional = in_conditional

        # Continuing branches are resumed before any test.

        tracker.resume_continuing_branches()

        # Evaluate any continuation test within the body.

        self.process_structure_node(n.test)

        tracker.shelve_branch(loop_node=True)

        # Support the non-looping condition.

        tracker.new_branch()
        tracker.shelve_branch()

        tracker.merge_branches()

        # Evaluate any else clause outside branches.

        if n.else_:
            self.process_structure_node(n.else_)

        # Connect broken branches to the code after any loop.

        tracker.resume_broken_branches()

    # Branch tracking methods.

    def start_tracking(self, names):

        """
        Start tracking attribute usage for names in the current namespace,
        immediately registering the given 'names'.
        """

        path = self.get_namespace_path()
        parent = self.trackers[-1]
        tracker = BranchTracker()
        self.trackers.append(tracker)

        # Record the given names established as new branches.

        tracker.assign_names(names)

    def assign_name(self, name, name_ref):

        "Assign to 'name' the given 'name_ref' in the current namespace."

        name = self.get_name_for_tracking(name)
        self.trackers[-1].assign_names([name], [name_ref])

    def stop_tracking(self):

        """
        Stop tracking attribute usage, recording computed usage for the current
        namespace. Indicate whether a value is always returned from the
        namespace.
        """

        path = self.get_namespace_path()
        tracker = self.trackers.pop()
        self.record_assignments_for_access(tracker)

        self.attr_usage[path] = tracker.get_all_usage()
        self.name_initialisers[path] = tracker.get_all_values()

        return tracker.returns_value()

    def start_tracking_in_module(self):

        "Start tracking attribute usage in the module."

        tracker = BranchTracker()
        self.trackers.append(tracker)

    def stop_tracking_in_module(self):

        "Stop tracking attribute usage in the module."

        tracker = self.trackers[0]
        self.record_assignments_for_access(tracker)
        self.attr_usage[self.name] = tracker.get_all_usage()
        self.name_initialisers[self.name] = tracker.get_all_values()

    def record_assignments_for_access(self, tracker):

        """
        For the current path, use the given 'tracker' to record assignment
        version information for attribute accesses.
        """

        path = self.get_path_for_access()

        if not self.attr_accessor_branches.has_key(path):
            return

        init_item(self.attr_accessors, path, dict)
        attr_accessors = self.attr_accessors[path]

        # Obtain the branches applying during each access.

        for access, all_branches in self.attr_accessor_branches[path].items():
            name, attrnames = access
            init_item(attr_accessors, access, list)

            # Obtain the assignments applying to each branch.

            for branches in all_branches:
                positions = tracker.get_assignment_positions_for_branches(name, branches)

                # Detect missing name information.

                if None in positions:
                    globals = self.global_attr_accesses.get(path)
                    accesses = globals and globals.get(name)
                    if not accesses:
                        print >>sys.stderr, "In %s, %s may not be defined when used." % (
                            self.get_namespace_path(), name)
                    positions.remove(None)

                attr_accessors[access].append(positions)

    def record_branches_for_access(self, branches, name, attrnames):

        """
        Record the given 'branches' for an access involving the given 'name' and
        'attrnames'.
        """

        access = name, attrnames
        path = self.get_path_for_access()

        init_item(self.attr_accessor_branches, path, dict)
        attr_accessor_branches = self.attr_accessor_branches[path]

        init_item(attr_accessor_branches, access, list)
        attr_accessor_branches[access].append(branches)

    def record_access_details(self, name, attrnames, assignment, invocation):

        """
        For the given 'name' and 'attrnames', record an access indicating
        whether an 'assignment' or an 'invocation' is occurring.

        These details correspond to accesses otherwise recorded by the attribute
        accessor and attribute access dictionaries.
        """

        access = name, attrnames
        path = self.get_path_for_access()

        init_item(self.attr_access_modifiers, path, dict)
        init_item(self.attr_access_modifiers[path], access, list)

        access_number = len(self.attr_access_modifiers[path][access])
        self.attr_access_modifiers[path][access].append((assignment, invocation))
        return access_number

    def record_global_access_details(self, name, attrnames):

        """
        Record details of a global access via the given 'name' involving the
        indicated 'attrnames'.
        """

        path = self.get_namespace_path()

        init_item(self.global_attr_accesses, path, dict)
        init_item(self.global_attr_accesses[path], name, set)
        self.global_attr_accesses[path][name].add(attrnames)

    # Namespace modification.

    def record_name(self, name):

        "Record the use of 'name' in a namespace."

        path = self.get_namespace_path()
        init_item(self.names_used, path, set)
        self.names_used[path].add(name)

    def set_module(self, name, module_name):

        """
        Set a module in the current namespace using the given 'name' associated
        with the corresponding 'module_name'.
        """

        if name:
            self.set_general_local(name, Reference("<module>", module_name))

    def set_definition(self, name, kind):

        """
        Set the definition having the given 'name' and 'kind'.

        Definitions are set in the static namespace hierarchy, but they can also
        be recorded for function locals.
        """

        if self.is_global(name):
            print >>sys.stderr, "In %s, %s is defined as being global." % (
                self.get_namespace_path(), name)

        path = self.get_object_path(name)
        self.set_object(path, kind)

        ref = self.get_object(path)
        if ref.get_kind() == "<var>":
            print >>sys.stderr, "In %s, %s is defined more than once." % (
                self.get_namespace_path(), name)

        if not self.is_global(name) and self.in_function:
            self.set_function_local(name, ref)

    def set_function_local(self, name, ref=None):

        "Set the local with the given 'name' and optional 'ref'."

        locals = self.function_locals[self.get_namespace_path()]
        multiple = not ref or locals.has_key(name) and locals[name] != ref
        locals[name] = multiple and Reference("<var>") or ref

    def assign_general_local(self, name, name_ref):

        """
        Set for 'name' the given 'name_ref', recording the name for attribute
        usage tracking.
        """

        self.set_general_local(name, name_ref)
        self.assign_name(name, name_ref)

    def set_general_local(self, name, value=None):

        """
        Set the 'name' with optional 'value' in any kind of local namespace,
        where the 'value' should be a reference if specified.
        """

        init_value = self.get_initialising_value(value)

        # Module global names.

        if self.is_global(name):
            path = self.get_global_path(name)
            self.set_object(path, init_value)

        # Function local names.

        elif self.in_function:
            path = self.get_object_path(name)
            self.set_function_local(name, init_value)

        # Other namespaces (classes).

        else:
            path = self.get_object_path(name)
            self.set_name(name, init_value)

    def set_name(self, name, ref=None):

        "Attach the 'name' with optional 'ref' to the current namespace."

        self.set_object(self.get_object_path(name), ref)

    def set_instance_attr(self, name, ref=None):

        """
        Add an instance attribute of the given 'name' to the current class,
        using the optional 'ref'.
        """

        self._set_instance_attr(self.in_class, name, ref)

    def _set_instance_attr(self, path, name, ref=None):

        init_item(self.instance_attrs, path, set)
        self.instance_attrs[path].add(name)

        if ref:
            init_item(self.instance_attr_constants, path, dict)
            self.instance_attr_constants[path][name] = ref

    def get_initialising_value(self, value):

        "Return a suitable initialiser reference for 'value'."

        # Includes LiteralSequenceRef, ResolvedNameRef...

        if isinstance(value, (NameRef, AccessRef, InstanceRef)):
            return value.reference()

        # In general, invocations do not produce known results. However, the
        # name initialisers are resolved once a module has been inspected.

        elif isinstance(value, InvocationRef):
            return value.reference()

        # Variable references are unknown results.

        elif isinstance(value, VariableRef):
            return value.reference()

        else:
            return value

    # Static, program-relative naming.

    def find_name(self, name):

        """
        Return the qualified name for the given 'name' used in the current
        non-function namespace.
        """

        path = self.get_namespace_path()
        ref = None

        if not self.in_function and name not in predefined_constants:
            if self.in_class:
                ref = self.get_object(self.get_object_path(name), False)
            if not ref:
                ref = self.get_global_or_builtin(name)

        return ref

    def get_class(self, node):

        """
        Use the given 'node' to obtain the identity of a class. Return a
        reference for the class. Unresolved dependencies are permitted and must
        be resolved later.
        """

        ref = self._get_class(node)
        return ref.has_kind(["<class>", "<depends>"]) and ref or None

    def _get_class(self, node):

        """
        Use the given 'node' to find a class definition. Return a reference to
        the class.
        """

        if isinstance(node, compiler.ast.Getattr):

            # Obtain the identity of the access target.

            ref = self._get_class(node.expr)

            # Where the target is a class or module, obtain the identity of the
            # attribute.

            if ref.has_kind(["<function>", "<var>"]):
                return None
            else:
                attrname = "%s.%s" % (ref.get_origin(), node.attrname)
                return self.get_object(attrname)

        # Names can be module-level or built-in.

        elif isinstance(node, compiler.ast.Name):

            # Record usage of the name and attempt to identify it.

            self.record_name(node.name)
            return self.find_name(node.name)
        else:
            return None

    def get_constant(self, name, value):

        "Return a constant reference for the given type 'name' and 'value'."

        ref = self.get_builtin_class(name)
        return self.get_constant_reference(ref, value)

    def get_literal_instance(self, n, name=None):

        """
        For node 'n', return a reference to an instance of 'name', or if 'name'
        is not specified, deduce the type from the value.
        """

        # Handle stray None constants (Sliceobj seems to produce them).

        if name == "NoneType":
            return self.process_name_node(compiler.ast.Name("None"))

        # Obtain the details of the literal itself.
        # An alias to the type is generated for sequences.

        if name in ("dict", "list", "tuple"):
            ref = self.get_builtin_class(name)
            self.set_special_literal(name, ref)
            return self.process_literal_sequence_node(n, name, ref, LiteralSequenceRef)

        # Constant values are independently recorded.

        else:
            value, typename, encoding = self.get_constant_value(n.value, n.literals)
            ref = self.get_builtin_class(typename)
            return self.get_constant_reference(ref, value, encoding)

    # Special names.

    def get_special(self, name):

        "Return any stored value for the given special 'name'."

        value = self.special.get(name)
        if value:
            ref, paths = value
        else:
            ref = None
        return ref

    def set_special(self, name, value):

        """
        Set a special 'name' that merely tracks the use of an implicit object
        'value'.
        """

        if not self.special.has_key(name):
            paths = set()
            self.special[name] = value, paths
        else:
            _ref, paths = self.special[name]

        paths.add(self.get_namespace_path())

    def set_special_literal(self, name, ref):

        """
        Set a special name for the literal type 'name' having type 'ref'. Such
        special names provide a way of referring to literal object types.
        """

        literal_name = "$L%s" % name
        value = ResolvedNameRef(literal_name, ref)
        self.set_special(literal_name, value)

    # Exceptions.

    def record_exception_handler(self):

        "Record the current namespace as employing an exception handler."

        self.exception_namespaces.add(self.get_namespace_path())

    # Return values.

    def record_return_value(self, expr):

        "Record the given return 'expr'."

        path = self.get_namespace_path()
        init_item(self.return_values, path, set)
        self.return_values[path].add(expr)

# vim: tabstop=4 expandtab shiftwidth=4
