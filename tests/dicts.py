def f(d):
    return d.keys()

def g(d):
    for key, value in d.items():
        return value

d = {"a" : 1, "b" : 2}
f(d) # ["a", "b"]
g(d) # either 1 or 2
