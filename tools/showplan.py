#!/usr/bin/env python

import sys

if len(sys.argv) < 3:
    print >>sys.stderr, "Usage: %s <filename> <access>" % sys.argv[0]
    sys.exit(1)

filename = sys.argv[1]
access = sys.argv[2]

f = open(filename)
try:
    for line in f.xreadlines():
        columns = line.rstrip().split()
        if not columns[0].startswith(access):
            continue

        location, name, test, test_type, base, traversed, traversal_modes, \
        attrnames, context, context_test, first_method, final_method, attr, \
        accessor_kinds = columns

        print "Location:", location
        print "Name:", name
        print "Test:", test
        print "Test type:", test_type
        print "Base:", base
        print "Traversed:", traversed
        print "Traversal modes:", traversal_modes
        print "Attribute names:", attrnames
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
