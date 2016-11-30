def f(d):
    return d.keys()

#def g(d):
#    for key, value in d.items():
#        return value

d = {10 : "a", 20 : "b"}
l = f(d)
print 10 in l                          	# True
print 20 in l                          	# True
print 30 in l                          	# False

l = d.values()
print "a" in l                          # True
print "b" in l                          # True
print "c" in l                          # False


#v = g(d) # either "a" or "b"
#print v == "a" or v == "b"              # True
