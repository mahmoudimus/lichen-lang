b = buffer()
b.append("Hello")
b.append(" ")
b.append("world")
b.append("!")
print b                 # Hello world!

b = buffer(["Hello "])
print repr(b)           # buffer(["Hello "])

b2 = buffer(["world!"])
b.append(b2)
print b                 # Hello world!
