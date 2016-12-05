import package.module

C = module.Class
c = module
f = c.Class

def t():
    x = c.Class
    return x

print C.attr                    # 457
print f.attr                    # 457
print t().attr                  # 457
