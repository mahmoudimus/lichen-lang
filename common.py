#!/usr/bin/env python

"""
Common functions.

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

from errors import *
from os import listdir, makedirs, remove
from os.path import exists, isdir, join, split
from results import ConstantValueRef, LiteralSequenceRef, NameRef
import compiler

class CommonOutput:

    "Common output functionality."

    def check_output(self):

        "Check the existing output and remove it if irrelevant."

        if not exists(self.output):
            makedirs(self.output)

        details = self.importer.get_cache_details()
        recorded_details = self.get_output_details()

        if recorded_details != details:
            self.remove_output()

        writefile(self.get_output_details_filename(), details)

    def get_output_details_filename(self):

        "Return the output details filename."

        return join(self.output, "$details")

    def get_output_details(self):

        "Return details of the existing output."

        details_filename = self.get_output_details_filename()

        if not exists(details_filename):
            return None
        else:
            return readfile(details_filename)

    def remove_output(self, dirname=None):

        "Remove the output."

        dirname = dirname or self.output

        for filename in listdir(dirname):
            path = join(dirname, filename)
            if isdir(path):
                self.remove_output(path)
            else:
                remove(path)

class CommonModule:

    "A common module representation."

    def __init__(self, name, importer):

        """
        Initialise this module with the given 'name' and an 'importer' which is
        used to provide access to other modules when required.
        """

        self.name = name
        self.importer = importer
        self.filename = None

        # Inspection-related attributes.

        self.astnode = None
        self.iterators = {}
        self.temp = {}
        self.lambdas = {}

        # Constants, literals and values.

        self.constants = {}
        self.constant_values = {}
        self.literals = {}
        self.literal_types = {}

        # Nested namespaces.

        self.namespace_path = []
        self.in_function = False

        # Attribute chains.

        self.attrs = []

    def __repr__(self):
        return "CommonModule(%r, %r)" % (self.name, self.importer)

    def parse_file(self, filename):

        "Parse the file with the given 'filename', initialising attributes."

        self.filename = filename
        self.astnode = compiler.parseFile(filename)

    # Module-relative naming.

    def get_global_path(self, name):
        return "%s.%s" % (self.name, name)

    def get_namespace_path(self):
        return ".".join([self.name] + self.namespace_path)

    def get_object_path(self, name):
        return ".".join([self.name] + self.namespace_path + [name])

    def get_parent_path(self):
        return ".".join([self.name] + self.namespace_path[:-1])

    # Namespace management.

    def enter_namespace(self, name):

        "Enter the namespace having the given 'name'."

        self.namespace_path.append(name)

    def exit_namespace(self):

        "Exit the current namespace."

        self.namespace_path.pop()

    # Constant reference naming.

    def get_constant_name(self, value):

        "Add a new constant to the current namespace for 'value'."

        path = self.get_namespace_path()
        init_item(self.constants, path, dict)
        return "$c%d" % add_counter_item(self.constants[path], value)

    # Literal reference naming.

    def get_literal_name(self):

        "Add a new literal to the current namespace."

        path = self.get_namespace_path()
        init_item(self.literals, path, lambda: 0)
        return "$C%d" % self.literals[path]

    def next_literal(self):
        self.literals[self.get_namespace_path()] += 1

    # Temporary iterator naming.

    def get_iterator_path(self):
        return self.in_function and self.get_namespace_path() or self.name

    def get_iterator_name(self):
        path = self.get_iterator_path()
        init_item(self.iterators, path, lambda: 0)
        return "$i%d" % self.iterators[path]

    def next_iterator(self):
        self.iterators[self.get_iterator_path()] += 1

    # Temporary variable naming.

    def get_temporary_name(self):
        path = self.get_namespace_path()
        init_item(self.temp, path, lambda: 0)
        return "$t%d" % self.temp[path]

    def next_temporary(self):
        self.temp[self.get_namespace_path()] += 1

    # Arbitrary function naming.

    def get_lambda_name(self):
        path = self.get_namespace_path()
        init_item(self.lambdas, path, lambda: 0)
        name = "$l%d" % self.lambdas[path]
        self.lambdas[path] += 1
        return name

    def reset_lambdas(self):
        self.lambdas = {}

    # Constant and literal recording.

    def get_constant_reference(self, ref, value):

        "Return a constant reference for the given 'ref' type and 'value'."

        constant_name = self.get_constant_name(value)

        # Return a reference for the constant.

        objpath = self.get_object_path(constant_name)
        name_ref = ConstantValueRef(constant_name, ref.instance_of(), value)

        # Record the value and type for the constant.

        self.constant_values[objpath] = name_ref.value, name_ref.get_origin()
        return name_ref

    def get_literal_reference(self, name, ref, items, cls):

        """
        Return a literal reference for the given type 'name', literal 'ref',
        node 'items' and employing the given 'cls' as the class of the returned
        reference object.
        """

        # Construct an invocation using the items as arguments.

        typename = "$L%s" % name

        invocation = compiler.ast.CallFunc(
            compiler.ast.Name(typename),
            items
            )

        # Get a name for the actual literal.

        instname = self.get_literal_name()
        self.next_literal()

        # Record the type for the literal.

        objpath = self.get_object_path(instname)
        self.literal_types[objpath] = ref.get_origin()

        # Return a wrapper for the invocation exposing the items.

        return cls(
            instname,
            ref.instance_of(),
            self.process_structure_node(invocation),
            invocation.args
            )

    # Node handling.

    def process_structure(self, node):

        """
        Within the given 'node', process the program structure.

        During inspection, this will process global declarations, adjusting the
        module namespace, and import statements, building a module dependency
        hierarchy.

        During translation, this will consult deduced program information and
        output translated code.
        """

        l = []
        for n in node.getChildNodes():
            l.append(self.process_structure_node(n))
        return l

    def process_augassign_node(self, n):

        "Process the given augmented assignment node 'n'."

        op = operator_functions[n.op]

        if isinstance(n.node, compiler.ast.Getattr):
            target = compiler.ast.AssAttr(n.node.expr, n.node.attrname, "OP_ASSIGN")
        elif isinstance(n.node, compiler.ast.Name):
            target = compiler.ast.AssName(n.node.name, "OP_ASSIGN")
        else:
            target = n.node

        assignment = compiler.ast.Assign(
            [target],
            compiler.ast.CallFunc(
                compiler.ast.Name("$op%s" % op),
                [n.node, n.expr]))

        return self.process_structure_node(assignment)

    def process_assignment_for_function(self, original_name, name):

        """
        Return an assignment operation making 'original_name' refer to the given
        'name'.
        """

        assignment = compiler.ast.Assign(
            [compiler.ast.AssName(original_name, "OP_ASSIGN")],
            compiler.ast.Name(name)
            )

        return self.process_structure_node(assignment)

    def process_assignment_node_items(self, n, expr):

        """
        Process the given assignment node 'n' whose children are to be assigned
        items of 'expr'.
        """

        name_ref = self.process_structure_node(expr)

        # Either unpack the items and present them directly to each assignment
        # node.

        if isinstance(name_ref, LiteralSequenceRef):
            self.process_literal_sequence_items(n, name_ref)

        # Or have the assignment nodes access each item via the sequence API.

        else:
            self.process_assignment_node_items_by_position(n, expr, name_ref)

    def process_assignment_node_items_by_position(self, n, expr, name_ref):

        """
        Process the given sequence assignment node 'n', converting the node to
        the separate assignment of each target using positional access on a
        temporary variable representing the sequence. Use 'expr' as the assigned
        value and 'name_ref' as the reference providing any existing temporary
        variable.
        """

        assignments = []

        if isinstance(name_ref, NameRef):
            temp = name_ref.name
        else:
            temp = self.get_temporary_name()
            self.next_temporary()

            assignments.append(
                compiler.ast.Assign([compiler.ast.AssName(temp, "OP_ASSIGN")], expr)
                )

        for i, node in enumerate(n.nodes):
            assignments.append(
                compiler.ast.Assign([node], compiler.ast.Subscript(
                    compiler.ast.Name(temp), "OP_APPLY", [compiler.ast.Const(i)]))
                )

        return self.process_structure_node(compiler.ast.Stmt(assignments))

    def process_literal_sequence_items(self, n, name_ref):

        """
        Process the given assignment node 'n', obtaining from the given
        'name_ref' the items to be assigned to the assignment targets.
        """

        if len(n.nodes) == len(name_ref.items):
            for node, item in zip(n.nodes, name_ref.items):
                self.process_assignment_node(node, item)
        else:
            raise InspectError("In %s, item assignment needing %d items is given %d items." % (
                self.get_namespace_path(), len(n.nodes), len(name_ref.items)))

    def process_compare_node(self, n):

        """
        Process the given comparison node 'n', converting an operator sequence
        from...

        <expr1> <op1> <expr2> <op2> <expr3>

        ...to...

        <op1>(<expr1>, <expr2>) and <op2>(<expr2>, <expr3>)
        """

        invocations = []
        last = n.expr

        for op, op_node in n.ops:
            op = operator_functions.get(op)

            invocations.append(compiler.ast.CallFunc(
                compiler.ast.Name("$op%s" % op),
                [last, op_node]))

            last = op_node

        if len(invocations) > 1:
            result = compiler.ast.And(invocations)
        else:
            result = invocations[0]

        return self.process_structure_node(result)

    def process_dict_node(self, node):

        """
        Process the given dictionary 'node', returning a list of (key, value)
        tuples.
        """

        l = []
        for key, value in node.items:
            l.append((
                self.process_structure_node(key),
                self.process_structure_node(value)))
        return l

    def process_for_node(self, n):

        """
        Generate attribute accesses for {n.list}.__iter__ and the next method on
        the iterator, producing a replacement node for the original.
        """

        node = compiler.ast.Stmt([

            # <iterator> = {n.list}.__iter__

            compiler.ast.Assign(
                [compiler.ast.AssName(self.get_iterator_name(), "OP_ASSIGN")],
                compiler.ast.CallFunc(
                    compiler.ast.Getattr(n.list, "__iter__"),
                    []
                    )),

            # try:
            #     while True:
            #         <var>... = <iterator>.next()
            #         ...
            # except StopIteration:
            #     pass

            compiler.ast.TryExcept(
                compiler.ast.While(
                    compiler.ast.Name("True"),
                    compiler.ast.Stmt([
                        compiler.ast.Assign(
                            [n.assign],
                            compiler.ast.CallFunc(
                                compiler.ast.Getattr(compiler.ast.Name(self.get_iterator_name()), "next"),
                                []
                                )),
                        n.body]),
                    None),
                [(compiler.ast.Name("StopIteration"), None, compiler.ast.Stmt([compiler.ast.Pass()]))],
                None)
            ])

        self.next_iterator()
        self.process_structure_node(node)

    def process_literal_sequence_node(self, n, name, ref, cls):

        """
        Process the given literal sequence node 'n' as a function invocation,
        with 'name' indicating the type of the sequence, and 'ref' being a
        reference to the type. The 'cls' is used to instantiate a suitable name
        reference.
        """

        if name == "dict":
            items = []
            for key, value in n.items:
                items.append(compiler.ast.Tuple([key, value]))
        else: # name in ("list", "tuple"):
            items = n.nodes

        return self.get_literal_reference(name, ref, items, cls)

    def process_operator_node(self, n):

        """
        Process the given operator node 'n' as an operator function invocation.
        """

        op = operator_functions[n.__class__.__name__]
        invocation = compiler.ast.CallFunc(
            compiler.ast.Name("$op%s" % op),
            list(n.getChildNodes())
            )
        return self.process_structure_node(invocation)

    def process_slice_node(self, n, expr=None):

        """
        Process the given slice node 'n' as an operator function invocation.
        """

        op = n.flags == "OP_ASSIGN" and "setslice" or "getslice"
        invocation = compiler.ast.CallFunc(
            compiler.ast.Name("$op%s" % op),
            [n.expr, n.lower or compiler.ast.Name("None"), n.upper or compiler.ast.Name("None")] +
                (expr and [expr] or [])
            )
        return self.process_structure_node(invocation)

    def process_sliceobj_node(self, n):

        """
        Process the given slice object node 'n' as a slice constructor.
        """

        op = "slice"
        invocation = compiler.ast.CallFunc(
            compiler.ast.Name("$op%s" % op),
            n.nodes
            )
        return self.process_structure_node(invocation)

    def process_subscript_node(self, n, expr=None):

        """
        Process the given subscript node 'n' as an operator function invocation.
        """

        op = n.flags == "OP_ASSIGN" and "setitem" or "getitem"
        invocation = compiler.ast.CallFunc(
            compiler.ast.Name("$op%s" % op),
            [n.expr] + list(n.subs) + (expr and [expr] or [])
            )
        return self.process_structure_node(invocation)

    def process_attribute_chain(self, n):

        """
        Process the given attribute access node 'n'. Return a reference
        describing the expression.
        """

        # AssAttr/Getattr are nested with the outermost access being the last
        # access in any chain.

        self.attrs.insert(0, n.attrname)
        attrs = self.attrs

        # Break attribute chains where non-access nodes are found.

        if not self.have_access_expression(n):
            self.attrs = []

        # Descend into the expression, extending backwards any existing chain,
        # or building another for the expression.

        name_ref = self.process_structure_node(n.expr)

        # Restore chain information applying to this node.

        self.attrs = attrs

        # Return immediately if the expression was another access and thus a
        # continuation backwards along the chain. The above processing will
        # have followed the chain all the way to its conclusion.

        if self.have_access_expression(n):
            del self.attrs[0]

        return name_ref

    def have_access_expression(self, node):

        "Return whether the expression associated with 'node' is Getattr."

        return isinstance(node.expr, compiler.ast.Getattr)

    def get_name_for_tracking(self, name, path=None):

        """
        Return the name to be used for attribute usage observations involving
        the given 'name' in the current namespace. If 'path' is indicated and
        the name is being used outside a function, return the path value;
        otherwise, return a path computed using the current namespace and the
        given name.

        The intention of this method is to provide a suitably-qualified name
        that can be tracked across namespaces. Where globals are being
        referenced in class namespaces, they should be referenced using their
        path within the module, not using a path within each class.

        It may not be possible to identify a global within a function at the
        time of inspection (since a global may appear later in a file).
        Consequently, globals are identified by their local name rather than
        their module-qualified path.
        """

        # For functions, use the appropriate local names.

        if self.in_function:
            return name

        # For static namespaces, use the given qualified name.

        elif path:
            return path

        # Otherwise, establish a name in the current (module) namespace.

        else:
            return self.get_object_path(name)

    def get_path_for_access(self):

        "Outside functions, register accesses at the module level."

        if not self.in_function:
            return self.name
        else:
            return self.get_namespace_path()

    def get_module_name(self, node):

        """
        Using the given From 'node' in this module, calculate any relative import
        information, returning a tuple containing a module to import along with any
        names to import based on the node's name information.

        Where the returned module is given as None, whole module imports should
        be performed for the returned modules using the returned names.
        """

        # Absolute import.

        if node.level == 0:
            return node.modname, node.names

        # Relative to an ancestor of this module.

        else:
            path = self.name.split(".")
            level = node.level

            # Relative imports treat package roots as submodules.

            if split(self.filename)[-1] == "__init__.py":
                level -= 1

            if level > len(path):
                raise InspectError("Relative import %r involves too many levels up from module %r" % (
                    ("%s%s" % ("." * node.level, node.modname or "")), self.name))

            basename = ".".join(path[:len(path)-level])

        # Name imports from a module.

        if node.modname:
            return "%s.%s" % (basename, node.modname), node.names

        # Relative whole module imports.

        else:
            return basename, node.names

def get_argnames(args):

    """
    Return a list of all names provided by 'args'. Since tuples may be
    employed, the arguments are traversed depth-first.
    """

    l = []
    for arg in args:
        if isinstance(arg, tuple):
            l += get_argnames(arg)
        else:
            l.append(arg)
    return l

# Dictionary utilities.

def init_item(d, key, fn):

    """
    Add to 'd' an entry for 'key' using the callable 'fn' to make an initial
    value where no entry already exists.
    """

    if not d.has_key(key):
        d[key] = fn()
    return d[key]

def dict_for_keys(d, keys):

    "Return a new dictionary containing entries from 'd' for the given 'keys'."

    nd = {}
    for key in keys:
        if d.has_key(key):
            nd[key] = d[key]
    return nd

def make_key(s):

    "Make sequence 's' into a tuple-based key, first sorting its contents."

    l = list(s)
    l.sort()
    return tuple(l)

def add_counter_item(d, key):

    """
    Make a mapping in 'd' for 'key' to the number of keys added before it, thus
    maintaining a mapping of keys to their order of insertion.
    """

    if not d.has_key(key):
        d[key] = len(d.keys())
    return d[key] 

def remove_items(d1, d2):

    "Remove from 'd1' all items from 'd2'."

    for key in d2.keys():
        if d1.has_key(key):
            del d1[key]

# Set utilities.

def first(s):
    return list(s)[0]

def same(s1, s2):
    return set(s1) == set(s2)

# General input/output.

def readfile(filename):

    "Return the contents of 'filename'."

    f = open(filename)
    try:
        return f.read()
    finally:
        f.close()

def writefile(filename, s):

    "Write to 'filename' the string 's'."

    f = open(filename, "w")
    try:
        f.write(s)
    finally:
        f.close()

# General encoding.

def sorted_output(x):

    "Sort sequence 'x' and return a string with commas separating the values."

    x = map(str, x)
    x.sort()
    return ", ".join(x)

# Attribute chain decoding.

def get_attrnames(attrnames):

    """
    Split the qualified attribute chain 'attrnames' into its components,
    handling special attributes starting with "#" that indicate type
    conformance.
    """

    if attrnames.startswith("#"):
        return [attrnames]
    else:
        return attrnames.split(".")

def get_attrname_from_location(location):

    """
    Extract the first attribute from the attribute names employed in a
    'location'.
    """

    path, name, attrnames, access = location
    if not attrnames:
        return attrnames
    return get_attrnames(attrnames)[0]

def get_name_path(path, name):

    "Return a suitable qualified name from the given 'path' and 'name'."

    if "." in name:
        return name
    else:
        return "%s.%s" % (path, name)

# Usage-related functions.

def get_types_for_usage(attrnames, objects):

    """
    Identify the types that can support the given 'attrnames', using the
    given 'objects' as the catalogue of type details.
    """

    types = []
    for name, _attrnames in objects.items():
        if set(attrnames).issubset(_attrnames):
            types.append(name)
    return types

def get_invoked_attributes(usage):

    "Obtain invoked attribute from the given 'usage'."

    invoked = []
    if usage:
        for attrname, invocation, assignment in usage:
            if invocation:
                invoked.append(attrname)
    return invoked

def get_assigned_attributes(usage):

    "Obtain assigned attribute from the given 'usage'."

    assigned = []
    if usage:
        for attrname, invocation, assignment in usage:
            if assignment:
                assigned.append(attrname)
    return assigned

# Useful data.

predefined_constants = "False", "None", "NotImplemented", "True"

operator_functions = {

    # Fundamental operations.

    "is" : "is_",
    "is not" : "is_not",

    # Binary operations.

    "in" : "in_",
    "not in" : "not_in",
    "Add" : "add",
    "Bitand" : "and_",
    "Bitor" : "or_",
    "Bitxor" : "xor",
    "Div" : "div",
    "FloorDiv" : "floordiv",
    "LeftShift" : "lshift",
    "Mod" : "mod",
    "Mul" : "mul",
    "Power" : "pow",
    "RightShift" : "rshift",
    "Sub" : "sub",

    # Unary operations.

    "Invert" : "invert",
    "UnaryAdd" : "pos",
    "UnarySub" : "neg",

    # Augmented assignment.

    "+=" : "iadd",
    "-=" : "isub",
    "*=" : "imul",
    "/=" : "idiv",
    "//=" : "ifloordiv",
    "%=" : "imod",
    "**=" : "ipow",
    "<<=" : "ilshift",
    ">>=" : "irshift",
    "&=" : "iand",
    "^=" : "ixor",
    "|=" : "ior",

    # Comparisons.

    "==" : "eq",
    "!=" : "ne",
    "<" : "lt",
    "<=" : "le",
    ">=" : "ge",
    ">" : "gt",
    }

# vim: tabstop=4 expandtab shiftwidth=4
