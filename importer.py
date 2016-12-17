#!/usr/bin/env python

"""
Import logic.

Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
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

from errors import ProgramError
from os.path import exists, extsep, getmtime, join
from os import listdir, makedirs, remove
from common import init_item, readfile, writefile
from modules import CachedModule
from referencing import Reference
import inspector
import sys

class Importer:

    "An import machine, searching for and loading modules."

    def __init__(self, path, cache=None, verbose=False):

        """
        Initialise the importer with the given search 'path' - a list of
        directories to search for Python modules.

        The optional 'cache' should be the name of a directory used to store
        cached module information.

        The optional 'verbose' parameter causes output concerning the activities
        of the object to be produced if set to a true value (not the default).
        """

        self.path = path
        self.cache = cache
        self.verbose = verbose

        # Module importing queue, required modules, removed modules and active
        # modules in the final program.

        self.to_import = set()
        self.required = set(["__main__"])
        self.removed = {}
        self.modules = {}

        # Module relationships and invalidated cached modules.

        self.accessing_modules = {}
        self.invalidated = set()

        # Object relationships and dependencies.

        self.depends = {}
        self.module_depends = {}

        # Basic program information.

        self.objects = {}
        self.classes = {}
        self.function_parameters = {}
        self.function_defaults = {}
        self.function_locals = {}
        self.function_targets = {}
        self.function_arguments = {}

        # Unresolved names.

        self.missing = set()

        # Derived information.

        self.subclasses = {}

        # Attributes of different object types.

        self.all_class_attrs = {}
        self.all_instance_attrs = {}
        self.all_instance_attr_constants = {}
        self.all_combined_attrs = {}
        self.all_module_attrs = {}
        self.all_shadowed_attrs = {}

        # References to external names and aliases within program units.

        self.all_name_references = {}
        self.all_initialised_names = {}
        self.all_aliased_names = {}

        # General attribute accesses.

        self.all_attr_accesses = {}
        self.all_const_accesses = {}
        self.all_attr_access_modifiers = {}

        # Constant literals and values.

        self.all_constants = {}
        self.all_constant_values = {}

        self.make_cache()

    def make_cache(self):
        if self.cache and not exists(self.cache):
            makedirs(self.cache)

    def check_cache(self, details):

        """
        Check whether the cache applies for the given 'details', invalidating it
        if it does not.
        """

        recorded_details = self.get_cache_details()

        if recorded_details != details:
            self.remove_cache()

        writefile(self.get_cache_details_filename(), details)

    def get_cache_details_filename(self):

        "Return the filename for the cache details."

        return join(self.cache, "$details")

    def get_cache_details(self):

        "Return details of the cache."

        details_filename = self.get_cache_details_filename()

        if not exists(details_filename):
            return None
        else:
            return readfile(details_filename)

    def remove_cache(self):

        "Remove the contents of the cache."

        for filename in listdir(self.cache):
            remove(join(self.cache, filename))

    def to_cache(self):

        "Write modules to the cache."

        if self.cache:
            for module_name, module in self.modules.items():
                module.to_cache(join(self.cache, module_name))

    # Object retrieval and storage.

    def get_object(self, name):

        """
        Return a reference for the given 'name' or None if no such object
        exists.
        """

        return self.objects.get(name)

    def set_object(self, name, value=None):

        "Set the object with the given 'name' and the given 'value'."

        if isinstance(value, Reference):
            ref = value.alias(name)
        else:
            ref = Reference(value, name)

        self.objects[name] = ref

    # Identification of both stored object names and name references.

    def identify(self, name):

        "Identify 'name' using stored object and external name records."

        return self.objects.get(name) or self.all_name_references.get(name)

    # Indirect object retrieval.

    def get_attributes(self, ref, attrname):

        """
        Return attributes provided by 'ref' for 'attrname'. Class attributes
        may be provided by instances.
        """

        kind = ref.get_kind()
        if kind == "<class>":
            ref = self.get_class_attribute(ref.get_origin(), attrname)
            return ref and set([ref]) or set()
        elif kind == "<instance>":
            return self.get_combined_attributes(ref.get_origin(), attrname)
        elif kind == "<module>":
            ref = self.get_module_attribute(ref.get_origin(), attrname)
            return ref and set([ref]) or set()
        else:
            return set()

    def get_class_attribute(self, object_type, attrname):

        "Return from 'object_type' the details of class attribute 'attrname'."

        attrs = self.all_class_attrs.get(object_type)
        attr = attrs and attrs.get(attrname)
        return attr and self.get_object(attr)

    def get_instance_attributes(self, object_type, attrname):

        """
        Return from 'object_type' the details of instance attribute 'attrname'.
        """

        consts = self.all_instance_attr_constants.get(object_type)
        attrs = set()
        for attr in self.all_instance_attrs[object_type].get(attrname, []):
            attrs.add(consts and consts.get(attrname) or Reference("<var>", attr))
        return attrs

    def get_combined_attributes(self, object_type, attrname):

        """
        Return from 'object_type' the details of class or instance attribute
        'attrname'.
        """

        ref = self.get_class_attribute(object_type, attrname)
        refs = ref and set([ref]) or set()
        refs.update(self.get_instance_attributes(object_type, attrname))
        return refs

    def get_module_attribute(self, object_type, attrname):

        "Return from 'object_type' the details of module attribute 'attrname'."

        if attrname in self.all_module_attrs[object_type]:
            return self.get_object("%s.%s" % (object_type, attrname))
        else:
            return None

    # Convenience methods for deducing which kind of object provided an
    # attribute.

    def get_attribute_provider(self, ref, attrname):

        """
        Return the kind of provider of the attribute accessed via 'ref' using
        'attrname'.
        """

        kind = ref.get_kind()

        if kind in ["<class>", "<module>"]:
            return kind
        else:
            return self.get_instance_attribute_provider(ref.get_origin(), attrname)

    def get_instance_attribute_provider(self, object_type, attrname):

        """
        Return the kind of provider of the attribute accessed via an instance of
        'object_type' using 'attrname'.
        """

        if self.get_class_attribute(object_type, attrname):
            return "<class>"
        else:
            return "<instance>"

    # Module management.

    def queue_module(self, name, accessor, required=False):

        """
        Queue the module with the given 'name' for import from the given
        'accessor' module. If 'required' is true (it is false by default), the
        module will be required in the final program.
        """

        if not self.modules.has_key(name):
            self.to_import.add(name)

        if required:
            self.required.add(name)

        init_item(self.accessing_modules, name, set)
        self.accessing_modules[name].add(accessor.name)

    def get_modules(self):

        "Return all modules known to the importer."

        return self.modules.values()

    def get_module(self, name):

        "Return the module with the given 'name'."

        if not self.modules.has_key(name):
            return None

        return self.modules[name]

    # Program operations.

    def initialise(self, filename, reset=False):

        """
        Initialise a program whose main module is 'filename', resetting the
        cache if 'reset' is true. Return the main module.
        """

        if reset:
            self.remove_cache()
        self.check_cache(filename)

        # Load the program itself.

        m = self.load_from_file(filename)

        # Load any queued modules.

        while self.to_import:
            for name in list(self.to_import): # avoid mutation issue
                self.load(name)

        # Resolve dependencies between modules.

        self.resolve()

        # Record the type of all classes.

        self.type_ref = self.get_object("__builtins__.type")

        # Resolve dependencies within the program.

        for module in self.modules.values():
            module.complete()

        # Remove unneeded modules.

        all_modules = self.modules.items()

        for name, module in all_modules:
            if name not in self.required:
                module.unpropagate()
                del self.modules[name]
                self.removed[name] = module

        # Collect redundant objects.

        for module in self.removed.values():
            module.collect()

        # Assert module objects where aliases have been removed.

        for name in self.required:
            if not self.objects.has_key(name):
                self.objects[name] = Reference("<module>", name)

        return m

    def finalise(self):

        """
        Finalise the inspected program, returning whether the program could be
        finalised.
        """

        self.finalise_classes()
        self.add_init_dependencies()
        self.to_cache()

        if self.missing:
            return False

        self.set_class_types()
        self.define_instantiators()
        self.collect_constants()

        return True

    # Supporting operations.

    def resolve(self):

        "Resolve dependencies between modules."

        self.waiting = {}

        for module in self.modules.values():

            # Resolve all deferred references in each module.

            original_deferred = []

            for ref in module.deferred:

                # Retain original references for caching.

                original_deferred.append(ref.copy())

                # Update references throughout the program.

                found = self.find_dependency(ref)
                if not found:
                    self.missing.add((module.name, ref.get_origin()))

                # Record the resolved names and identify required modules.

                else:
                    # Find the providing module of this reference.
                    # Where definitive details of the origin cannot be found,
                    # identify the provider using the deferred reference.
                    # NOTE: This may need to test for static origins.

                    provider = self.get_module_provider(found.unresolved() and ref or found)
                    ref.mutate(found)

                    # Record any external dependency.

                    if provider and provider != module.name:

                        # Record the provider dependency.

                        module.required.add(provider)
                        self.accessing_modules[provider].add(module.name)

                        # Postpone any inclusion of the provider until this
                        # module becomes required.

                        if module.name not in self.required:
                            init_item(self.waiting, module.name, set)
                            self.waiting[module.name].add(provider)
                            if self.verbose:
                                print >>sys.stderr, "Noting", provider, "for", ref, "from", module.name

                        # Make this module required in the accessing module.

                        elif provider not in self.required:
                            self.required.add(provider)
                            if self.verbose:
                                print >>sys.stderr, "Requiring", provider, "for", ref, "from", module.name

                        # Record a module ordering dependency.

                        if not found.static():
                            self.add_module_dependency(module.name, provider)

            # Restore the original references so that they may be read back in
            # and produce the same results.

            module.deferred = original_deferred

        # Check modules again to see if they are now required and should now
        # cause the inclusion of other modules providing objects to the program.

        for module_name in self.waiting.keys():
            self.require_providers(module_name)

        self.add_special_dependencies()
        self.add_module_dependencies()

    def require_providers(self, module_name):

        """
        Test if 'module_name' is itself required and, if so, require modules
        containing objects provided to the module.
        """

        if module_name in self.required and self.waiting.has_key(module_name):
            for provider in self.waiting[module_name]:
                if provider not in self.required:
                    self.required.add(provider)
                    if self.verbose:
                        print >>sys.stderr, "Requiring", provider
                    self.require_providers(provider)

    def add_special_dependencies(self):

        "Add dependencies due to the use of special names in namespaces."

        for module in self.modules.values():
            for ref, paths in module.special.values():
                for path in paths:
                    self.add_dependency(path, ref.get_origin())

    def add_init_dependencies(self):

        "Add dependencies related to object initialisation."

        for name in self.classes.keys():
            if self.is_dynamic_class(name):

                # Make subclasses depend on any class with non-static
                # attributes, plus its module for the initialisation.

                for subclass in self.subclasses[name]:
                    ref = Reference("<class>", subclass)
                    self.add_dependency(subclass, name)
                    self.add_dependency(subclass, self.get_module_provider(ref))

                # Also make the class dependent on its module for
                # initialisation.

                ref = Reference("<class>", name)
                self.add_dependency(name, self.get_module_provider(ref))

        for name in self.function_defaults.keys():
            if self.is_dynamic_callable(name):

                # Make functions with defaults requiring initialisation depend
                # on the parent scope.

                ref = Reference("<function>", name)
                self.add_dependency(name, ref.parent())

    def add_module_dependencies(self):

        "Record module-based dependencies."

        for module_name, providers in self.module_depends.items():
            if self.modules.has_key(module_name):
                for provider in providers:
                    if self.modules.has_key(provider):
                        self.add_dependency(module_name, provider)

    def add_dependency(self, path, origin):

        "Add dependency details for 'path' involving 'origin'."

        if origin and not origin.startswith("%s." % path):
            init_item(self.depends, path, set)
            self.depends[path].add(origin)

    def add_module_dependency(self, module_name, provider):

        "Add dependency details for 'module_name' involving 'provider'."

        if provider:
            init_item(self.module_depends, module_name, set)
            self.module_depends[module_name].add(provider)

    def condense_dependencies(self):

        """
        Condense the dependencies by removing all functions that do not need
        initialisation.
        """

        d = {}
        for path, depends in self.depends.items():
            d[path] = {}
            d[path] = self.condense_dependency_entry(depends, d)

        self.depends = {}

        for path, depends in d.items():
            if depends:
                self.depends[path] = depends

    def condense_dependency_entry(self, depends, d):
        l = set()
        for depend in depends:
            if self.modules.has_key(depend) or self.classes.has_key(depend) or \
               self.is_dynamic_callable(depend):

                l.add(depend)
            else:
                deps = d.get(depend)
                if deps:
                    l.update(self.condense_dependency_entry(deps, d))
        return l

    # NOTE: Consolidate this information in a common location.

    special_attributes = ("__args__", "__file__", "__fn__", "__fname__", "__mname__", "__name__")

    def is_dynamic_class(self, name):

        """
        Return whether 'name' refers to a class with members that must be
        initialised dynamically.
        """

        attrs = self.all_class_attrs.get(name)

        if not attrs:
            return False

        for attrname, attr in attrs.items():
            if attrname in self.special_attributes:
                continue
            if not attr or not self.get_object(attr).static():
                return True

        return False

    def is_dynamic_callable(self, name):

        """
        Return whether 'name' refers to a callable employing defaults that may
        need initialising before the callable can be used.
        """

        # Find any defaults for the function or method.

        defaults = self.function_defaults.get(name)
        if not defaults:
            return False

        # Identify non-constant defaults.

        for name, ref in defaults:
            if not ref.static() and not ref.is_constant_alias():
                return True

        return False

    def order_objects(self):

        "Produce an object initialisation ordering."

        self.condense_dependencies()

        # Record the number of modules using or depending on each module.

        usage = {}

        # Record path-based dependencies.

        for path in self.depends.keys():
            usage[path] = set()

        for path, depends in self.depends.items():
            for origin in depends:
                init_item(usage, origin, set)
                usage[origin].add(path)

        # Produce an ordering by obtaining exposed modules (required by modules
        # already processed) and putting them at the start of the list.

        ordered = []

        while usage:
            have_next = False

            for path, n in usage.items():
                if not n:
                    ordered.insert(0, path)
                    depends = self.depends.get(path)

                    # Reduce usage of the referenced objects.

                    if depends:
                        for origin in depends:
                            usage[origin].remove(path)

                    del usage[path]
                    have_next = True

            if not have_next:
                raise ProgramError("Modules with unresolvable dependencies exist: %s" % ", ".join(usage.keys()))

        ordered.remove("__main__")
        ordered.append("__main__")
        return ordered

    def order_modules(self):

        "Produce a module initialisation ordering."

        ordered = self.order_objects()
        filtered = []

        for module_name in self.modules.keys():
            if module_name not in ordered:
                filtered.append(module_name)

        for path in ordered:
            if self.modules.has_key(path):
                filtered.append(path)

        return filtered

    def find_dependency(self, ref):

        "Find the ultimate dependency for 'ref'."

        found = set()
        while ref and ref.has_kind("<depends>") and not ref in found:
            found.add(ref)
            ref = self.identify(ref.get_origin())
        return ref

    def get_module_provider(self, ref):

        "Identify the provider of the given 'ref'."

        for ancestor in ref.ancestors():
            if self.modules.has_key(ancestor):
                return ancestor
        return None

    def finalise_classes(self):

        "Finalise the class relationships and attributes."

        self.derive_inherited_attrs()
        self.derive_subclasses()
        self.derive_shadowed_attrs()

    def derive_inherited_attrs(self):

        "Derive inherited attributes for classes throughout the program."

        for name in self.classes.keys():
            self.propagate_attrs_for_class(name)

    def propagate_attrs_for_class(self, name, visited=None):

        "Propagate inherited attributes for class 'name'."

        # Visit classes only once.

        if self.all_combined_attrs.has_key(name):
            return

        visited = visited or []

        if name in visited:
            raise ProgramError, "Class %s may not inherit from itself: %s -> %s." % (name, " -> ".join(visited), name)

        visited.append(name)

        class_attrs = {}
        instance_attrs = {}

        # Aggregate the attributes from base classes, recording the origins of
        # applicable attributes.

        for base in self.classes[name][::-1]:

            # Get the identity of the class from the reference.

            base = base.get_origin()

            # Define the base class completely before continuing with this
            # class.

            self.propagate_attrs_for_class(base, visited)
            class_attrs.update(self.all_class_attrs[base])

            # Instance attribute origins are combined if different.

            for key, values in self.all_instance_attrs[base].items():
                init_item(instance_attrs, key, set)
                instance_attrs[key].update(values)

        # Class attributes override those defined earlier in the hierarchy.

        class_attrs.update(self.all_class_attrs.get(name, {}))

        # Instance attributes are merely added if not already defined.

        for key in self.all_instance_attrs.get(name, []):
            if not instance_attrs.has_key(key):
                instance_attrs[key] = set(["%s.%s" % (name, key)])

        self.all_class_attrs[name] = class_attrs
        self.all_instance_attrs[name] = instance_attrs
        self.all_combined_attrs[name] = set(class_attrs.keys()).union(instance_attrs.keys())

    def derive_subclasses(self):

        "Derive subclass details for classes."

        for name, bases in self.classes.items():
            for base in bases:

                # Get the identity of the class from the reference.

                base = base.get_origin()
                self.subclasses[base].add(name)

    def derive_shadowed_attrs(self):

        "Derive shadowed attributes for classes."

        for name, attrs in self.all_instance_attrs.items():
            attrs = set(attrs.keys()).intersection(self.all_class_attrs[name].keys())
            if attrs:
                self.all_shadowed_attrs[name] = attrs

    def set_class_types(self):

        "Set the type of each class."

        for attrs in self.all_class_attrs.values():
            attrs["__class__"] = self.type_ref.get_origin()

    def define_instantiators(self):

        """
        Consolidate parameter and default details, incorporating initialiser
        details to define instantiator signatures.
        """

        for cls, attrs in self.all_class_attrs.items():
            initialiser = attrs["__init__"]
            self.function_parameters[cls] = self.function_parameters[initialiser]
            self.function_defaults[cls] = self.function_defaults[initialiser]

    def collect_constants(self):

        "Get constants from all active modules."

        for module in self.modules.values():
            self.all_constants.update(module.constants)

    # Import methods.

    def find_in_path(self, name):

        """
        Find the given module 'name' in the search path, returning None where no
        such module could be found, or a 2-tuple from the 'find' method
        otherwise.
        """

        for d in self.path:
            m = self.find(d, name)
            if m: return m
        return None

    def find(self, d, name):

        """
        In the directory 'd', find the given module 'name', where 'name' can
        either refer to a single file module or to a package. Return None if the
        'name' cannot be associated with either a file or a package directory,
        or a 2-tuple from '_find_package' or '_find_module' otherwise.
        """

        m = self._find_package(d, name)
        if m: return m
        m = self._find_module(d, name)
        if m: return m
        return None

    def _find_module(self, d, name):

        """
        In the directory 'd', find the given module 'name', returning None where
        no suitable file exists in the directory, or a 2-tuple consisting of
        None (indicating that no package directory is involved) and a filename
        indicating the location of the module.
        """

        name_py = name + extsep + "py"
        filename = self._find_file(d, name_py)
        if filename:
            return None, filename
        return None

    def _find_package(self, d, name):

        """
        In the directory 'd', find the given package 'name', returning None
        where no suitable package directory exists, or a 2-tuple consisting of
        a directory (indicating the location of the package directory itself)
        and a filename indicating the location of the __init__.py module which
        declares the package's top-level contents.
        """

        filename = self._find_file(d, name)
        if filename:
            init_py = "__init__" + extsep + "py"
            init_py_filename = self._find_file(filename, init_py)
            if init_py_filename:
                return filename, init_py_filename
        return None

    def _find_file(self, d, filename):

        """
        Return the filename obtained when searching the directory 'd' for the
        given 'filename', or None if no actual file exists for the filename.
        """

        filename = join(d, filename)
        if exists(filename):
            return filename
        else:
            return None

    def load(self, name):

        """
        Load the module or package with the given 'name'. Return an object
        referencing the loaded module or package, or None if no such module or
        package exists.
        """

        # Loaded modules are returned immediately.
        # Modules may be known but not yet loading (having been registered as
        # submodules), loading, loaded, or completely unknown.

        module = self.get_module(name)

        if module:
            return self.modules[name]

        # Otherwise, modules are loaded.

        # Split the name into path components, and try to find the uppermost in
        # the search path.

        path = name.split(".")
        path_so_far = []
        module = None

        for p in path:

            # Get the module's filesystem details.

            if not path_so_far:
                m = self.find_in_path(p)
            elif d:
                m = self.find(d, p)
            else:
                m = None

            path_so_far.append(p)
            module_name = ".".join(path_so_far)

            # Return None if the module could not be located.

            if not m:
                if self.verbose:
                    print >>sys.stderr, "Not found (%s)" % name
                return None

            # Get the directory and module filename.

            d, filename = m

        # Get the module itself.

        return self.load_from_file(filename, module_name)

    def load_from_file(self, filename, module_name=None):

        "Load the module from the given 'filename'."

        if module_name is None:
            module_name = "__main__"

        module = self.modules.get(module_name)

        if not module:

            # Try to load from cache.

            module = self.load_from_cache(filename, module_name)
            if module:
                return module

            # If no cache entry exists, load from file.

            module = inspector.InspectedModule(module_name, self)
            self.add_module(module_name, module)
            self.update_cache_validity(module)

            self._load(module, module_name, lambda m: m.parse, filename)

        return module

    def update_cache_validity(self, module):

        "Make 'module' valid in the cache, but invalidate accessing modules."

        accessing = self.accessing_modules.get(module.name)
        if accessing:
            self.invalidated.update(accessing)
        if module.name in self.invalidated:
            self.invalidated.remove(module.name)

    def source_is_new(self, filename, module_name):

        "Return whether 'filename' is newer than the cached 'module_name'."

        if self.cache:
            cache_filename = join(self.cache, module_name)
            return not exists(cache_filename) or \
                getmtime(filename) > getmtime(cache_filename) or \
                module_name in self.invalidated
        else:
            return True

    def load_from_cache(self, filename, module_name):

        "Return a module residing in the cache."

        module = self.modules.get(module_name)

        if not module and not self.source_is_new(filename, module_name):
            module = CachedModule(module_name, self)
            self.add_module(module_name, module)

            filename = join(self.cache, module_name)
            self._load(module, module_name, lambda m: m.from_cache, filename)

        return module

    def _load(self, module, module_name, fn, filename):

        """
        Load 'module' for the given 'module_name', and with 'fn' performing an
        invocation on the module with the given 'filename'.
        """

        # Load the module.

        if self.verbose:
            print >>sys.stderr, module_name in self.required and "Required" or "Loading", module_name, "from", filename
        fn(module)(filename)

        # Add the module object if not already defined.

        if not self.objects.has_key(module_name):
            self.objects[module_name] = Reference("<module>", module_name)

    def add_module(self, module_name, module):

        """
        Return the module with the given 'module_name', adding a new module
        object if one does not already exist.
        """

        self.modules[module_name] = module
        if module_name in self.to_import:
            self.to_import.remove(module_name)

# vim: tabstop=4 expandtab shiftwidth=4
