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

# Test equality.

print l == [1, 2, 3]         # False
print l == [1, 2, 3, "four"] # True

# Test concatenation.

a = [1, 2]
a += [3, 4]
print a                 # [1, 2, 3, 4]

b = [5, 6]
c = a + b
print c                 # [1, 2, 3, 4, 5, 6]

a2 = a * 2
print a2                # [1, 2, 3, 4, 1, 2, 3, 4]

# Test removal.

print c.pop()           # 6
print c                 # [1, 2, 3, 4, 5]

d = []
try:
    d.pop()             # should raise an exception
except IndexError, exc:
    print "d.pop(): failed to access item", exc.index
