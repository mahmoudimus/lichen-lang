#!/usr/bin/env python

import branching

names = []

# Equivalent to...
#
# a = ...
# a.p
# if ...:
#   a = ...
#   a.x
# else:
#   ...
# a.q

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.use_attribute("a", "p")
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
a2 = bt.assign_names(["a"])         # a = ...
ax = bt.use_attribute("a", "x")
bt.shelve_branch()
bt.new_branch()                     # else
bt.shelve_branch()
bt.merge_branches()                 # end
aq = bt.use_attribute("a", "q")

print a1.get_usage() == \
    {'a' : set([('p',), ('p', 'q')])}, \
    a1.get_usage()
print a2.get_usage() == \
    {'a' : set([('q', 'x')])}, \
    a2.get_usage()
print bt.get_assignment_positions_for_branches("a", ax) == [1], \
    bt.get_assignment_positions_for_branches("a", ax)
print bt.get_assignment_positions_for_branches("a", aq) == [0, 1], \
    bt.get_assignment_positions_for_branches("a", aq)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# a.p
# if ...:
#   a.x
# elif ...:
#   a.y; a.z
# else:
#   ...
# a.q

bt = branching.BranchTracker()
a = bt.assign_names(["a"])
bt.use_attribute("a", "p")
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
ax = bt.use_attribute("a", "x")
bt.shelve_branch()
bt.new_branch()                     # elif ...
ay = bt.use_attribute("a", "y")
az = bt.use_attribute("a", "z")
bt.shelve_branch()
bt.new_branch()                     # else
bt.shelve_branch()
bt.merge_branches()                 # end
bt.use_attribute("a", "q")

print a.get_usage() == \
    {'a' : set([('p', 'q'), ('p', 'q', 'x'), ('p', 'q', 'y', 'z')])}, \
    a.get_usage()
print bt.get_assignment_positions_for_branches("a", ax) == [0], \
    bt.get_assignment_positions_for_branches("a", ax)
print bt.get_assignment_positions_for_branches("a", ay) == [0], \
    bt.get_assignment_positions_for_branches("a", ay)
print bt.get_assignment_positions_for_branches("a", az) == [0], \
    bt.get_assignment_positions_for_branches("a", az)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# a.p
# while ...:
#   a.x
# a.q

bt = branching.BranchTracker()
a = bt.assign_names(["a"])
bt.use_attribute("a", "p")
bt.new_branchpoint(True)            # begin
bt.new_branch(True)                 # while ...
ax = bt.use_attribute("a", "x")
bt.resume_continuing_branches()
bt.shelve_branch(True)
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.resume_broken_branches()
bt.use_attribute("a", "q")

print a.get_usage() == \
    {'a' : set([('p', 'q'), ('p', 'q', 'x')])}, a.get_usage()
print bt.get_assignment_positions_for_branches("a", ax) == [0], \
    bt.get_assignment_positions_for_branches("a", ax)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# a.p
# while ...:
#   if ...:
#     a.x
#   else ...:
#     a.y
# a.q

bt = branching.BranchTracker()
a = bt.assign_names(["a"])
bt.use_attribute("a", "p")
bt.new_branchpoint(True)            # begin
bt.new_branch(True)                 # while ...
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
ax = bt.use_attribute("a", "x")
bt.shelve_branch()
bt.new_branch()
ay = bt.use_attribute("a", "y")
bt.shelve_branch()
bt.merge_branches()                 # end
bt.resume_continuing_branches()
bt.shelve_branch(True)
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.resume_broken_branches()
bt.use_attribute("a", "q")

print a.get_usage() == \
    {'a' : set([('p', 'q'), ('p', 'q', 'x'), ('p', 'q', 'y')])}, \
    a.get_usage()
print bt.get_assignment_positions_for_branches("a", ax) == [0], \
    bt.get_assignment_positions_for_branches("a", ax)
print bt.get_assignment_positions_for_branches("a", ay) == [0], \
    bt.get_assignment_positions_for_branches("a", ay)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# a.p
# while ...:
#   if ...:
#     a = ...
#     a.x
#   else ...:
#     a.y
# a.q

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.use_attribute("a", "p")
bt.new_branchpoint(True)            # begin
bt.new_branch(True)                 # while ...
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
a2 = bt.assign_names(["a"])         # a = ...
ax = bt.use_attribute("a", "x")
bt.shelve_branch()
bt.new_branch()
ay = bt.use_attribute("a", "y")
bt.shelve_branch()
bt.merge_branches()                 # end
bt.resume_continuing_branches()
bt.shelve_branch(True)
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.resume_broken_branches()
bt.use_attribute("a", "q")

print a1.get_usage() == \
    {'a' : set([('p', 'q'), ('p', 'q', 'y'), ('p',)])}, a1.get_usage()
print a2.get_usage() == \
    {'a' : set([('q', 'x')])}, a2.get_usage()
print bt.get_assignment_positions_for_branches("a", ax) == [1], \
    bt.get_assignment_positions_for_branches("a", ax)
print bt.get_assignment_positions_for_branches("a", ay) == [0, 1], \
    bt.get_assignment_positions_for_branches("a", ay)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# a.p
# while ...:
#   if ...:
#     a.y
#   else ...:
#     a = ...
#     a.x
# a.q

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.use_attribute("a", "p")
bt.new_branchpoint(True)            # begin
bt.new_branch(True)                 # while ...
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
ay = bt.use_attribute("a", "y")
bt.shelve_branch()
bt.new_branch()
a2 = bt.assign_names(["a"])         # a = ...
ax = bt.use_attribute("a", "x")
bt.shelve_branch()
bt.merge_branches()                 # end
bt.resume_continuing_branches()
bt.shelve_branch(True)
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.resume_broken_branches()
bt.use_attribute("a", "q")

print a1.get_usage() == \
    {'a' : set([('p', 'q'), ('p', 'q', 'y'), ('p',)])}, a1.get_usage()
print a2.get_usage() == \
    {'a' : set([('q', 'x')])}, a2.get_usage()
print bt.get_assignment_positions_for_branches("a", ax) == [1], \
    bt.get_assignment_positions_for_branches("a", ax)
print bt.get_assignment_positions_for_branches("a", ay) == [0, 1], \
    bt.get_assignment_positions_for_branches("a", ay)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# a.p
# while ...:
#   a = ...
#   a.x
# a.q

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
ap = bt.use_attribute("a", "p")
bt.new_branchpoint(True)            # begin
bt.new_branch(True)                 # while ...
a2 = bt.assign_names(["a"])         # a = ...
ax = bt.use_attribute("a", "x")
bt.resume_continuing_branches()
bt.shelve_branch(True)
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.resume_broken_branches()
aq = bt.use_attribute("a", "q")

print a1.get_usage() == \
    {'a' : set([('p', 'q'), ('p',)])}, a1.get_usage()
print a2.get_usage() == \
    {'a' : set([('q', 'x')])}, a2.get_usage()
print bt.get_assignment_positions_for_branches("a", ax) == [1], \
    bt.get_assignment_positions_for_branches("a", ax)
print bt.get_assignment_positions_for_branches("a", ap) == [0], \
    bt.get_assignment_positions_for_branches("a", ap)
print bt.get_assignment_positions_for_branches("a", aq) == [0, 1], \
    bt.get_assignment_positions_for_branches("a", aq)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# a.p
# while ...:
#   if ...:
#     break
#   a.q
# a.r

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.use_attribute("a", "p")
bt.new_branchpoint(True)            # begin
bt.new_branch(True)                 # while ...
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
bt.suspend_broken_branch()          # break
bt.shelve_branch()
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.use_attribute("a", "q")
bt.resume_continuing_branches()
bt.shelve_branch(True)
bt.merge_branches()                 # end
bt.resume_broken_branches()
bt.use_attribute("a", "r")

print a1.get_usage() == \
    {'a' : set([('p', 'q', 'r'), ('p', 'r')])}, a1.get_usage()
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# a.p and a.q and a.r

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.new_branchpoint()                # begin
bt.new_branch()
bt.use_attribute("a", "p")
bt.new_branchpoint()                # begin
bt.new_branch()
bt.use_attribute("a", "q")
bt.new_branchpoint()                # begin
bt.new_branch()
bt.use_attribute("a", "r")
bt.shelve_branch()
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.shelve_branch()
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.shelve_branch()
bt.merge_branches()                 # end

print a1.get_usage() == \
    {'a' : set([('p', 'q', 'r'), ('p', 'q'), ('p',)])}, a1.get_usage()
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# if ...:
#   a.p
#   return
# a.q

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
bt.use_attribute("a", "p")
bt.abandon_returning_branch()
bt.shelve_branch()
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.use_attribute("a", "q")

print a1.get_usage() == \
    {'a' : set([('p',), ('q',)])}, a1.get_usage()
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# try:
#   if ...:
#     a.p
#     return
#   a.q
# except:
#   a.r

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.new_branchpoint()                # begin (try)
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
bt.use_attribute("a", "p")
bt.abandon_returning_branch()
bt.shelve_branch()                  # ... if
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.use_attribute("a", "q")
bt.resume_abandoned_branches()      # except
bt.use_attribute("a", "r")
bt.shelve_branch()
bt.merge_branches()                 # end

print a1.get_usage() == \
    {'a' : set([('p',), ('q', 'r')])}, a1.get_usage()
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# if ...:
#   a.p
# a = ...
# if ...:
#   a.q

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
ap = bt.use_attribute("a", "p")
bt.abandon_branch()
bt.shelve_branch()                  # ... if
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
a2 = bt.assign_names(["a"])
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
aq = bt.use_attribute("a", "q")
bt.abandon_branch()
bt.shelve_branch()                  # ... if
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end

print a1.get_usage() == \
    {'a' : set([('p',), ()])}, a1.get_usage()
print a2.get_usage() == \
    {'a' : set([('q',), ()])}, a2.get_usage()
print bt.get_assignment_positions_for_branches("a", ap) == [0], \
    bt.get_assignment_positions_for_branches("a", ap)
print bt.get_assignment_positions_for_branches("a", aq) == [1], \
    bt.get_assignment_positions_for_branches("a", aq)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = {}
# a.p
# if ...:
#   a = ...
#   a.x
# else:
#   ...
# a.q

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"], ["<instance>:__builtins__.dict.dict"])
ap = bt.use_attribute("a", "p")
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
a2 = bt.assign_names(["a"])         # a = ...
ax = bt.use_attribute("a", "x")
bt.shelve_branch()
bt.new_branch()                     # else
bt.shelve_branch()
bt.merge_branches()                 # end
aq = bt.use_attribute("a", "q")

print a1.get_usage() == \
    {'a' : set([('p',), ('p', 'q')])}, \
    a1.get_usage()
print a2.get_usage() == \
    {'a' : set([('q', 'x')])}, \
    a2.get_usage()
print bt.get_assignment_positions_for_branches("a", ap) == [0], \
    bt.get_assignment_positions_for_branches("a", ap)
print bt.get_assignment_positions_for_branches("a", ax) == [1], \
    bt.get_assignment_positions_for_branches("a", ax)
print bt.get_assignment_positions_for_branches("a", aq) == [0, 1], \
    bt.get_assignment_positions_for_branches("a", aq)
names.append(bt.assignments["a"])

# Equivalent to...
#
# if ...:
#   a = ...
#   a.x
# else:
#   ...
# a.q

bt = branching.BranchTracker()
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
a1 = bt.assign_names(["a"])         # a = ...
ax = bt.use_attribute("a", "x")
bt.shelve_branch()
bt.new_branch()                     # else
bt.shelve_branch()
bt.merge_branches()                 # end
aq = bt.use_attribute("a", "q")

print a1.get_usage() == \
    {'a' : set([('q', 'x')])}, \
    a1.get_usage()
print bt.get_assignment_positions_for_branches("a", aq) == [None, 0], \
    bt.get_assignment_positions_for_branches("a", aq)
names.append(bt.assignments["a"])

# Equivalent to...
#
# if ...:
#   a = ...
#   return
# a.q

bt = branching.BranchTracker()
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
a1 = bt.assign_names(["a"])
bt.abandon_returning_branch()
bt.shelve_branch()
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
aq = bt.use_attribute("a", "q")

print a1.get_usage() == \
    {'a' : set([()])}, a1.get_usage()
print bt.get_assignment_positions_for_branches("a", aq) == [None], \
    bt.get_assignment_positions_for_branches("a", aq)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# try:
#   if ...:
#     a.p
#     return
#   a.q
# finally:
#   a.r

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
bt.use_attribute("a", "p")
bt.abandon_returning_branch()
bt.shelve_branch()                  # ... if
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.use_attribute("a", "q")
branches = bt.resume_all_abandoned_branches()
bt.use_attribute("a", "r")
bt.restore_active_branches(branches)

print a1.get_usage() == \
    {'a' : set([('p', 'r'), ('q', 'r')])}, a1.get_usage()
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# try:
#   if ...:
#     a = ...
#     a.p
#     return
#   a.q
# finally:
#   a.r

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
a2 = bt.assign_names(["a"])
bt.use_attribute("a", "p")
bt.abandon_returning_branch()
bt.shelve_branch()                  # ... if
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
aq = bt.use_attribute("a", "q")
branches = bt.resume_all_abandoned_branches()
ar = bt.use_attribute("a", "r")
bt.restore_active_branches(branches)

print a1.get_usage() == \
    {'a' : set([(), ('q', 'r')])}, a1.get_usage()
print a2.get_usage() == \
    {'a' : set([('p', 'r')])}, a2.get_usage()
print bt.get_assignment_positions_for_branches("a", ar) == [0, 1], \
    bt.get_assignment_positions_for_branches("a", ar)
names.append(bt.assignments["a"])

# Equivalent to...
#
# a = ...
# try:
#   if ...:
#     a = ...
#     a.p
#     return
#   a.q
# except:
#   a.r

bt = branching.BranchTracker()
a1 = bt.assign_names(["a"])
bt.new_branchpoint()                # begin (try)
bt.new_branchpoint()                # begin
bt.new_branch()                     # if ...
a2 = bt.assign_names(["a"])
bt.use_attribute("a", "p")
bt.abandon_returning_branch()
bt.shelve_branch()                  # ... if
bt.new_branch()                     # (null)
bt.shelve_branch()
bt.merge_branches()                 # end
bt.use_attribute("a", "q")
bt.resume_abandoned_branches()      # except
ar = bt.use_attribute("a", "r")
bt.shelve_branch()
bt.merge_branches()                 # end

print a1.get_usage() == \
    {'a' : set([(), ('q', 'r')])}, a1.get_usage()
print a2.get_usage() == \
    {'a' : set([('p',)])}, a2.get_usage()
print bt.get_assignment_positions_for_branches("a", ar) == [0, 1], \
    bt.get_assignment_positions_for_branches("a", ar)
names.append(bt.assignments["a"])

# vim: tabstop=4 expandtab shiftwidth=4
