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

# Explicit function for addition purposes.

def combine(x, y, z):
    return x + y + z

class Tree:
    def __init__(self, item, left=None, right=None):
        self.item = item
        self.left = left
        self.right = right

    def count(self):
        if self.left and self.right:
            # Test calls in parameter lists needing separate temporary storage.
            return combine(self.item, self.left.count(), self.right.count())
        else:
            return self.item

tree = \
    Tree(10000,
        Tree(2000,
            Tree(300),
            Tree(40)
            ),
        Tree(5))

print tree.count()                      # 12345
