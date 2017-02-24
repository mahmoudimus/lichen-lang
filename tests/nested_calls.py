class C:
    def __init__(self, x):
        self.x = x

    def value(self):
        return self.x

    def length(self):
        return self.double(self.value())

    def double(self, x):
        return x * 2

c = C(3)
print c.length()                        # 6
