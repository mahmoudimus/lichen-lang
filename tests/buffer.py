b = buffer()
b.append("Hello")
b.append(" ")
b.append("world")
b.append("!")
print b

b = buffer(["Hello "])
print b
b2 = buffer(["world!"])
b.append(b2)
print b
