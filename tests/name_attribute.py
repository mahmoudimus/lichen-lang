import operator

class C:
    def f(self): pass

c = C()
print c.__name__                        # C
print c.__oname__                       # __main__
print C.__name__                        # C
print C.__oname__                       # __main__
print c.f.__fname__                     # f
print c.f.__oname__                     # __main__.C
print C.f.__fname__                     # f
print C.f.__oname__                     # __main__.C

# If it were defined, operator.__name__ would be module.

print operator.__mname__                # operator

# If it were defined, operator.add.__name__ would be function.

print operator.add.__fname__            # add
print operator.add.__oname__            # operator.binary
