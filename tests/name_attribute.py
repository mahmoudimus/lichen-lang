import operator

class C:
    pass

c = C()
print c.__name__                        # __main__.C
print C.__name__                        # __main__.C

# If it were defined, operator.__name__ would be __builtins__.core.module.

print operator.__mname__

# If it were defined, operator.add.__name__ would be __builtins__.core.function.

print operator.add.__fname__
