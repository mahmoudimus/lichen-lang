#!/usr/bin/env python

"""
Common functions.

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

from compiler.transformer import Transformer
from errors import InspectError
from os import listdir, makedirs, remove
from os.path import exists, isdir, join, split
from results import ConstantValueRef, LiteralSequenceRef, NameRef
import compiler.ast

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
        self.encoding = None
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

        # Retain the assignment value expression and track invocations.

        self.in_assignment = None
        self.in_invocation = False

        # Attribute chain state management.

        self.attrs = []
        self.chain_assignment = []
        self.chain_invocation = []

    def __repr__(self):
        return "CommonModule(%r, %r)" % (self.name, self.importer)

    def parse_file(self, filename):

        "Parse the file with the given 'filename', initialising attributes."

        self.filename = filename

        # Use the Transformer directly to obtain encoding information.

        t = Transformer()
        f = open(filename)

        try:
            self.astnode = t.parsesuite(f.read() + "\n")
            self.encoding = t.encoding
        finally:
            f.close()

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

    def get_constant_name(self, value, value_type, encoding=None):

        """
        Add a new constant to the current namespace for 'value' with
        'value_type'.
        """

        path = self.get_namespace_path()
        init_item(self.constants, path, dict)
        return "$c%d" % add_counter_item(self.constants[path], (value, value_type, encoding))

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

    def get_constant_value(self, value, literals=None):

        """
        Encode the 'value' if appropriate, returning a value, a typename and any
        encoding.
        """

        if isinstance(value, unicode):
            return value.encode("utf-8"), "unicode", self.encoding

        # Attempt to convert plain strings to text.

        elif isinstance(value, str) and self.encoding:
            try:
                return get_string_details(literals, self.encoding)
            except UnicodeDecodeError:
                pass

        return value, value.__class__.__name__, None

    def get_constant_reference(self, ref, value, encoding=None):

        """
        Return a constant reference for the given 'ref' type and 'value', with
        the optional 'encoding' applying to text values.
        """

        constant_name = self.get_constant_name(value, ref.get_origin(), encoding)

        # Return a reference for the constant.

        objpath = self.get_object_path(constant_name)
        name_ref = ConstantValueRef(constant_name, ref.instance_of(objpath), value)

        # Record the value and type for the constant.

        self._reserve_constant(objpath, name_ref.value, name_ref.get_origin(), encoding)
        return name_ref

    def reserve_constant(self, objpath, value, origin, encoding=None):

        """
        Reserve a constant within 'objpath' with the given 'value' and having a
        type with the given 'origin', with the optional 'encoding' applying to
        text values.
        """

        constant_name = self.get_constant_name(value, origin)
        objpath = self.get_object_path(constant_name)
        self._reserve_constant(objpath, value, origin, encoding)

    def _reserve_constant(self, objpath, value, origin, encoding):

        """
        Store a constant for 'objpath' with the given 'value' and 'origin', with
        the optional 'encoding' applying to text values.
        """

        self.constant_values[objpath] = value, origin, encoding

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

    def process_assignment_for_object(self, original_name, source):

        """
        Return an assignment operation making 'original_name' refer to the given
        'source'.
        """

        assignment = compiler.ast.Assign(
            [compiler.ast.AssName(original_name, "OP_ASSIGN")],
            source
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

        if isinstance(name_ref, LiteralSequenceRef) and \
           self.process_literal_sequence_items(n, name_ref):

            pass

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

        # Employ existing names to access the sequence.
        # Literal sequences do not provide names of accessible objects.

        if isinstance(name_ref, NameRef) and not isinstance(name_ref, LiteralSequenceRef):
            temp = name_ref.name

        # For other expressions, create a temporary name to reference the items.

        else:
            temp = self.get_temporary_name()
            self.next_temporary()

            assignments.append(
                compiler.ast.Assign([compiler.ast.AssName(temp, "OP_ASSIGN")], expr)
                )

        # Assign the items to the target nodes.

        for i, node in enumerate(n.nodes):
            assignments.append(
                compiler.ast.Assign([node], compiler.ast.Subscript(
                    compiler.ast.Name(temp), "OP_APPLY", [compiler.ast.Const(i, str(i))]))
                )

        return self.process_structure_node(compiler.ast.Stmt(assignments))

    def process_literal_sequence_items(self, n, name_ref):

        """
        Process the given assignment node 'n', obtaining from the given
        'name_ref' the items to be assigned to the assignment targets.

        Return whether this method was able to process the assignment node as
        a sequence of direct assignments.
        """

        if len(n.nodes) == len(name_ref.items):
            assigned_names, count = get_names_from_nodes(n.nodes)
            accessed_names, _count = get_names_from_nodes(name_ref.items)

            # Only assign directly between items if all assigned names are
            # plain names (not attribute assignments), and if the assigned names
            # do not appear in the accessed names.

            if len(assigned_names) == count and \
               not assigned_names.intersection(accessed_names):

                for node, item in zip(n.nodes, name_ref.items):
                    self.process_assignment_node(node, item)

                return True

            # Otherwise, use the position-based mechanism to obtain values.

            else:
                return False
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

            # <next> = {n.list}.__iter__().next

            compiler.ast.Assign(
                [compiler.ast.AssName(self.get_iterator_name(), "OP_ASSIGN")],
                compiler.ast.Getattr(
                    compiler.ast.CallFunc(
                        compiler.ast.Getattr(n.list, "__iter__"),
                        []
                        ), "next")),

            # try:
            #     while True:
            #         <var>... = <next>()
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
                                compiler.ast.Name(self.get_iterator_name()),
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

    def process_print_node(self, n):

        """
        Process the given print node 'n' as an invocation on a stream of the
        form...

        $print(dest, args, nl)

        The special function name will be translated elsewhere.
        """

        nl = isinstance(n, compiler.ast.Printnl)
        invocation = compiler.ast.CallFunc(
            compiler.ast.Name("$print"),
            [n.dest or compiler.ast.Name("None"),
             compiler.ast.List(list(n.nodes)),
             nl and compiler.ast.Name("True") or compiler.ast.Name("False")]
            )
        return self.process_structure_node(invocation)

    def process_slice_node(self, n, expr=None):

        """
        Process the given slice node 'n' as an operator function invocation.
        """

        if n.flags == "OP_ASSIGN": op = "setslice"
        elif n.flags == "OP_DELETE": op = "delslice"
        else: op = "getslice"

        invocation = compiler.ast.CallFunc(
            compiler.ast.Name("$op%s" % op),
            [n.expr, n.lower or compiler.ast.Name("None"), n.upper or compiler.ast.Name("None")] +
                (expr and [expr] or [])
            )

        # Fix parse tree structure.

        if op == "delslice":
            invocation = compiler.ast.Discard(invocation)

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

        if n.flags == "OP_ASSIGN": op = "setitem"
        elif n.flags == "OP_DELETE": op = "delitem"
        else: op = "getitem"

        invocation = compiler.ast.CallFunc(
            compiler.ast.Name("$op%s" % op),
            [n.expr] + list(n.subs) + (expr and [expr] or [])
            )

        # Fix parse tree structure.

        if op == "delitem":
            invocation = compiler.ast.Discard(invocation)

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
            self.reset_attribute_chain()

        # Descend into the expression, extending backwards any existing chain,
        # or building another for the expression.

        name_ref = self.process_structure_node(n.expr)

        # Restore chain information applying to this node.

        if not self.have_access_expression(n):
            self.restore_attribute_chain(attrs)

        # Return immediately if the expression was another access and thus a
        # continuation backwards along the chain. The above processing will
        # have followed the chain all the way to its conclusion.

        if self.have_access_expression(n):
            del self.attrs[0]

        return name_ref

    # Attribute chain handling.

    def reset_attribute_chain(self):

        "Reset the attribute chain for a subexpression of an attribute access."

        self.attrs = []
        self.chain_assignment.append(self.in_assignment)
        self.chain_invocation.append(self.in_invocation)
        self.in_assignment = None
        self.in_invocation = False

    def restore_attribute_chain(self, attrs):

        "Restore the attribute chain for an attribute access."

        self.attrs = attrs
        self.in_assignment = self.chain_assignment.pop()
        self.in_invocation = self.chain_invocation.pop()

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

        # Otherwise, establish a name in the current namespace.

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

def get_names_from_nodes(nodes):

    """
    Return the names employed in the given 'nodes' along with the number of
    nodes excluding sequences.
    """

    names = set()
    count = 0

    for node in nodes:

        # Add names and count them.

        if isinstance(node, (compiler.ast.AssName, compiler.ast.Name)):
            names.add(node.name)
            count += 1

        # Add names from sequences and incorporate their counts.

        elif isinstance(node, (compiler.ast.AssList, compiler.ast.AssTuple,
                               compiler.ast.List, compiler.ast.Set,
                               compiler.ast.Tuple)):
            _names, _count = get_names_from_nodes(node.nodes)
            names.update(_names)
            count += _count

        # Count non-name, non-sequence nodes.

        else:
            count += 1

    return names, count

# Result classes.

class InstructionSequence:

    "A generic sequence of instructions."

    def __init__(self, instructions):
        self.instructions = instructions

    def get_value_instruction(self):
        return self.instructions[-1]

    def get_init_instructions(self):
        return self.instructions[:-1]

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

def get_string_details(literals, encoding):

    """
    Determine whether 'literals' represent Unicode strings or byte strings,
    using 'encoding' to reproduce byte sequences.

    Each literal is the full program representation including prefix and quotes
    recoded by the parser to UTF-8. Thus, any literal found to represent a byte
    string needs to be translated back to its original encoding.

    Return a single encoded literal value, a type name, and the original
    encoding as a tuple.
    """

    typename = "unicode"

    l = []

    for s in literals:
        out, _typename = get_literal_details(s)
        if _typename == "str":
            typename = "str"
        l.append(out)

    out = "".join(l)

    # For Unicode values, convert to the UTF-8 program representation.

    if typename == "unicode":
        return out.encode("utf-8"), typename, encoding

    # For byte string values, convert back to the original encoding.

    else:
        return out.encode(encoding), typename, encoding

def get_literal_details(s):

    """
    Determine whether 's' represents a Unicode string or a byte string, where
    's' contains the full program representation of a literal including prefix
    and quotes, recoded by the parser to UTF-8.

    Find and convert Unicode values starting with <backslash>u or <backslash>U,
    and byte or Unicode values starting with <backslash><octal digit> or
    <backslash>x.

    Literals prefixed with "u" cause <backslash><octal digit> and <backslash>x
    to be considered as Unicode values. Otherwise, they produce byte values and
    cause unprefixed strings to be considered as byte strings.

    Literals prefixed with "r" do not have their backslash-encoded values
    converted unless also prefixed with "u", in which case only the above value
    formats are converted, not any of the other special sequences for things
    like newlines.

    Return the literal value as a Unicode object together with the appropriate
    type name in a tuple.
    """

    l = []

    # Identify the quote character and use it to identify the prefix.

    quote_type = s[-1]
    prefix_end = s.find(quote_type)
    prefix = s[:prefix_end].lower()

    if prefix not in ("", "b", "br", "r", "u", "ur"):
        raise ValueError, "String literal does not have a supported prefix: %s" % s

    if "b" in prefix:
        typename = "str"
    else:
        typename = "unicode"

    # Identify triple quotes or single quotes.

    if len(s) >= 6 and s[-2] == quote_type and s[-3] == quote_type:
        quote = s[prefix_end:prefix_end+3]
        current = prefix_end + 3
        end = len(s) - 3
    else:
        quote = s[prefix_end]
        current = prefix_end + 1
        end = len(s) - 1

    # Conversions of some quoted values.

    searches = {
        "u" : (6, 16),
        "U" : (10, 16),
        "x" : (4, 16),
        }

    octal_digits = map(str, range(0, 8))

    # Translations of some quoted values.

    escaped = {
        "\\" : "\\", "'" : "'", '"' : '"',
        "a" : "\a", "b" : "\b", "f" : "\f",
        "n" : "\n", "r" : "\r", "t" : "\t",
        }

    while current < end:

        # Look for quoted values.

        index = s.find("\\", current)
        if index == -1 or index + 1 == end:
            l.append(s[current:end])
            break

        # Add the preceding text.

        l.append(s[current:index])

        # Handle quoted text.

        term = s[index+1]

        # Add Unicode values. Where a string is u-prefixed, even \o and \x
        # produce Unicode values.

        if typename == "unicode" and (
            term in ("u", "U") or 
            "u" in prefix and (term == "x" or term in octal_digits)):

            needed, base = searches.get(term, (4, 8))
            value = convert_quoted_value(s, index, needed, end, base, unichr)
            l.append(value)
            current = index + needed

        # Add raw byte values, changing the string type.

        elif "r" not in prefix and (
             term == "x" or term in octal_digits):

            needed, base = searches.get(term, (4, 8))
            value = convert_quoted_value(s, index, needed, end, base, chr)
            l.append(value)
            typename = "str"
            current = index + needed

        # Add other escaped values.

        elif "r" not in prefix and escaped.has_key(term):
            l.append(escaped[term])
            current = index + 2

        # Add other text as found.

        else:
            l.append(s[index:index+2])
            current = index + 2

    # Collect the components into a single Unicode object. Since the literal
    # text was already in UTF-8 form, interpret plain strings as UTF-8
    # sequences.

    out = []

    for value in l:
        if isinstance(value, unicode):
            out.append(value)
        else:
            out.append(unicode(value, "utf-8"))

    return "".join(out), typename

def convert_quoted_value(s, index, needed, end, base, fn):

    """
    Interpret a quoted value in 's' at 'index' with the given 'needed' number of
    positions, and with the given 'end' indicating the first position after the
    end of the actual string content.

    Use 'base' as the numerical base when interpreting the value, and use 'fn'
    to convert the value to an appropriate type.
    """

    s = s[index:min(index+needed, end)]

    # Not a complete occurrence.

    if len(s) < needed:
        return s

    # Test for a well-formed value.

    try:
        first = base == 8 and 1 or 2
        value = int(s[first:needed], base)
    except ValueError:
        return s
    else:
        return fn(value)

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

# Type and module functions.
# NOTE: This makes assumptions about the __builtins__ structure.

def get_builtin_module(name):

    "Return the module name containing the given type 'name'."

    if name == "string":
        modname = "str"
    elif name == "utf8string":
        modname = "unicode"
    elif name == "NoneType":
        modname = "none"
    else:
        modname = name

    return "__builtins__.%s" % modname

def get_builtin_type(name):

    "Return the type name provided by the given Python value 'name'."

    if name == "str":
        return "string"
    elif name == "unicode":
        return "utf8string"
    else:
        return name

def get_builtin_class(name):

    "Return the full name of the built-in class having the given 'name'."

    typename = get_builtin_type(name)
    module = get_builtin_module(typename)
    return "%s.%s" % (module, typename)

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
