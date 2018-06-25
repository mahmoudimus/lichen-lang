#!/usr/bin/env python

from os.path import abspath, split
import sys

# Find the modules.

try:
    import encoders
except ImportError:
    parent = abspath(split(split(__file__)[0])[0])
    if split(parent)[1] == "Lichen":
        sys.path.append(parent)

from encoders import decode_alias_location

if len(sys.argv) < 3:
    print >>sys.stderr, "Usage: %s <filename> <alias>" % sys.argv[0]
    sys.exit(1)

filename = sys.argv[1]
alias = sys.argv[2]

f = open(filename)
try:
    for line in f.xreadlines():
        columns = line.rstrip().split(" ")
        if not columns[0].startswith(alias):
            continue

        first = True

        for column in columns:
            location = decode_alias_location(column.rstrip(","))
            path, name, attrnames, version, access_number, invocation = location

            print first and "Alias:" or "Path:", path
            print "Name:", name
            print "Attribute names:", attrnames
            print "Version:", version is None and "{}" or version
            print "Access number:", access_number is None and "{}" or access_number
            print "Invocation:", invocation and "true" or "false"
            print

            first = False

        print "----"
        print

finally:
    f.close()

# vim: tabstop=4 expandtab shiftwidth=4
