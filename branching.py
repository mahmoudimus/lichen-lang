#!/usr/bin/env python

"""
Track attribute usage for names.

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

from common import dict_for_keys, init_item

class Branch:

    """
    A control-flow branch capturing local attribute usage for names.
    Branches typically begin with assignments or function parameters and are
    connected to others introduced by conditional and loop nodes.

    Branches hosting accesses, and thus providing usage information, are
    contributors to preceding branches.

    Branches also provide a route from accesses back to assignments which are
    the ultimate suppliers of the names involved.
    """

    def __init__(self, names, assigning=False, values=None):

        """
        Capture attribute usage for the given 'names', with the accompanying
        'values' indicating assigned values for each name, if indicated.
        """

        self.contributors = set()
        self.suppliers = {}
        self.assignments = set(assigning and names or [])
        self.usage = {}
        self.values = {}

        # Initialise usage for each name.

        for name in names:
            self.usage[name] = set()

        # Initialise assigned values if any were provided.

        if values:
            for name, value in zip(names, values):
                if value:
                    self.values[name] = value

        # Computed results.

        self.combined_usage = None

    def get_assignment_sources(self, name):

        """
        Return the sources of 'name' from this branch's assignment information,
        returning a list containing only this branch itself if it is the source.
        """

        if name in self.assignments:
            return [self]
        else:
            return [b for b in self.get_all_suppliers(name) if name in b.assignments]

    def set_usage(self, name, attrname, invocation=False):

        """
        Record usage on the given 'name' of the attribute 'attrname', noting the
        invocation of the attribute if 'invocation' is set to a true value.
        """

        if self.usage.has_key(name):
            self.usage[name].add((attrname, invocation))

    def get_usage(self):

        """
        Obtain usage from this node, combined with usage observed by its
        contributors. Unlike the local usage which involves only a single set of
        attribute names for a given variable name, the returned usage is a set
        of attribute name combinations for a given variable name. For example:

        {'a': set([('p', 'q', 'r'), ('p', 'r')])}
        """

        if self.combined_usage is None:

            # Accumulate usage observations from contributors.

            all_usage = []

            for contributor in self.contributors:

                # Record any usage that can be returned.

                all_usage.append(contributor.get_usage())

            # Merge usage from the contributors.

            merged_usage = merge_dicts(all_usage)

            # Make the local usage compatible with the combined usage.

            usage = deepen_dict(self.usage)

            self.combined_usage = combine_dicts(usage, merged_usage, combine_sets)

        return self.combined_usage

    def get_all_suppliers(self, name, all_suppliers=None):

        "Return all branches supplying this branch with definitions of 'name'."

        all_suppliers = all_suppliers or set()
        all_suppliers.add(self)

        if self.suppliers.has_key(name):
            for supplier in self.suppliers[name]:
                if supplier not in all_suppliers:
                    supplier.get_all_suppliers(name, all_suppliers)

        return all_suppliers

    def __repr__(self):
        return "Branch(%r, %r)" % (self.usage.keys(),
            self.assignments and True or False)

class BranchTracker:

    """
    A tracker of attribute usage for names in a namespace. This tracker directs
    usage observations to branches which are the ultimate repositories of
    attribute usage information.

    As a program unit is inspected, the branches associated with names may
    change. Assignments reset the branches; control-flow operations cause
    branches to be accumulated from different code paths.
    """

    def __init__(self):

        # Track assignments.

        self.assignments = {}

        # Details of attributes at each active branch level.

        self.attribute_branches = [{}]          # stack of branches for names
        self.attribute_branch_shelves = []      # stack of shelved branches

        # Suspended branch details plus loop details.

        self.suspended_broken_branches = []     # stack of lists of dicts
        self.suspended_continuing_branches = [] # stack of lists of dicts

        # Abandoned usage, useful for reviving usage for exception handlers.

        self.abandoned_branches = [[]]          # stack of lists of branches

        # Returning branches are like abandoned branches but are only revived in
        # finally clauses.

        self.returning_branches = [[]]

        # Branches active when starting loops.

        self.loop_branches = []

    # Structure assembly methods.

    def new_branchpoint(self, loop_node=False):

        """
        Indicate that branches diverge, initialising resources dependent on
        any given 'loop_node'.
        """

        self.attribute_branch_shelves.append([])

        if loop_node:
            self.suspended_broken_branches.append([])
            self.suspended_continuing_branches.append([])

        # Retain a record of abandoned branches.

        self.abandoned_branches.append([])
        self.returning_branches.append([])

    def new_branch(self, loop_node=False):

        "Create a new branch."

        attribute_branches = self.attribute_branches[-1]

        branch, new_branches = self._new_branch(attribute_branches)

        if branch and loop_node:
            self.loop_branches.append(branch)

        # Start using the branch for known names.

        self.attribute_branches.append(new_branches)

    def _new_branch(self, attribute_branches):

        """
        Define a new branch that will record attribute usage on known names from
        'attribute_branches'.
        """

        # Detect abandoned branches.

        if isinstance(attribute_branches, AbandonedDict):
            return None, AbandonedDict()

        # Otherwise, define a new branch.

        names = attribute_branches.keys()

        new_branches = {}
        branch = Branch(names)

        for name in names:
            new_branches[name] = [branch]

        # Add this new branch as a contributor to the previously active
        # branches.

        self._connect_branches(attribute_branches, branch)

        return branch, new_branches

    def shelve_branch(self, loop_node=False):

        "Retain the current branch for later merging."

        branches = self.attribute_branches.pop()
        self.attribute_branch_shelves[-1].append(branches)

        # Connect any loop branch to the active branches as contributors.

        if loop_node:
            branch = self.loop_branches.pop()
            self._connect_branches(branches, branch, loop_node)

    def abandon_branch(self):

        "Abandon the current branch, retaining it for later."

        attribute_branches = self.attribute_branches[-1]
        self._abandon_branch()
        self.abandoned_branches[-1].append(attribute_branches)

    def abandon_returning_branch(self):

        "Abandon the current branch, retaining it for later."

        attribute_branches = self.attribute_branches[-1]
        self._abandon_branch()
        self.returning_branches[-1].append(attribute_branches)

    def suspend_broken_branch(self):

        "Suspend a branch for breaking out of a loop."

        attribute_branches = self.attribute_branches[-1]

        branches = self.suspended_broken_branches[-1]
        branches.append(attribute_branches)
        self._abandon_branch()

    def suspend_continuing_branch(self):

        "Suspend a branch for loop continuation."

        attribute_branches = self.attribute_branches[-1]

        branches = self.suspended_continuing_branches[-1]
        branches.append(attribute_branches)
        self._abandon_branch()

    def _abandon_branch(self):

        "Abandon the current branch."

        self.attribute_branches[-1] = AbandonedDict()

    def resume_abandoned_branches(self):

        """
        Resume branches previously abandoned.

        Abandoned branches are not reset because they may not be handled by
        exception handlers after all.
        """

        current_branches = self.attribute_branches[-1]
        abandoned_branches = self.abandoned_branches[-1]
        merged_branches = merge_dicts(abandoned_branches + [current_branches])

        # Replace the combined branches with a new branch applying to all active
        # names, connected to the supplying branches.

        branch, new_branches = self._new_branch(merged_branches)
        self.attribute_branches.append(new_branches)

        # Although returning branches should not be considered as accumulating
        # usage, they do provide sources of assignments.

        if branch:
            for returning_branches in self.returning_branches[-1]:
                self._connect_suppliers(returning_branches, branch)

    def resume_all_abandoned_branches(self):

        """
        Resume branches previously abandoned including returning branches.

        Abandoned branches are not reset because they may not be handled by
        exception handlers after all.
        """

        current_branches = self.attribute_branches[-1]
        abandoned_branches = self.abandoned_branches[-1]
        returning_branches = self.returning_branches[-1]
        merged_branches = merge_dicts(abandoned_branches + returning_branches + [current_branches])
        self.replace_branches(merged_branches)

        # Return the previously-active branches for later restoration.

        return current_branches

    def resume_broken_branches(self):

        "Resume branches previously suspended for breaking out of a loop."

        suspended_branches = self.suspended_broken_branches.pop()
        current_branches = self.attribute_branches[-1]

        # Merge suspended branches with the current branch.

        merged_branches = merge_dicts(suspended_branches + [current_branches])
        self.replace_branches(merged_branches)

    def resume_continuing_branches(self):

        "Resume branches previously suspended for loop continuation."

        suspended_branches = self.suspended_continuing_branches.pop()
        current_branches = self.attribute_branches[-1]

        # Merge suspended branches with the current branch.

        merged_branches = merge_dicts(suspended_branches + [current_branches])
        self.replace_branches(merged_branches)

    def replace_branches(self, merged_branches):

        """
        Replace the 'merged_branches' with a new branch applying to all active
        names, connected to the supplying branches.
        """

        branch, new_branches = self._new_branch(merged_branches)
        self.attribute_branches[-1] = new_branches

    def restore_active_branches(self, branches):

        "Restore the active 'branches'."

        self.attribute_branches[-1] = branches

    def merge_branches(self):

        "Merge branches."

        # Combine the attribute branches. This ensures that a list of branches
        # affected by attribute usage is maintained for the current branch.

        all_shelved_branches = self.attribute_branch_shelves.pop()
        merged_branches = merge_dicts(all_shelved_branches, missing=make_missing)
        self.replace_branches(merged_branches)

        # Abandoned branches are retained for exception handling purposes.

        all_abandoned_branches = self.abandoned_branches.pop()
        new_abandoned_branches = merge_dicts(all_abandoned_branches)
        self.abandoned_branches[-1].append(new_abandoned_branches)

        # Returning branches are retained for finally clauses.

        all_returning_branches = self.returning_branches.pop()
        new_returning_branches = merge_dicts(all_returning_branches)
        self.returning_branches[-1].append(new_returning_branches)

    # Internal structure assembly methods.

    def _connect_branches(self, attribute_branches, contributor, loop_node=False):

        """
        Given the 'attribute_branches' mapping, connect the branches referenced
        in the mapping to the given 'contributor' branch. If 'loop_node' is
        set to a true value, connect only the branches so that the 'contributor'
        references the nodes supplying it with name information.
        """

        all_branches = self._connect_suppliers(attribute_branches, contributor)
        if not loop_node:
            self._connect_contributor(contributor, all_branches)

    def _connect_suppliers(self, attribute_branches, contributor):

        "Connect the 'attribute_branches' to the given 'contributor'."

        # Gather branches involved with all known names into a single set.

        all_branches = set()

        for name, branches in attribute_branches.items():
            all_branches.update(branches)

            # Also note receiving branches on the contributor.

            for branch in branches:
                init_item(contributor.suppliers, name, set)
                contributor.suppliers[name].add(branch)

        return all_branches

    def _connect_contributor(self, contributor, branches):

        "Connect the given 'contributor' branch to the given 'branches'."

        for branch in branches:
            branch.contributors.add(contributor)

    # Attribute usage methods.

    def tracking_name(self, name):

        """
        Return whether 'name' is being tracked, returning all branches doing so
        if it is.
        """

        return self.assignments.has_key(name) and self.have_name(name)

    def have_name(self, name):

        "Return whether 'name' is known."

        return self.attribute_branches[-1].get(name)

    def assign_names(self, names, values=None):

        """
        Define the start of usage tracking for the given 'names', each being
        assigned with the corresponding 'values' if indicated.
        """

        branches = self.attribute_branches[-1]
        branch = Branch(names, True, values)

        for name in names:
            branches[name] = [branch]
            init_item(self.assignments, name, list)
            self.assignments[name].append(branch)

        return branch

    def use_attribute(self, name, attrname, invocation=False):

        """
        Indicate the use on the given 'name' of an attribute with the given
        'attrname', optionally involving an invocation of the attribute if
        'invocation' is set to a true value.

        Return all branches that support 'name'.
        """

        branches = self.attribute_branches[-1]

        # Add the usage to all current branches.

        if branches.has_key(name):
            for branch in branches[name]:
                branch.set_usage(name, attrname, invocation)
            return branches[name]
        else:
            return None

    # Query methods.

    def get_assignment_positions_for_branches(self, name, branches, missing=True):

        """
        Return the positions of assignments involving the given 'name' affected
        by the given 'branches'. If 'missing' is set to a false value, branches
        with missing name details will be excluded instead of contributing the
        value None to the list of positions.
        """

        if not branches:
            return [None]

        positions = set()
        assignments = self.assignments[name]

        for assignment in self.get_assignments_for_branches(name, branches):

            # Use None to indicate a branch without assignment information.

            if missing and isinstance(assignment, MissingBranch):
                positions.add(None)
            else:
                pos = assignments.index(assignment)
                positions.add(pos)

        positions = list(positions)
        positions.sort()
        return positions

    def get_assignments_for_branches(self, name, branches, missing=True):

        """
        Return the origins of assignments involving the given 'name' affected
        by the given 'branches'. The origins are a list of branches where names
        are defined using assignments. If 'missing' is set to a false value,
        branches with missing name details are excluded.
        """

        all_branches = []
        assignments = self.assignments[name]

        # Obtain the assignments recorded for each branch.

        for branch in branches:

            # Find the branch representing the definition of some names in the
            # scope's assignments, making sure that the given name is involved.

            for assignment in branch.get_assignment_sources(name):

                # Capture branches without assignment information as well as
                # genuine assignment branches.

                if assignment in assignments or missing and isinstance(assignment, MissingBranch):
                    all_branches.append(assignment)

        return all_branches

    def get_all_usage(self):

        """
        Convert usage observations from the tracker to a simple mapping of
        names to sets of attribute names.
        """

        d = {}
        for name, branches in self.assignments.items():
            d[name] = self.get_usage_from_branches_for_name(branches, name)
        return d

    def get_usage_from_branches_for_name(self, branches, name):

        """
        Convert usage observations from the 'branches' to a simple list of
        usage sets for the given 'name'.
        """

        l = []
        for branch in branches:
            l.append(branch.get_usage()[name])
        return l

    def get_all_values(self):

        "Return a mapping from names to lists of assigned values."

        d = {}
        for name, branches in self.assignments.items():
            d[name] = [branch.values.get(name) for branch in branches]
        return d

# Special objects.

class AbandonedDict(dict):

    "A dictionary representing mappings in an abandoned branch."

    def __repr__(self):
        return "AbandonedDict()"

class MissingBranch(Branch):

    "A branch introduced during dictionary merging."

    def __repr__(self):
        return "MissingBranch(%r, %r)" % (self.usage.keys(),
            self.assignments and True or False)

def make_missing(name):

    "Make a special branch indicating missing name information."

    return set([MissingBranch([name], True)])

# Dictionary utilities.

def merge_dicts(dicts, ignored=AbandonedDict, missing=None):

    """
    Merge the given 'dicts' mapping keys to sets of values.

    Where 'ignored' is specified, any dictionary of the given type is ignored.
    Where all dictionaries to be merged are of the given type, an instance of
    the type is returned as the merged dictionary.

    Where 'missing' is specified, it provides a callable that produces a set of
    suitable values for a given name.
    """

    new_dict = {}
    all_names = set()

    # Determine all known names.

    for old_dict in dicts:
        all_names.update(old_dict.keys())

    # Merge the dictionaries, looking for all known names in each one.

    have_dicts = False

    for old_dict in dicts:

        # Abandoned dictionaries should not contribute information.

        if isinstance(old_dict, ignored):
            continue
        else:
            have_dicts = True

        for name in all_names:

            # Find branches providing each name.

            if old_dict.has_key(name):
                values = old_dict[name]

            # Branches not providing names may indicate usage before assignment.

            elif missing:
                values = missing(name)
            else:
                continue

            # Initialise mappings in the resulting dictionary.

            if not new_dict.has_key(name):
                new_dict[name] = set(values)
            else:
                new_dict[name].update(values)

    # Where no dictionaries contributed, all branches were abandoned.

    if have_dicts:
        return new_dict
    else:
        return ignored()

def deepen_dict(d):

    """
    Return a version of dictionary 'd' with its values converted to sets
    containing each original value as a single element in each new value.
    Original values are assumed to be sequences. Thus...

    {"self" : ("x", "y")}

    ...would become...

    {"self" : set([("x", "y")])}

    ...allowing other such values to be added to the set alongside the original
    value.
    """

    l = []

    for key, value in d.items():

        # Sort the attribute name details for stable comparisons.

        value = list(value)
        value.sort()
        l.append((key, set([tuple(value)])))

    return dict(l)

def combine_sets(s1, s2):

    "Combine elements from sets 's1' and 's2'."

    if not s1:
        return s2
    elif not s2:
        return s1

    s = set()

    for i1 in s1:
        for i2 in s2:

            # Sort the attribute name details for stable comparisons.

            l = list(set(i1 + i2))
            l.sort()
            s.add(tuple(l))

    return s

def combine_dicts(d1, d2, combine=combine_sets):

    """
    Combine dictionaries 'd1' and 'd2' such that the values for common keys
    are themselves combined in the result.
    """

    d = {}

    for key in d1.keys():
        if d2.has_key(key):
            d[key] = combine(d1[key], d2[key])
        else:
            d[key] = d1[key]

    return d

# vim: tabstop=4 expandtab shiftwidth=4
