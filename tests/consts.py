def f():
    s = "test"
    m = s.__len__
    n = "test".__len__
    print m()
    print n()

def g():
    l = [1]
    m = l.__len__
    n = [1].__len__
    print m()
    print n()

f()
g()
