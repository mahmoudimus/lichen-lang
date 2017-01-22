import operator

class C:
    def f(self): pass

def name(x):
    print x.__name__
    print x.__parent__.__name__
    print str(x)

def attrname(x):
    print x.f.__name__
    print x.f.__parent__.__name__
    print str(x.f)

c = C()
print c.__name__                        # C
print c.__parent__.__name__             # __main__
print str(c)                            # <__main__.C instance>
print C.__name__                        # C
print C.__parent__.__name__             # __main__
print str(C)                            # __main__.C
print c.f.__name__                      # f
print c.f.__parent__.__name__           # C
print str(c.f)                          # __main__.C.f
print C.f.__name__                      # f
print C.f.__parent__.__name__           # C
print str(C.f)                          # __main__.C.f

name(c)                                 # C
                                        # __main__
                                        # <__main__.C instance>
name(C)                                 # C
                                        # __main__
                                        # __main__.C
attrname(c)                             # f
                                        # C
                                        # __main__.C.f
attrname(C)                             # f
                                        # C
                                        # __main__.C.f
name(c.f)                               # f
                                        # C
                                        # __main__.C.f
name(C.f)                               # f
                                        # C
                                        # __main__.C.f

# If it were defined, operator.__name__ would be module.

print operator.__name__                 # operator

# If it were defined, operator.add.__name__ would be function.

print operator.add.__name__             # add
print operator.add.__parent__.__name__  # operator.binary
