def f():
    s = "test"
    m = s.__len__
    n = "test".__len__
    print m                 # __builtins__.str.basestring.__len__
    print m()               # 4
    print n                 # __builtins__.str.basestring.__len__
    print n()

def g():
    l = [1, 2]
    m = l.__len__
    n = [1, 2].__len__
    print l                 # [1, 2]
    print m                 # __builtins__.list.list.__len__
    print m()               # 2
    print n                 # __builtins__.list.list.__len__
    print n()               # 2

f()
g()
