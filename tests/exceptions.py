# Raise an instance of TypeError.

try:
    raise TypeError()
except TypeError, exc:
    print "Handled", exc

# Raise TypeError, causing instantiation.

try:
    raise TypeError
except TypeError, exc:
    print "Handled", exc
