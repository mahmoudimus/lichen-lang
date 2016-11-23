import package.module

C = module.Class
c = module
f = c.Class

def t():
    x = c.Class
    return x

print C.attr
print f.attr
print t().attr
