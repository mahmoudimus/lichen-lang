class fib:
    def __init__(self):
        self.a, self.b = 0, 1

    def next(self):
        result = self.b
        #self.a, self.b = self.b, self.a + self.b
        self.b, self.a = self.a + self.b, result
        return result

seq = fib()
i = 0
while i < 10:
    print seq.next()
    i += 1
