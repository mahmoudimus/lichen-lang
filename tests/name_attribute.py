import operator

class C:
    pass

c = C()
print c.__name__                        # C
print c.__mname__                       # __main__
print C.__name__                        # C
print C.__mname__                       # __main__

# If it were defined, operator.__name__ would be module.

print operator.__mname__                # operator

# If it were defined, operator.add.__name__ would be function.

print operator.add.__fname__            # add
print operator.add.__mname__            # operator.binary
