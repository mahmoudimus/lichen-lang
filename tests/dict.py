def f(d):
    return d.keys()

def g(d):
    for key, value in d.items():
        return value

d = {10 : "a", 20 : "b", "c" : 30, (1, 2) : "d"}
print "# d: ",
print d
print d[10]                             # a
print d[20]                             # b
print d["c"]                            # 30
print d[(1, 2)]                         # d
try:
    print d[30]                         # should fail with an exception
except KeyError, exc:
    print "d[30]: key not found", exc.key
print d.get(30)                         # None
print d.get(30, "c")                    # c
print d.has_key(20)                     # True
print d.has_key(30)                     # False

l = f(d)
print "# l: ",
print l
print 10 in l                          	# True
print 20 in l                          	# True
print "c" in l                          # True
print "d" in l                          # False
print 30 in l                          	# False
print (1, 2) in l                       # True

l = d.values()
print "# l: ",
print l
print "a" in l                          # True
print "b" in l                          # True
print "c" in l                          # False
print "d" in l                          # True
print 30 in l                           # True
print (1, 2) in l                       # False

v = g(d) # either "a" or "b" or 30 or "d"
print "# v: ",
print v
print v == "a" or v == "b" or v == 30 or v == "d"   # True
print v == 10 or v == 20 or v == "c" or v == (1, 2) # False

l = d.items()
print "# l: ",
print l
print (10, "a") in l                    # True
print ("c", 30) in l                    # True
print ((1, 2), "d") in l                # True
print (10, "b") in l                    # False

# Try to put a list key in a dictionary.

try:
    d[[1, 2]] = "e"
    print d[[1, 2]]
except TypeError:
    print "d[[1, 2]]: key not appropriate"

# Attempt to remove items.

del d[20]
print d.has_key(20)                     # False
try:
    del d[30]                           # should fail with an exception
except KeyError, exc:
    print "del d[30]: key not found", exc.key

# Clear the dictionary.

d.clear()
print d                                 # {}
