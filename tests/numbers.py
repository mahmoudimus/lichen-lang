# -*- coding: ISO-8859-1 -*-

import sys

print "# sys.maxint: ",
print sys.maxint
print "# sys.minint: ",
print sys.minint

print "# sys.maxint + sys.minint: ",
print sys.maxint + sys.minint

i = 2 ** 30
print i                                 # 1073741824
print hex(i)                            # 0x40000000
print oct(i)                            # 010000000000

j = -2 ** 30
print j                                 # -1073741824
print hex(j)                            # -0x40000000
print oct(j)                            # -010000000000

print i + j                             # 0

try:
    print i - j
except OverflowError:
    print "i - j: overflow occurred"

print i / i                             # 1
print i / j                             # -1
print j / j                             # 1
print j / i                             # -1

try:
    print i * j
except OverflowError:
    print "i * j: overflow occurred"

print i - i                             # 0
print j - j                             # 0
print ~j                                # 1073741823
print i & ~j                            # 0
print i - 1 & ~j                        # 1073741823

print hex(31)                           # 0x1f
print oct(31)                           # 037

print "# hash(sys.maxint): ",
print hash(sys.maxint)

print "# hash((sys.maxint, 0)): ",
print hash((sys.maxint, 0))

print "# hash((sys.maxint - 1, 0)): ",
print hash((sys.maxint - 1, 0))

# Test combining numbers with strings.

s = "Number is " + str(123)
s2 = "æøå -> " + str(123)
print s.__class__
print s2.__class__
print s
print s2

sys.stdout.encoding = "UTF-8"
print s2
