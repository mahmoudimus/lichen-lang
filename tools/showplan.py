#!/usr/bin/env python

from os.path import abspath, exists, join, split
import sys

# Find the modules.

try:
    import encoders
except ImportError:
    parent = abspath(split(split(__file__)[0])[0])
    if split(parent)[1] == "Lichen":
        sys.path.append(parent)

from encoders import decode_access_location

if len(sys.argv) < 3:
    print >>sys.stderr, "Usage: %s <directory> <access>" % sys.argv[0]
    sys.exit(1)

dirname = sys.argv[1]
access = sys.argv[2]

filename = join(dirname, "_deduced", "attribute_plans")

if not exists(filename):
    print >>sys.stderr, "Directory %s does not provide file %s." % (dirname, filename)
    sys.exit(1)

f = open(filename)
try:
    for line in f.xreadlines():
        columns = line.rstrip().split()
        if not columns[0].startswith(access):
            continue

        location, name, test, test_type, base, traversed, traversal_modes, \
        traversal_attrnames, context, context_test, \
        first_method, final_method, attr, accessor_kinds = columns

        path, _name, attrnames, access_number = decode_access_location(location)

        print "Location:", location
        print "Name:", name
        print "Attribute names:", attrnames
        print "Access number:", access_number
        print "Test:", test
        print "Test type:", test_type
        print "Base:", base
        print "Traversed:", traversed
        print "Traversal modes:", traversal_modes
        print "Traversed attributes:", traversal_attrnames
        print "Context:", context
        print "Context test:", context_test
        print "First method:", first_method
        print "Final method:", final_method
        print "Origin/attribute:", attr
        print "Accessor kinds:", accessor_kinds
        print

finally:
    f.close()

# vim: tabstop=4 expandtab shiftwidth=4
