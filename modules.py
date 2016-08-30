#!/usr/bin/env python

"""
Module abstractions.

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

from common import *
from encoders import decode_modifier_term, encode_modifiers, encode_usage
from referencing import decode_reference, Reference
import sys

class BasicModule(CommonModule):

    "The basic module information."

    def __init__(self, name, importer):
        CommonModule.__init__(self, name, importer)

        # Import machinery links.

        self.loaded = False

        # Module dependencies.

        self.imported = set()
        self.imported_hidden = set()
        self.imported_names = {}
        self.revealed = set()
        self.accessing_modules = set()

        # Global name information.

        self.objects = {}
        self.special = {}

        # Class relationships.

        self.classes = {}

        # Attributes.

        self.class_attrs = {}
        self.instance_attrs = {}
        self.instance_attr_constants = {}
        self.module_attrs = set()

        # Names used and missing.

        self.names_used = {}
        self.names_missing = {}
        self.name_references = {} # references to globals

        # Function details.

        self.function_parameters = {}
        self.function_defaults = {}
        self.function_locals = {}
        self.scope_globals = {}

        # Invocation details.

        self.function_targets = {}
        self.function_arguments = {}

        # Attribute usage at module and function levels.

        self.attr_usage = {}
        self.name_initialisers = {}

        # General attribute access expressions.

        self.attr_accesses = {}
        self.const_accesses = {}

        # Attribute accessor definition details.

        self.attr_accessors = {}

        # Assignment details for accesses.

        self.attr_access_modifiers = {}

        # Initialisation-related details.

        self.initialised_names = {}
        self.aliased_names = {}

    def __repr__(self):
        return "BasicModule(%r, %r)" % (self.name, self.importer)

    def resolve(self):

        "Resolve dependencies and complete definitions."

        self.resolve_class_bases()
        self.check_special()
        self.check_names_used()
        self.resolve_members()
        self.resolve_initialisers()
        self.resolve_literals()
        self.remove_redundant_accessors()
        self.set_invocation_usage()

        # Propagate to the importer information needed in subsequent activities.

        self.propagate()

    # Derived information methods.

    def propagate(self):

        "Finalise and propagate module information."

        self.propagate_attrs()
        self.propagate_name_references()
        self.propagate_attr_accesses()
        self.propagate_constants()

    def unpropagate(self):

        """
        Retract information from the importer including information about this
        module derived by the importer.
        """

        del self.importer.all_module_attrs[self.name]

        for name in self.classes.keys():
            del self.importer.all_class_attrs[name]
            del self.importer.all_instance_attrs[name]
            del self.importer.all_combined_attrs[name]
            del self.importer.all_instance_attr_constants[name]

            for name, bases in self.classes.items():
                for base in bases:

                    # Get the identity of the class from the reference.

                    base = base.get_origin()

                    try:
                        self.importer.subclasses[base].remove(name)
                    except (KeyError, ValueError):
                        pass

        remove_items(self.importer.all_name_references, self.name_references)
        remove_items(self.importer.all_initialised_names, self.initialised_names)
        remove_items(self.importer.all_aliased_names, self.aliased_names)
        remove_items(self.importer.all_attr_accesses, self.attr_accesses)
        remove_items(self.importer.all_const_accesses, self.const_accesses)
        remove_items(self.importer.all_attr_access_modifiers, self.attr_access_modifiers)
        remove_items(self.importer.all_constants, self.constants)
        remove_items(self.importer.all_constant_values, self.constant_values)

        # Remove this module's objects from the importer. Objects are
        # automatically propagated when defined.

        for name, ref in self.objects.items():
            if ref.provided_by_module(self.name) or name in self.importer.hidden:
                if ref.get_kind() != "<module>":
                    del self.importer.objects[name]

    def resolve_class_bases(self):

        "Resolve all class bases since some of them may have been deferred."

        for name, bases in self.classes.items():
            resolved = []
            bad = []

            for base in bases:

                # Resolve dependencies.

                if base.has_kind("<depends>"):
                    ref = self.importer.get_object(base.get_origin())
                else:
                    ref = base

                # Obtain the origin of the base class reference.

                if not ref or not ref.has_kind("<class>"):
                    bad.append(base)
                    break

                resolved.append(ref)

            if bad:
                print >>sys.stderr, "Bases of class %s were not classes." % (name, ", ".join(map(str, bad)))
            else:
                self.importer.classes[name] = self.classes[name] = resolved

    def propagate_attrs(self):

        "Derive attributes from the class and module member details."

        # Initialise class attribute records for all classes.

        for name in self.classes.keys():
            self.importer.all_class_attrs[name] = self.class_attrs[name] = {}

        # Separate the objects into module and class attributes.

        for name in self.objects.keys():
            if "." in name:
                parent, attrname = name.rsplit(".", 1)
                if self.classes.has_key(parent):
                    self.class_attrs[parent][attrname] = name
                elif parent == self.name:
                    self.module_attrs.add(attrname)

        # Propagate the module attributes.

        self.importer.all_module_attrs[self.name] = self.module_attrs

    def propagate_name_references(self):

        "Propagate name references for the module."

        self.importer.all_name_references.update(self.name_references)
        self.importer.all_initialised_names.update(self.initialised_names)
        self.importer.all_aliased_names.update(self.aliased_names)

    def propagate_attr_accesses(self):

        "Propagate attribute accesses for the module."

        self.importer.all_attr_accesses.update(self.attr_accesses)
        self.importer.all_const_accesses.update(self.const_accesses)
        self.importer.all_attr_access_modifiers.update(self.attr_access_modifiers)

    def propagate_constants(self):

        "Propagate constant values and aliases for the module."

        self.importer.all_constants.update(self.constants)
        self.importer.all_constant_values.update(self.constant_values)

        for name in self.classes.keys():
            self.importer.all_instance_attrs[name] = self.instance_attrs.get(name) or {}
            self.importer.all_instance_attr_constants[name] = self.instance_attr_constants.get(name) or {}

    # Module-relative naming.

    def is_global(self, name):

        """
        Return whether 'name' is registered as a global in the current
        namespace.
        """

        path = self.get_namespace_path()
        return name in self.scope_globals.get(path, [])

    def get_globals(self):

        """
        Get the globals from this module, returning a dictionary mapping names
        to references incorporating original definition details.
        """

        l = []
        for name, value in self.objects.items():
            parent, attrname = name.rsplit(".", 1)
            if parent == self.name:
                l.append((attrname, value))
        return dict(l)

    def get_global(self, name):

        """
        Get the global of the given 'name' from this module, returning a
        reference incorporating the original definition details.
        """

        path = self.get_global_path(name)
        return self.objects.get(path)

    # Name definition discovery.

    def get_global_or_builtin(self, name):

        """
        Return the object recorded the given 'name' from this module or from the
        __builtins__ module. If no object has yet been defined, perhaps due to
        circular module references, None is returned.
        """

        return self.get_global(name) or self.get_builtin(name)

    def get_builtin(self, name):

        "Return the object providing the given built-in 'name'."

        path = "__builtins__.%s" % name

        # Obtain __builtins__.

        module = self.ensure_builtins(path)

        # Attempt to find the named object within __builtins__.

        if module:
            self.find_imported_name(name, module.name, module)

        # Return the path and any reference for the named object.

        return self.importer.get_object(path)

    def ensure_builtins(self, path):

        """
        If 'path' is a reference to an object within __builtins__, return the
        __builtins__ module.
        """

        if path.split(".", 1)[0] == "__builtins__":
            return self.importer.load("__builtins__", True, True)
        else:
            return None

    def get_object(self, path):

        """
        Get the details of an object with the given 'path', either from this
        module or from the whole program. Return a tuple containing the path and
        any object found.
        """

        if self.objects.has_key(path):
            return self.objects[path]
        else:
            self.ensure_builtins(path)
            return self.importer.get_object(path)

    def set_object(self, name, value=None):

        "Set an object with the given 'name' and the given 'value'."

        ref = decode_reference(value, name)
        multiple = self.objects.has_key(name) and self.objects[name].get_kind() != ref.get_kind()
        self.importer.objects[name] = self.objects[name] = multiple and ref.as_var() or ref

    # Special names.

    def get_special(self, name):

        "Return any stored value for the given special 'name'."

        return self.special.get(name)

    def set_special(self, name, value):

        """
        Set a special 'name' that merely tracks the use of an implicit object
        'value'.
        """

        self.special[name] = value

    def set_special_literal(self, name, ref):

        """
        Set a special name for the literal type 'name' having type 'ref'. Such
        special names provide a way of referring to literal object types.
        """

        literal_name = "$L%s" % name
        value = ResolvedNameRef(literal_name, ref)
        self.set_special(literal_name, value)

    # Revealing modules by tracking name imports across modules.

    def set_imported_name(self, name, module_name, alias=None, path=None):

        """
        Record 'name' as being imported from the given 'module_name', employing
        the given 'alias' in the local namespace if specified.
        """

        path = path or self.get_namespace_path()
        init_item(self.imported_names, path, dict)
        self.imported_names[path][alias or name] = (name, module_name)

    def get_imported_name(self, name, path):

        "Get details of any imported 'name' within the namespace at 'path'."

        if self.imported_names.has_key(path):
            return self.imported_names[path].get(name)
        else:
            return None

    def find_imported_name(self, name, path, module=None):

        """
        Find details of the imported 'name' within the namespace at 'path',
        starting within the given 'module' if indicated, or within this module
        otherwise.
        """

        module = module or self

        # Obtain any module required by the name.

        name_modname = module.get_imported_name(name, path)

        if name_modname:
            name, modname = name_modname
            module = self._find_imported_name(name, modname, module)

        # Obtain the name from the final module, revealing it if appropriate.

        if module:
            init_item(self.importer.revealing, module.name, set)
            self.importer.set_revealing(module, name, self)

    def _find_imported_name(self, name, modname, module):

        """
        Traverse details for 'name' via 'modname' to the module providing the
        name, tentatively revealing the module even if the module is not yet
        loaded and cannot provide the details of the object recorded for the
        name.
        """

        _name = name

        # Obtain any modules referenced by each required module.

        while True:

            # Get the module directly or traverse possibly-aliased names.

            module = self.get_module_direct(modname, True)
            if not module:
                top, module = self.get_module(modname, True)
            name_modname = module.get_imported_name(_name, module.name)
            if not name_modname:
                break
            else:
                _name, modname = name_modname

        return module

    def reveal_referenced(self):

        """
        Reveal modules referenced by this module.
        """

        for path, names in self.imported_names.items():
            for alias, (name, modname) in names.items():
                module = self._find_imported_name(name, modname, self)
                self.reveal_module(module)

    def reveal_module(self, module):

        """
        Reveal the given 'module', recording the revealed modules on this
        module.
        """

        if module is not self:
            self.importer.reveal_module(module)
            self.revealed.add(module)
            module.accessing_modules.add(self.name)

    # Module loading.

    def get_module_direct(self, modname, hidden=False):

        """
        Return 'modname' without traversing parent modules, keeping the module
        'hidden' if set to a true value, loading the module if not already
        loaded.
        """

        return self.importer.get_module(modname, True) or self.importer.load(modname, hidden=hidden)

    def get_module(self, name, hidden=False):

        """
        Use the given 'name' to obtain the identity of a module. Return module
        objects or None if the module cannot be found. This method is required
        when aliases are used to refer to modules and where a module "path" does
        not correspond to the actual module path.

        A tuple is returned containing the top or base module and the deepest or
        leaf module involved.
        """

        path_so_far = []
        top = module = None
        parts = name.split(".")

        for i, part in enumerate(parts):
            path_so_far.append(part)
            module_name = ".".join(path_so_far)
            ref = self.get_object(module_name)

            # If no known object exists, attempt to load it.

            if not ref:
                module = self.importer.load(module_name, True, hidden)
                if not module:
                    return None

                # Rewrite the path to use the actual module details.

                path_so_far = module.name.split(".")

            # If the object exists and is not a module, stop.

            elif ref.has_kind(["<class>", "<function>", "<var>"]):
                return None

            else:
                module = self.importer.get_module(ref.get_origin(), hidden)

            if not top:
                top = module

        return top, module

class CachedModule(BasicModule):

    "A cached module."

    def __repr__(self):
        return "CachedModule(%r, %r)" % (self.name, self.importer)

    def resolve(self):
        pass

    def to_cache(self, filename):

        "Not actually writing the module back to 'filename'."

        pass

    def from_cache(self, filename):

        """
        Read a module's details from the file with the given 'filename' as
        described in the to_cache method of InspectedModule.
        """

        f = open(filename)
        try:
            self.filename = f.readline().rstrip()

            accessing_modules = f.readline().split(": ", 1)[-1].rstrip()

            module_names = f.readline().split(": ", 1)[-1].rstrip()
            if module_names:
                for module_name in module_names.split(", "):
                    self.imported.add(self.importer.load(module_name))

            module_names = f.readline().split(": ", 1)[-1].rstrip()
            if module_names:
                for module_name in module_names.split(", "):
                    self.imported_hidden.add(self.importer.load(module_name, hidden=True))

            module_names = f.readline().split(": ", 1)[-1].rstrip()
            if module_names:
                for module_name in module_names.split(", "):
                    module = self.importer.load(module_name, True, True)
                    self.reveal_module(module)

            f.readline() # (empty line)

            self._get_imported_names(f)
            self._get_members(f)
            self._get_class_relationships(f)
            self._get_instance_attrs(f)
            self._get_instance_attr_constants(f)
            self.from_lines(f, self.names_used)     # "names used:"
            self.from_lines(f, self.names_missing)  # "names missing:"
            self._get_name_references(f)
            self._get_initialised_names(f)
            self._get_aliased_names(f)
            self._get_function_parameters(f)
            self._get_function_defaults(f)
            self._get_function_locals(f)
            self.from_lines(f, self.scope_globals)  # "scope globals:"
            self._get_function_targets(f)
            self._get_function_arguments(f)
            self._get_attribute_usage(f)
            self._get_attr_accesses(f)
            self._get_const_accesses(f)
            self._get_attr_accessors(f)
            self._get_attr_access_modifiers(f)
            self._get_constant_literals(f)
            self._get_constant_values(f)

        finally:
            f.close()

        self.loaded = True

    def resolve(self):
        self.propagate()

    def _get_imported_names(self, f):
        f.readline() # "imported names:"
        line = f.readline().rstrip()
        while line:
            path, alias_or_name, name, module_name = self._get_fields(line, 4)
            init_item(self.imported_names, path, dict)
            self.imported_names[path][alias_or_name] = (name, module_name)
            line = f.readline().rstrip()

    def _get_members(self, f):
        f.readline() # "members:"
        line = f.readline().rstrip()
        while line:
            name, ref = line.split(" ", 1)
            self.set_object(name, ref)
            line = f.readline().rstrip()

    def _get_class_relationships(self, f):
        f.readline() # "class relationships:"
        line = f.readline().rstrip()
        while line:
            name, value = self._get_fields(line)
            values = value and value.split(", ") or []
            self.importer.classes[name] = self.classes[name] = map(decode_reference, values)
            self.importer.subclasses[name] = set()
            line = f.readline().rstrip()

    def _get_instance_attrs(self, f):
        f.readline() # "instance attributes:"
        line = f.readline().rstrip()
        while line:
            name, value = self._get_fields(line)
            self.importer.all_instance_attrs[name] = self.instance_attrs[name] = set(value and value.split(", ") or [])
            line = f.readline().rstrip()

    def _get_instance_attr_constants(self, f):
        f.readline() # "instance attribute constants:"
        line = f.readline().rstrip()
        while line:
            name, attrname, ref = self._get_fields(line, 3)
            init_item(self.instance_attr_constants, name, dict)
            self.instance_attr_constants[name][attrname] = decode_reference(ref)
            line = f.readline().rstrip()

    def _get_name_references(self, f):
        f.readline() # "name references:"
        line = f.readline().rstrip()
        while line:
            name, value = self._get_fields(line)
            self.name_references[name] = value
            line = f.readline().rstrip()

    def _get_initialised_names(self, f):
        f.readline() # "initialised names:"
        line = f.readline().rstrip()
        while line:
            name, version, value = self._get_fields(line, 3)
            init_item(self.initialised_names, name, dict)
            self.initialised_names[name][int(version)] = decode_reference(value)
            line = f.readline().rstrip()

    def _get_aliased_names(self, f):
        f.readline() # "aliased names:"
        line = f.readline().rstrip()
        while line:
            name, version, original_name, attrnames, number = self._get_fields(line, 5)
            init_item(self.aliased_names, name, dict)
            if number == "{}": number = None
            else: number = int(number)
            self.aliased_names[name][int(version)] = (original_name, attrnames != "{}" and attrnames or None, number)
            line = f.readline().rstrip()

    def _get_function_parameters(self, f):
        f.readline() # "function parameters:"
        line = f.readline().rstrip()
        while line:
            function, names = self._get_fields(line)
            self.importer.function_parameters[function] = \
                self.function_parameters[function] = names and names.split(", ") or []
            line = f.readline().rstrip()

    def _get_function_defaults(self, f):
        f.readline() # "function default parameters:"
        line = f.readline().rstrip()
        while line:
            function, defaults = self._get_fields(line)
            self.importer.function_defaults[function] = \
                self.function_defaults[function] = l = []
            if defaults != "{}":
                for value in defaults.split(", "):
                    name, default = value.split("=")
                    default = decode_reference(default)
                    l.append((name, default))
            line = f.readline().rstrip()

    def _get_function_locals(self, f):
        f.readline() # "function locals:"
        line = f.readline().rstrip()
        while line:
            function, name, value = self._get_fields(line, 3)
            init_item(self.function_locals, function, dict)
            if name != "{}":
                self.function_locals[function][name] = decode_reference(value)
            line = f.readline().rstrip()

    def _get_function_targets(self, f):
        f.readline() # "function targets:"
        line = f.readline().rstrip()
        while line:
            function, n = self._get_fields(line)
            self.importer.function_targets[function] = \
                self.function_targets[function] = int(n)
            line = f.readline().rstrip()

    def _get_function_arguments(self, f):
        f.readline() # "function arguments:"
        line = f.readline().rstrip()
        while line:
            function, n = self._get_fields(line)
            self.importer.function_arguments[function] = \
                self.function_arguments[function] = int(n)
            line = f.readline().rstrip()

    def _get_attribute_usage(self, f):
        f.readline() # "attribute usage:"
        line = f.readline().rstrip()
        while line:
            unit, value = self._get_fields(line)
            init_item(self.attr_usage, unit, dict)
            self.usage_from_cache(value, self.attr_usage[unit])
            line = f.readline().rstrip()

    def _get_attr_accesses(self, f):
        f.readline() # "attribute accesses:"
        line = f.readline().rstrip()
        while line:
            name, value = self._get_fields(line)
            self.attr_accesses[name] = set(value.split(", "))
            line = f.readline().rstrip()

    def _get_const_accesses(self, f):
        f.readline() # "constant accesses:"
        line = f.readline().rstrip()
        while line:
            name, original_name, attrnames, objpath, ref, remaining = self._get_fields(line, 6)
            if attrnames == "{}": attrnames = None
            init_item(self.const_accesses, name, dict)
            self.const_accesses[name][(original_name, attrnames)] = (objpath, decode_reference(ref), remaining != "{}" and remaining or "")
            line = f.readline().rstrip()

    def _get_attr_accessors(self, f):
        f.readline() # "attribute access usage:"
        line = f.readline().rstrip()
        while line:
            objpath, name, attrname, value = self._get_fields(line, 4)
            if attrname == "{}": attrname = None
            access = name, attrname
            init_item(self.attr_accessors, objpath, dict)
            init_item(self.attr_accessors[objpath], access, list)
            positions = map(int, value.split(", "))
            self.attr_accessors[objpath][access].append(positions)
            line = f.readline().rstrip()

    def _get_attr_access_modifiers(self, f):
        f.readline() # "attribute access modifiers:"
        line = f.readline().rstrip()
        while line:
            objpath, name, attrnames, value = self._get_fields(line, 4)
            if name == "{}": name = None
            if attrnames == "{}": attrnames = None
            access = name, attrnames
            init_item(self.attr_access_modifiers, objpath, dict)
            init_item(self.attr_access_modifiers[objpath], access, list)
            modifiers = [decode_modifier_term(s) for s in value]
            self.attr_access_modifiers[objpath][access] = modifiers
            line = f.readline().rstrip()

    def _get_constant_literals(self, f):
        f.readline() # "constant literals:"
        line = f.readline().rstrip()
        last_path = None
        n = None
        while line:
            path, constant = self._get_fields(line)
            if path != last_path:
                n = 0
                last_path = path
            else:
                n += 1
            init_item(self.constants, path, dict)
            self.constants[path][eval(constant)] = n
            line = f.readline().rstrip()

    def _get_constant_values(self, f):
        f.readline() # "constant values:"
        line = f.readline().rstrip()
        while line:
            name, value_type, value = self._get_fields(line, 3)
            self.constant_values[name] = eval(value), value_type
            line = f.readline().rstrip()

    # Generic parsing methods.

    def from_lines(self, f, d):

        "Read lines from 'f', populating 'd'."

        f.readline() # section heading
        line = f.readline().rstrip()
        while line:
            name, value = self._get_fields(line)
            d[name] = set(value and value.split(", ") or [])
            line = f.readline().rstrip()

    def usage_from_cache(self, value, mapping):

        """
        Interpret the given 'value' containing name and usage information,
        storing the information in the given 'mapping'.
        """

        local, usage = self._get_fields(value)
        init_item(mapping, local, list)
        self._usage_from_cache(mapping[local], usage)

    def _usage_from_cache(self, d, usage):

        # Interpret descriptions of each version of the name.

        all_usages = set()
        for attrnames in usage.split("; "):
            if attrnames == "{}":
                all_attrnames = ()
            else:
                # Decode attribute details for each usage description.

                all_attrnames = set()
                for attrname_str in attrnames.split(", "):
                    all_attrnames.add(attrname_str)

                all_attrnames = list(all_attrnames)
                all_attrnames.sort()

            all_usages.add(tuple(all_attrnames))

        d.append(all_usages)

    def _get_fields(self, s, n=2):
        result = s.split(" ", n-1)
        if len(result) == n:
            return result
        else:
            return tuple(result) + tuple([""] * (n - len(result)))

class CacheWritingModule:

    """
    A mix-in providing cache-writing support, to be combined with BasicModule.
    """

    def to_cache(self, filename):

        """
        Write a cached representation of the inspected module with the following
        format to the file having the given 'filename':

        filename
        "accessed by:" accessing module names during this module's import
        "imports:" imported module names
        "hidden imports:" imported module names
        "reveals:" revealed module names
        (empty line)
        "imported names:"
        zero or more: qualified name " " name " " module name
        (empty line)
        "members:"
        zero or more: qualified name " " reference
        (empty line)
        "class relationships:"
        zero or more: qualified class name " " base class references
        (empty line)
        "instance attributes:"
        zero or more: qualified class name " " instance attribute names
        (empty line)
        "instance attribute constants:"
        zero or more: qualified class name " " attribute name " " reference
        (empty line)
        "names used:"
        zero or more: qualified class/function/module name " " names
        (empty line)
        "names missing:"
        zero or more: qualified class/function/module name " " names
        (empty line)
        "name references:"
        zero or more: qualified name " " reference
        (empty line)
        "initialised names:"
        zero or more: qualified name " " definition version " " reference
        (empty line)
        "aliased names:"
        zero or more: qualified name " " definition version " " original name " " attribute names " " access number
        (empty line)
        "function parameters:"
        zero or more: qualified function name " " parameter names
        (empty line)
        "function default parameters:"
        zero or more: qualified function name " " parameter names with defaults
        (empty line)
        "function locals:"
        zero or more: qualified function name " " local variable name " " reference
        (empty line)
        "scope globals:"
        zero or more: qualified function name " " global variable names
        (empty line)
        "function targets:"
        zero or more: qualified function name " " maximum number of targets allocated
        (empty line)
        "function arguments:"
        zero or more: qualified function name " " maximum number of arguments allocated
        (empty line)
        "attribute usage:"
        zero or more: qualified scope name " " local/global/qualified variable name " " usages
        (empty line)
        "attribute accesses:"
        zero or more: qualified scope name " " attribute-chains
        (empty line)
        "constant accesses:"
        zero or more: qualified function name " " attribute-chain " " reference " " remaining attribute-chain
        (empty line)
        "attribute access usage:"
        zero or more: qualified function name " " local/global variable name " " attribute name " " definition versions
        (empty line)
        "attribute access modifiers:"
        zero or more: qualified function name " " local/global variable name " " attribute name " " access modifiers
        "constant literals:"
        zero or more: qualified scope name " " constant literal
        "constant values:"
        zero or more: qualified name " " value type " " constant literal

        All collections of names are separated by ", " characters.

        References can be "<var>", a module name, or one of "<class>" or
        "<function>" followed optionally by a ":" character and a qualified
        name.

        Parameter names with defaults are separated by ", " characters, with
        each name followed by "=" and then followed by a reference. If "{}" is
        indicated, no defaults are defined for the function. Similarly, function
        locals may be indicated as "{}" meaning that there are no locals.

        All usages (attribute usage sets) are separated by "; " characters, with
        the special string "{}" representing an empty set.

        Each usage is a collection of names separated by ", " characters, with
        assigned attribute names suffixed with a "*" character.

        Each attribute-chain expression is a dot-separated chain of attribute
        names, with assignments suffixed with a "*" character.

        Definition versions are separated by ", " characters and indicate the
        name definition version associated with the access.

        Access modifiers are separated by ", " characters and indicate features
        of each access, with multiple accesses described on a single line.
        """

        f = open(filename, "w")
        try:
            print >>f, self.filename

            accessing_modules = list(self.accessing_modules)
            accessing_modules.sort()
            print >>f, "accessed by:", ", ".join(accessing_modules)

            module_names = [m.name for m in self.imported]
            module_names.sort()
            print >>f, "imports:", ", ".join(module_names)

            module_names = [m.name for m in self.imported_hidden]
            module_names.sort()
            print >>f, "hidden imports:", ", ".join(module_names)

            module_names = [m.name for m in self.revealed]
            module_names.sort()
            print >>f, "reveals:", ", ".join(module_names)

            print >>f
            print >>f, "imported names:"
            paths = self.imported_names.keys()
            paths.sort()
            for path in paths:
                names = self.imported_names[path].keys()
                names.sort()
                for alias_or_name in names:
                    name, modname = self.imported_names[path][alias_or_name]
                    print >>f, path, alias_or_name, name, modname

            print >>f
            print >>f, "members:"
            objects = self.objects.keys()
            objects.sort()
            for name in objects:
                print >>f, name, self.objects[name]

            print >>f
            print >>f, "class relationships:"
            classes = self.classes.keys()
            classes.sort()
            for class_ in classes:
                bases = self.classes[class_]
                if bases:
                    print >>f, class_, ", ".join(map(str, bases))
                else:
                    print >>f, class_

            self.to_lines(f, "instance attributes:", self.instance_attrs)

            print >>f
            print >>f, "instance attribute constants:"
            classes = self.instance_attr_constants.items()
            classes.sort()
            for name, attrs in classes:
                attrs = attrs.items()
                attrs.sort()
                for attrname, ref in attrs:
                    print >>f, name, attrname, ref

            self.to_lines(f, "names used:", self.names_used)
            self.to_lines(f, "names missing:", self.names_missing)

            print >>f
            print >>f, "name references:"
            refs = self.name_references.items()
            refs.sort()
            for name, ref in refs:
                print >>f, name, ref

            print >>f
            print >>f, "initialised names:"
            assignments = self.initialised_names.items()
            assignments.sort()
            for name, refs in assignments:
                versions = refs.items()
                versions.sort()
                for version, ref in versions:
                    print >>f, name, version, ref

            print >>f
            print >>f, "aliased names:"
            assignments = self.aliased_names.items()
            assignments.sort()
            for name, aliases in assignments:
                versions = aliases.items()
                versions.sort()
                for version, alias in versions:
                    original_name, attrnames, number = alias
                    print >>f, name, version, original_name, attrnames or "{}", number is None and "{}" or number

            print >>f
            print >>f, "function parameters:"
            functions = self.function_parameters.keys()
            functions.sort()
            for function in functions:
                print >>f, function, ", ".join(self.function_parameters[function])

            print >>f
            print >>f, "function default parameters:"
            functions = self.function_defaults.keys()
            functions.sort()
            for function in functions:
                parameters = self.function_defaults[function]
                if parameters:
                    print >>f, function, ", ".join([("%s=%s" % (name, default)) for (name, default) in parameters])
                else:
                    print >>f, function, "{}"

            print >>f
            print >>f, "function locals:"
            functions = self.function_locals.keys()
            functions.sort()
            for function in functions:
                names = self.function_locals[function].items()
                if names:
                    names.sort()
                    for name, value in names:
                        print >>f, function, name, value
                else:
                    print >>f, function, "{}"

            self.to_lines(f, "scope globals:", self.scope_globals)

            print >>f
            print >>f, "function targets:"
            functions = self.function_targets.keys()
            functions.sort()
            for function in functions:
                print >>f, function, self.function_targets[function]

            print >>f
            print >>f, "function arguments:"
            functions = self.function_arguments.keys()
            functions.sort()
            for function in functions:
                print >>f, function, self.function_arguments[function]

            print >>f
            print >>f, "attribute usage:"
            units = self.attr_usage.keys()
            units.sort()
            for unit in units:
                d = self.attr_usage[unit]
                self.usage_to_cache(d, f, unit)

            print >>f
            print >>f, "attribute accesses:"
            paths = self.attr_accesses.keys()
            paths.sort()
            for path in paths:
                accesses = list(self.attr_accesses[path])
                accesses.sort()
                print >>f, path, ", ".join(accesses)

            print >>f
            print >>f, "constant accesses:"
            paths = self.const_accesses.keys()
            paths.sort()
            for path in paths:
                accesses = self.const_accesses[path].items()
                accesses.sort()
                for (original_name, attrnames), (objpath, ref, remaining_attrnames) in accesses:
                    print >>f, path, original_name, attrnames, objpath, ref, remaining_attrnames or "{}"

            print >>f
            print >>f, "attribute access usage:"
            paths = self.attr_accessors.keys()
            paths.sort()
            for path in paths:
                all_accesses = self.attr_accessors[path].items()
                all_accesses.sort()
                for (name, attrname), accesses in all_accesses:
                    for positions in accesses:
                        positions = map(str, positions)
                        print >>f, path, name, attrname or "{}", ", ".join(positions)

            print >>f
            print >>f, "attribute access modifiers:"
            paths = self.attr_access_modifiers.keys()
            paths.sort()
            for path in paths:
                all_accesses = self.attr_access_modifiers[path].items()
                all_accesses.sort()
                for (name, attrnames), modifiers in all_accesses:
                    print >>f, path, name or "{}", attrnames or "{}", encode_modifiers(modifiers)

            print >>f
            print >>f, "constant literals:"
            paths = self.constants.keys()
            paths.sort()
            for path in paths:
                constants = [(v, k) for (k, v) in self.constants[path].items()]
                constants.sort()
                for n, constant in constants:
                    print >>f, path, repr(constant)

            print >>f
            print >>f, "constant values:"
            names = self.constant_values.keys()
            names.sort()
            for name in names:
                value, value_type = self.constant_values[name]
                print >>f, name, value_type, repr(value)

        finally:
            f.close()

    def to_lines(self, f, heading, d):

        "Write lines to 'f' with the given 'heading', using 'd'."

        print >>f
        print >>f, heading
        keys = d.keys()
        keys.sort()
        for key in keys:
            attrs = list(d[key])
            if attrs:
                attrs.sort()
                print >>f, key, ", ".join(attrs)

    def usage_to_cache(self, details, f, prefix):

        "Write the given namespace usage details to the cache."

        names = list(details.keys())
        if names:
            names.sort()
            for name in names:
                if details[name]:

                    # Produce descriptions for each version of the name.

                    for version in details[name]:
                        all_usages = []
                        for usage in version:
                            all_usages.append(encode_usage(usage))

                        print >>f, "%s %s %s" % (prefix, name, "; ".join(all_usages))

# vim: tabstop=4 expandtab shiftwidth=4
