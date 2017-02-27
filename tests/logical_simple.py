a = 1
b = 2
c = a and b
print c                             # 2

d = a or b
print d                             # 1

e = not a
print e                             # False

if a and b:
    print "a and b"                 # a and b

if not (a and b):
    print "not (a and b)"           #

if not not (a and b):
    print "not not (a and b)"       # not not (a and b)

if a or b:
    print "a or b"                  # a or b

if not (a or b):
    print "not (a or b)"            #

if not not (a or b):
    print "not not (a or b)"        # not not (a or b)
