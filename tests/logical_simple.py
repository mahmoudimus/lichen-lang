def no_temp(a, b):
    return not (a and b)

a = 1
b = 2
c = a and b
print c                             # 2

d = a or b
print d                             # 1

e = not a
print e                             # False

f = 0

g = no_temp(a, b)
print g                             # False

if a and b:
    print "a and b"                 # a and b
else:
    print "! (a and b)"

if a and f:
    print "a and f"
else:
    print "! (a and f)"             # ! (a and f)

if not (a and b):
    print "not (a and b)"
else:
    print "! (not (a and b))"       # ! (not (a and b))

if not not (a and b):
    print "not not (a and b)"       # not not (a and b)
else:
    print "! (not not (a and b))"

if a or b:
    print "a or b"                  # a or b
else:
    print "! (a or b)"

if not (a or b):
    print "not (a or b)"
else:
    print "! (not (a or b))"        # ! (not (a or b))

if not not (a or b):
    print "not not (a or b)"        # not not (a or b)
else:
    print "! (not not (a or b))"

if a and b or f:
    print "a and b or f"            # a and b or f
else:
    print "! (a and b or f)"
