s = set()
s.add(10)
s.add(20)
s.add("c")
s.add((1, 2))
print "# s:",
print s
print 10 in s
print 20 in s
print "c" in s
print 30 in s
print (1, 2) in s

s2 = set([10, 20, "c", (1, 2)])
print "# s2:",
print s
print 10 in s2
print 20 in s2
print "c" in s2
print 30 in s2
print (1, 2) in s2
