i = 2 ** 30
print i

j = -2 ** 30
print j

print i + j

try:
    print i - j
except OverflowError:
    print "i - j: overflow occurred"

print i / j

try:
    print i * j
except OverflowError:
    print "i * j: overflow occurred"
