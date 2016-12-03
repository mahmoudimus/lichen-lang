import sys

print sys.maxint
print sys.minint

print sys.maxint + sys.minint

i = 2 ** 30
print i                                 # 1073741824

j = -2 ** 30
print j                                 # -1073741824

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
