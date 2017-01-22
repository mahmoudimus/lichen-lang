class C:
    def __init__(self):
        self.x = 1
        self.y = 2
        self.z = 3

class D:
    def __init__(self):
        self.x = 4
        self.y = 5
        self.z = 6

c = C()
d = D()

attrnames = ["a", "b", "c", "x", "y", "z"]

print ". c d"

for attrname in attrnames:
    print attrname, hasattr(c, attrname) and "1" or "0", hasattr(d, attrname) and "1" or "0"

print
print ". c d"

for attrname in attrnames:
    print attrname,
    try:
        v = getattr(c, attrname)
        print v,
    except AttributeError:
        print "?",

    try:
        v = getattr(d, attrname)
        print v
    except AttributeError:
        print "?"

try:
    setattr(c, "x", 7)
except NotImplementedError, exc:
    print 'setattr(c, "x", 7): not implemented:', exc.name
