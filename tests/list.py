l = [1, 2, 3]
l.append("four")
print len(l)            # 4
print l[0]              # 1
print l[1]              # 2
print l[2]              # 3
print l[3]              # four
print l[-1]             # four
print l[-2]             # 3
print l[-3]             # 2
print l[-4]             # 1
print l                 # [1, 2, 3, "four"]

t = (1, 2, 3, "four")
l = list(t)
print l                 # [1, 2, 3, "four"]

try:
    print l[4]          # should raise an exception
except IndexError, exc:
    print "l[4]: failed with argument", exc.index

try:
    print l[-5]         # should raise an exception
except IndexError, exc:
    print "l[-5]: failed with argument", exc.index

print 1 in l            # True
print 4 in l            # False
print "four" in l       # True
print "one" in l        # False
print 1 not in l        # False
print 4 not in l        # True
print "four" not in l   # False
print "one" not in l    # True

print l.index(1)        # 0
print l.index("four")   # 3

try:
    print l.index(4)    # should raise an exception
except ValueError, exc:
    print "l.index(4): failed to find argument", exc.value
