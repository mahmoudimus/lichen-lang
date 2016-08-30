#!/usr/bin/env python

"""
Inspect and obtain module structure.

Copyright (C) 2007, 2008, 2009, 2010, 2011, 2012, 2013,
              2014, 2015, 2016 Paul Boddie <paul@boddie.org.uk>

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
from common import *
from modules import *
from os import listdir
from os.path import extsep, split, splitext
from referencing import Reference
import compiler
import sys

class AccessRef(Result):

    """
    A reference to an attribute access that is generally only returned from a
    processed access for possible initialiser resolution for assignments.
    """

    def __init__(self, original_name, attrnames, number):
        self.original_name = original_name
        self.attrnames = attrnames
        self.number = number

    def reference(self):
        return None

    def __repr__(self):
        return "AccessRef(%r, %r, %r)" % (self.original_name, self.attrnames, self.number)

class InvocationRef(Result):

    "An invocation of a name reference."

    def __init__(self, name_ref):
        self.name_ref = name_ref

    def __repr__(self):
        return "InvocationRef(%r)" % self.name_ref

class InspectedModule(BasicModule, CacheWritingModule):

    "A module inspector."

    def __init__(self, name, importer):
        BasicModule.__init__(self, name, importer)
        self.in_class = False
        self.in_conditional = False
        self.global_attr_accesses = {}

        # Usage tracking.

        self.trackers = []
        self.attr_accessor_branches = {}

    def __repr__(self):
        return "InspectedModule(%r, %r)" % (self.name, self.importer)

    def parse(self, filename):

        "Parse the file having the given 'filename'."

        self.parse_file(filename)

        # Inspect the module.

        self.start_tracking_in_module()

        # Detect and record imports and globals declared in the module.

        self.assign_general_local("__name__", self.get_constant("str", self.name))
        self.assign_general_local("__file__", self.get_constant("str", filename))
        self.process_structure(self.astnode)

        # Set the class of the module after the definition has occurred.

        ref = self.get_builtin("object")
        self.set_name("__class__", ref)

        # Get module-level attribute usage details.

        self.stop_tracking_in_module()

        # Check names used and resolve them.

        self.register_submodules()
        self.loaded = True

    def register_submodules(self):

        "For package modules add submodule details."

        if splitext(split(self.filename)[1])[0] == "__init__":
            for subname in listdir(split(self.filename)[0]):
                name, ext = splitext(subname)

                # Add modules whose names are not already defined as globals.

                if ext == ("%spy" % extsep) and name != "__init__" and not self.get_global(name):
                    module_name = self.get_global_path(name)
                    top, submodule = self.get_module(module_name, True)
                    self.set_module(name, submodule, hidden=True)

    def check_special(self):

        "Check special names."

        for name, value in self.special.items():
            if value.has_kind("<depends>"):
                self.find_imported_name(name, self.name)
            self.special[name] = self.get_object(value.get_origin())

    def check_names_used(self):

        "Check the names used by each function."

        for path in self.names_used.keys():
            self.check_names_used_for_path(path)

    def check_names_used_for_path(self, path):

        "Check the names used by the given 'path'."

        names = self.names_used.get(path)
        if not names:
            return

        in_function = self.function_locals.has_key(path)

        for name in names:
            if name in predefined_constants or in_function and name in self.function_locals[path]:
                continue

            # Resolve names that have been imported locally.

            self.find_imported_name(name, path)

            # Find local definitions.

            key = "%s.%s" % (path, name)
            ref = self.get_object(key)
            if ref:
                self.name_references[key] = ref.final() or key
                self.resolve_accesses(path, name, ref)
                continue

            # Resolve names that have been imported globally.

            self.find_imported_name(name, self.name)

            # Find global or built-in definitions.

            ref = self.get_global_or_builtin(name)
            objpath = ref and (ref.final() or ref.get_name())
            if objpath:
                self.name_references[key] = objpath
                self.resolve_accesses(path, name, ref)
                continue

            print >>sys.stderr, "Name not recognised: %s in %s" % (name, path)
            init_item(self.names_missing, path, set)
            self.names_missing[path].add(name)

    def resolve_members(self):

        "Resolve any members referring to deferred references."

        for name, ref in self.objects.items():
            if ref.has_kind("<depends>"):
                ref = self.get_object(ref.get_origin())
                ref = ref.alias(name)
                self.importer.objects[name] = self.objects[name] = ref

    def resolve_accesses(self, path, name, ref):

        """
        Resolve any unresolved accesses in the function at the given 'path'
        for the given 'name' corresponding to the indicated 'ref'. Note that
        this mechanism cannot resolve things like inherited methods because
        they are not recorded as program objects in their inherited locations.
        """

        attr_accesses = self.global_attr_accesses.get(path)
        all_attrnames = attr_accesses and attr_accesses.get(name)

        if not all_attrnames:
            return

        # Insist on constant accessors.

        if not ref.has_kind(["<class>", "<module>"]):
            return

        found_attrnames = set()

        for attrnames in all_attrnames:

            # Start with the resolved name, adding attributes.

            attrs = ref.get_path()
            remaining = attrnames.split(".")
            last_ref = ref

            # Add each component, testing for a constant object.

            while remaining:
                attrname = remaining[0]
                attrs.append(attrname)
                del remaining[0]

                # Find any constant object reference.

                attr_ref = self.get_object(".".join(attrs))

                # Non-constant accessors terminate the traversal.

                if not attr_ref.has_kind(["<class>", "<module>", "<function>"]):

                    # Provide the furthest constant accessor unless the final
                    # access can be resolved.

                    if remaining:
                        remaining.insert(0, attrs.pop())
                    else:
                        last_ref = attr_ref
                    break

                # A module may expose an attribute imported from a hidden
                # module.

                elif last_ref.has_kind("<module>"):
                    module, leaf_module = self.get_module(last_ref.get_origin())
                    self.find_imported_name(attrname, module.name, module)

                # Follow any reference to a constant object.
                # Where the given name refers to an object in another location,
                # switch to the other location in order to be able to test its
                # attributes.

                last_ref = attr_ref
                attrs = attr_ref.get_path()

            # Record a constant accessor only if an object was found
            # that is different from the namespace involved.

            if last_ref:
                objpath = ".".join(attrs)
                if objpath != path:

                    # Establish a constant access.

                    init_item(self.const_accesses, path, dict)
                    self.const_accesses[path][(name, attrnames)] = (objpath, last_ref, ".".join(remaining))

                    if len(attrs) > 1:
                        found_attrnames.add(attrs[1])

        # Remove any usage records for the name.

        if found_attrnames:

            # NOTE: Should be only one name version.

            versions = []
            for version in self.attr_usage[path][name]:
                new_usage = set()
                for usage in version:
                    if found_attrnames.intersection(usage):
                        new_usage.add(tuple(set(usage).difference(found_attrnames)))
                    else:
                        new_usage.add(usage)
                versions.append(new_usage)

            self.attr_usage[path][name] = versions

    def resolve_initialisers(self):

        "Resolve initialiser values for names."

        # Get the initialisers in each namespace.

        for path, name_initialisers in self.name_initialisers.items():
            const_accesses = self.const_accesses.get(path)

            # Resolve values for each name in a scope.

            for name, values in name_initialisers.items():
                if path == self.name:
                    assigned_path = name
                else:
                    assigned_path = "%s.%s" % (path, name)

                initialised_names = {}
                aliased_names = {}

                for i, name_ref in enumerate(values):

                    # Unwrap invocations.

                    if isinstance(name_ref, InvocationRef):
                        invocation = True
                        name_ref = name_ref.name_ref
                    else:
                        invocation = False

                    # Obtain a usable reference from names or constants.

                    if isinstance(name_ref, ResolvedNameRef):
                        if not name_ref.reference():
                            continue
                        ref = name_ref.reference()

                    # Obtain a reference from instances.

                    elif isinstance(name_ref, InstanceRef):
                        if not name_ref.reference():
                            continue
                        ref = name_ref.reference()

                    # Resolve accesses that employ constants.

                    elif isinstance(name_ref, AccessRef):
                        ref = None

                        if const_accesses:
                            resolved_access = const_accesses.get((name_ref.original_name, name_ref.attrnames))
                            if resolved_access:
                                objpath, ref, remaining_attrnames = resolved_access
                                if remaining_attrnames:
                                    ref = None

                        # Accesses that do not employ constants cannot be resolved,
                        # but they may be resolvable later.

                        if not ref:
                            if not invocation:
                                aliased_names[i] = name_ref.original_name, name_ref.attrnames, name_ref.number
                            continue

                    # Attempt to resolve a plain name reference.

                    elif isinstance(name_ref, LocalNameRef):
                        key = "%s.%s" % (path, name_ref.name)
                        origin = self.name_references.get(key)

                        # Accesses that do not refer to known static objects
                        # cannot be resolved, but they may be resolvable later.

                        if not origin:
                            if not invocation:
                                aliased_names[i] = name_ref.name, None, name_ref.number
                            continue

                        ref = self.get_object(origin)
                        if not ref:
                            continue

                    elif isinstance(name_ref, NameRef):
                        key = "%s.%s" % (path, name_ref.name)
                        origin = self.name_references.get(key)
                        if not origin:
                            continue

                        ref = self.get_object(origin)
                        if not ref:
                            continue

                    else:
                        continue

                    # Convert class invocations to instances.

                    if invocation:
                        ref = ref.has_kind("<class>") and ref.instance_of() or None

                    if ref:
                        initialised_names[i] = ref

                if initialised_names:
                    self.initialised_names[assigned_path] = initialised_names
                if aliased_names:
                    self.aliased_names[assigned_path] = aliased_names

    def resolve_literals(self):

        "Resolve constant value types."

        # Get the constants defined in each namespace.

        for path, constants in self.constants.items():
            for constant, n in constants.items():
                objpath = "%s.$c%d" % (path, n)
                _constant, value_type = self.constant_values[objpath]
                self.initialised_names[objpath] = {0 : Reference("<instance>", value_type)}

        # Get the literals defined in each namespace.

        for path, literals in self.literals.items():
            for n in range(0, literals):
                objpath = "%s.$C%d" % (path, n)
                value_type = self.literal_types[objpath]
                self.initialised_names[objpath] = {0 : Reference("<instance>", value_type)}

    def remove_redundant_accessors(self):

        "Remove now-redundant modifier and accessor information."

        for path, const_accesses in self.const_accesses.items():
            accesses = self.attr_accessors.get(path)
            modifiers = self.attr_access_modifiers.get(path)
            if not accesses:
                continue
            for access in const_accesses.keys():
                if accesses.has_key(access):
                    del accesses[access]
                if modifiers and modifiers.has_key(access):
                    del modifiers[access]

    def set_invocation_usage(self):

        """
        Discard the current invocation storage figures, retaining the maximum
        values.
        """

        for path, (current, maximum) in self.function_targets.items():
            self.importer.function_targets[path] = self.function_targets[path] = maximum

        for path, (current, maximum) in self.function_arguments.items():
            self.importer.function_arguments[path] = self.function_arguments[path] = maximum

    # Module structure traversal.

    def process_structure_node(self, n):

        "Process the individual node 'n'."

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
            self.process_assignment_node(n, None)

        elif isinstance(n, compiler.ast.AssAttr):
            self.process_attribute_access(n)

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
            self.process_structure(n)
            self.trackers[-1].abandon_returning_branch()

        # Invocations.

        elif isinstance(n, compiler.ast.CallFunc):
            return self.process_invocation_node(n)

        # Constant usage.

        elif isinstance(n, compiler.ast.Const):
            return self.get_literal_instance(n, n.value.__class__.__name__)

        elif isinstance(n, compiler.ast.Dict):
            return self.get_literal_instance(n, "dict")

        elif isinstance(n, compiler.ast.List):
            return self.get_literal_instance(n, "list")

        elif isinstance(n, compiler.ast.Tuple):
            return self.get_literal_instance(n, "tuple")

        # List comprehensions and if expressions.

        elif isinstance(n, compiler.ast.ListComp):
            self.process_listcomp_node(n)

        elif isinstance(n, compiler.ast.IfExp):
            self.process_ifexp_node(n)

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

            name_ref = expr and self.process_structure_node(expr)

            # Name assignments populate either function namespaces or the
            # general namespace hierarchy.

            self.assign_general_local(n.name, name_ref)

            # Record usage of the name.

            self.record_name(n.name)

        elif isinstance(n, compiler.ast.AssAttr):
            if expr: self.process_structure_node(expr)
            self.process_attribute_access(n)

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

            assignment = isinstance(n, compiler.ast.AssAttr)

            init_item(self.attr_accesses, path, set)
            self.attr_accesses[path].add(attrnames)

            self.record_access_details(None, attrnames, assignment)
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

            name = self.get_name_for_tracking(name_ref.name, name_ref.final())
            tracker = self.trackers[-1]

            immediate_access = len(self.attrs) == 1
            assignment = immediate_access and isinstance(n, compiler.ast.AssAttr)

            del self.attrs[0]

            # Record global-based chains for subsequent resolution.

            is_global = self.in_function and not self.function_locals[path].has_key(name) or \
                        not self.in_function

            if is_global:
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

            branches = tracker.use_attribute(name, attrname)

            if not branches:
                print >>sys.stderr, "In %s, name %s is accessed using %s before an assignment." % (
                    path, name, attrname)
                branches = tracker.use_attribute(name, attrname)

            self.record_branches_for_access(branches, name, attrnames)
            access_number = self.record_access_details(name, attrnames, assignment)
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
                print >>sys.stderr, "In %s, class %s has unidentifiable base classes." % (
                    path, n.name)
                return
            else:
                bases.append(base_class)

        # Record bases for the class and retain the class name.

        class_name = self.get_object_path(n.name)

        if not bases and class_name != "__builtins__.core.object":
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
        self.set_name("__fn__") # special instantiator attribute
        self.set_name("__args__") # special instantiator attribute
        self.assign_general_local("__name__", self.get_constant("str", class_name))
        self.process_structure_node(n.code)
        self.exit_namespace()
        self.in_class = in_class

    def process_from_node(self, n):

        "Process the given node 'n', importing from another module."

        path = self.get_namespace_path()

        modname, names = self.get_module_name(n)

        # Load the mentioned module.

        top, module = self.get_module(modname, True)
        self.set_module(None, module, hidden=True)

        if not module:
            print >>sys.stderr, "In %s, from statement importing from %s failed." % (
                path, modname)

        # Attempt to obtain the referenced objects.

        for name, alias in n.names:

            # NOTE: Package submodules are not implicitly imported.

            if name == "*":
                if module:

                    # Warn about a circular import that probably doesn't find
                    # the names.

                    if not module.loaded:
                        print >>sys.stderr, "In %s, from statement performs circular import %s of %s." % (
                            path, modname)

                    for name, value in module.get_globals().items():
                        if name != "__name__":
                            value = ResolvedNameRef(name, value)
                            self.set_general_local(name, value)
                            self.set_imported_name(name, modname)
                break

            # Explicit names.

            ref = self.import_name_from_module(name, modname, module, alias)
            value = ResolvedNameRef(alias or name, ref)
            self.set_general_local(alias or name, value)
            self.set_imported_name(name, modname, alias)

    def import_name_from_module(self, name, modname, module, alias=None):

        """
        Import 'name' from the module having the given 'modname', with 'module'
        having been obtained for the module name, using 'alias' for the imported
        name in the current namespace.
        """

        path = self.get_namespace_path()

        if module and module.get_global(name):
            value = module.get_global(name)

            # Warn about an import that fails to provide a name, perhaps due
            # to a circular import.

            if not value:
                print >>sys.stderr, "In %s, from statement cannot import %s from %s%s." % (
                    path, name, modname, not module.loaded and "(circular import)")

            return value

        # Record the name as a dependency.

        else:
            return Reference("<depends>", "%s.%s" % (modname, name))

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

        # Initialise argument and local records.

        function_name = self.get_object_path(name)

        argnames = self.importer.function_parameters[function_name] = \
                   self.function_parameters[function_name] = get_argnames(n.argnames)
        locals = self.function_locals[function_name] = {}

        for argname in argnames:
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

        # Track attribute usage within the namespace.

        path = self.get_namespace_path()

        self.start_tracking(locals)
        self.process_structure_node(n.code)
        self.stop_tracking()

        # Exit to the parent.

        self.exit_namespace()

        # Update flags.

        self.in_function = in_function
        self.in_conditional = in_conditional

        # Define the function using the appropriate name.

        self.set_definition(name, "<function>")

        # Where a function is set conditionally, assign the name.

        if original_name:
            self.process_assignment_for_function(original_name, name)

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

    def process_ifexp_node(self, n):

        "Process the given if expression node 'n'."

        name_ref = self.process_structure_node(self.convert_ifexp_node(n))

        path = self.get_namespace_path()
        self.allocate_arguments(path, self.function_defaults[name_ref.get_origin()])
        self.deallocate_arguments(path, self.function_defaults[name_ref.get_origin()])

        return InvocationRef(name_ref)

    def process_import_node(self, n):

        "Process the given import node 'n'."

        path = self.get_namespace_path()

        # Load the mentioned module.

        for name, alias in n.names:
            module, leaf_module = self.get_module(name, alias)

            if not module:
                print >>sys.stderr, "In %s, import statement importing from %s failed." % (
                    path, name)
            if module and not module.loaded:
                print >>sys.stderr, "In %s, import statement performs circular import of %s." % (
                    path, name)

            self.set_module(alias or name.split(".")[0], module, leaf_module)

    def process_invocation_node(self, n):

        "Process the given invocation node 'n'."

        path = self.get_namespace_path()

        self.allocate_arguments(path, n.args)

        try:
            # Process the expression, obtaining any identified reference.

            name_ref = self.process_structure_node(n.node)

            # Process the arguments.

            for arg in n.args:
                self.process_structure_node(arg)

            # Detect class invocations.

            if isinstance(name_ref, ResolvedNameRef) and name_ref.has_kind("<class>"):
                return InstanceRef(name_ref.reference().instance_of())

            elif isinstance(name_ref, NameRef):
                return InvocationRef(name_ref)

            return None

        finally:
            self.deallocate_arguments(path, n.args)

    def process_lambda_node(self, n):

        "Process the given lambda node 'n'."

        name = self.get_lambda_name()
        self.process_function_node(n, name)

        origin = self.get_object_path(name)
        return ResolvedNameRef(name, Reference("<function>", origin))

    def process_listcomp_node(self, n):

        "Process the given list comprehension node 'n'."

        name_ref = self.process_structure_node(self.convert_listcomp_node(n))

        path = self.get_namespace_path()
        self.allocate_arguments(path, self.function_defaults[name_ref.get_origin()])
        self.deallocate_arguments(path, self.function_defaults[name_ref.get_origin()])

        return InvocationRef(name_ref)

    def process_logical_node(self, n):

        "Process the given operator node 'n'."

        self.process_operator_chain(n.nodes, self.process_structure_node)

    def process_name_node(self, n):

        "Process the given name node 'n'."

        path = self.get_namespace_path()

        # Special names.

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

            # Access the operator module.

            top, module = self.get_module("operator", True)
            self.set_module(None, module, hidden=True)

            # Link the operation to the operator module definition in this
            # module.

            self.set_imported_name(op, "operator", n.name, self.name)

            # Attempt to get a reference.

            ref = self.import_name_from_module(op, "operator", module)
            ref = self.get_object("operator.%s" % op) or ref

            # Record the imported name and provide the resolved name reference.

            value = ResolvedNameRef(n.name, ref)
            self.set_special(n.name, value)
            return value

        # Record usage of the name.

        self.record_name(n.name)

        # Search for unknown names in non-function scopes immediately.
        # External names in functions are resolved later.

        ref = self.find_name(n.name)
        if ref:
            return ResolvedNameRef(n.name, ref)

        # Global name.

        elif self.in_function and n.name in self.scope_globals[path]:
            return NameRef(n.name)

        # Examine other names.

        else:
            tracker = self.trackers[-1]

            # Check local names.

            branches = tracker.tracking_name(n.name)

            # Local name.

            if branches:
                self.record_branches_for_access(branches, n.name, None)
                access_number = self.record_access_details(n.name, None, False)
                return LocalNameRef(n.name, access_number)

            # Possible global name.

            else:
                return NameRef(n.name)

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
                self.process_structure_node(var)
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
        namespace.
        """

        path = self.get_namespace_path()
        tracker = self.trackers.pop()
        self.record_assignments_for_access(tracker)

        self.attr_usage[path] = tracker.get_all_usage()
        self.name_initialisers[path] = tracker.get_all_values()

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

    def record_access_details(self, name, attrnames, assignment):

        """
        For the given 'name' and 'attrnames', record an access indicating
        whether 'assignment' is occurring.

        These details correspond to accesses otherwise recorded by the attribute
        accessor and attribute access dictionaries.
        """

        access = name, attrnames
        path = self.get_path_for_access()

        init_item(self.attr_access_modifiers, path, dict)
        init_item(self.attr_access_modifiers[path], access, list)

        access_number = len(self.attr_access_modifiers[path][access])
        self.attr_access_modifiers[path][access].append(assignment)
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

    def set_module(self, name, module, leaf_module=None, hidden=False):

        """
        Set a module in the current namespace using the given 'name' and
        corresponding 'module' object, with the 'leaf_module' being recorded
        if different. If 'hidden' is a true value, the modules are recorded as
        not necessarily being exposed by this module. This module is, however,
        recorded as accessing the given modules and is thus dependent on them.
        """

        if name:
            self.set_general_local(name, module and Reference("<module>", module.name) or None)
        if module:
            if hidden:
                self.imported_hidden.add(module)
                if leaf_module and leaf_module is not module:
                    self.imported_hidden.add(leaf_module)
            else:
                self.imported.add(module)
                module.accessing_modules.add(self.name)
                if leaf_module and leaf_module is not module:
                    self.imported.add(leaf_module)
                    leaf_module.accessing_modules.add(self.name)

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

        init_item(self.instance_attrs, self.in_class, set)
        self.instance_attrs[self.in_class].add(name)

        if ref:
            init_item(self.instance_attr_constants, self.in_class, dict)
            self.instance_attr_constants[self.in_class][name] = ref

    def get_initialising_value(self, value):

        "Return a suitable initialiser reference for 'value'."

        if isinstance(value, (NameRef, AccessRef, InstanceRef)): # includes LiteralSequenceRef, ResolvedNameRef
            return value.reference()

        # In general, invocations do not produce known results. However, the
        # name initialisers are resolved once a module has been inspected.

        elif isinstance(value, InvocationRef):
            return None

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
                ref = self.get_object(self.get_object_path(name))
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
            return self.get_global_or_builtin(node.name)
        else:
            return None

    def get_constant(self, name, value):

        "Return a constant reference for the given type 'name' and 'value'."

        ref = self.get_literal_builtin(name)
        return self.get_constant_reference(ref, value)

    def get_literal_instance(self, n, name):

        "For node 'n', return a reference to an instance of 'name'."

        # Get a class reference.

        ref = self.get_literal_builtin(name)

        # Obtain the details of the literal itself.
        # An alias to the type is generated for sequences.

        if name in ("dict", "list", "tuple"):
            self.set_special_literal(name, ref)
            return self.process_literal_sequence_node(n, name, ref, LiteralSequenceRef)

        # Constant values are independently recorded.

        else:
            return self.get_constant_reference(ref, n.value)

    def get_literal_builtin(self, name):

        "Return a reference for a built-in literal type of the given 'name'."

        ref = self.get_builtin(name)
        true_origin = "__builtins__.%s.%s" % (name, name)
        exposed_origin = "__builtins__.%s" % name

        # Obtain fully-imported built-in class references.

        if ref and ref.has_kind("<class>"):
            pass

        # Early-stage references need explicit references.

        elif ref:
            ref = Reference("<class>", true_origin)

        # Otherwise, the normal locations can be used.

        else:
            ref = Reference("<class>", true_origin, exposed_origin)

        return ref

    # Functions and invocations.

    def allocate_arguments(self, path, args):

        """
        Allocate temporary argument storage using current and maximum
        requirements for the given 'path' and 'args'.
        """

        init_item(self.function_targets, path, lambda: [0, 0])
        t = self.function_targets[path]
        t[0] += 1
        t[1] = max(t[0], t[1])

        init_item(self.function_arguments, path, lambda: [0, 0])
        t = self.function_arguments[path]
        t[0] += len(args) + 1
        t[1] = max(t[0], t[1])

    def deallocate_arguments(self, path, args):

        "Deallocate temporary argument storage for the given 'path' and 'args'."

        self.function_targets[path][0] -= 1
        self.function_arguments[path][0] -= len(args) + 1

# vim: tabstop=4 expandtab shiftwidth=4
