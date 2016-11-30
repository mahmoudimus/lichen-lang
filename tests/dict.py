def f(d):
    return d.keys()

def g(d):
    for key, value in d.items():
        return value

d = {10 : "a", 20 : "b"}
print d[10]                             # a
print d[20]                             # b
try:
    print d[30]                         # should fail with an exception
except KeyError, exc:
    print "d[30]: key not found", exc.key

l = f(d)
print l
print 10 in l                          	# True
print 20 in l                          	# True
print 30 in l                          	# False

l = d.values()
print l
print "a" in l                          # True
print "b" in l                          # True
print "c" in l                          # False

v = g(d) # either "a" or "b"
print v
print v == "a" or v == "b"              # True
print v == 10 or v == 20                # False

l = d.items()
print l
print (10, "a") in l                    # True
print (10, "b") in l                    # False
