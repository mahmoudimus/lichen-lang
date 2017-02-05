s = set()
s.add(10)
s.add(20)
s.add("c")
s.add((1, 2))

print "# s:",
print s                             # set([10, 20, "c", (1, 2))
print len(s)                        # 4
print 10 in s                       # True
print 20 in s                       # True
print "c" in s                      # True
print 30 in s                       # False
print (1, 2) in s                   # True

s2 = set([10, 20, "c", (1, 2)])

print "# s2:",
print s2                            # set([10, 20, "c", (1, 2))
print len(s2)                       # 4
print 10 in s2                      # True
print 20 in s2                      # True
print "c" in s2                     # True
print 30 in s2                      # False
print (1, 2) in s2                  # True

a = set([1, 3, 5, 7, 9])
b = set([1, 2, 3, 5, 7])

aub = a.union(b)
aib = a.intersection(b)
adb = a.difference(b)
asdb = a.symmetric_difference(b)

print len(aub)                      # 6
print len(aib)                      # 4
print len(adb)                      # 1
print len(asdb)                     # 2
print
print 1 in aub                      # True
print 1 in aib                      # True
print 1 in adb                      # False
print 1 in asdb                     # True
print
print 2 in aub                      # True
print 2 in aib                      # False
print 2 in adb                      # False
print 2 in asdb                     # False
print
print 9 in aub                      # True
print 9 in aib                      # False
print 9 in adb                      # True
print 9 in asdb                     # False
print

aub2 = a.copy()
aub2.update(b)
print len(aub2)                     # 6

aib2 = a.copy()
aib2.intersection_update(b)
print len(aib2)                     # 4

adb2 = a.copy()
adb2.difference_update(b)
print len(adb2)                     # 1

asdb2 = a.copy()
asdb2.symmetric_difference_update(b)
print len(asdb2)                    # 2
