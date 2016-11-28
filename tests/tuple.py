l = (1, 2, 3, "four")
print len(l)            # 4
print l[0]              # 1
print l[1]              # 2
print l[2]              # 3
print l[3]              # four
print l[-1]             # four
print l[-2]             # 3
print l[-3]             # 2
print l[-4]             # 1
print l                 # (1, 2, 3, "four")

l = [1, 2, 3, "four"]
t = tuple(l)
print t                 # (1, 2, 3, "four")

try:
    print t[4]          # should raise an exception
except IndexError, exc:
    print "t[4]: failed with argument", exc.index

try:
    print t[-5]         # should raise an exception
except IndexError, exc:
    print "t[-5]: failed with argument", exc.index
