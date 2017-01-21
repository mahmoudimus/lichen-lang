class Expr:

    "An expression."

    def __init__(self, ops):
        self.ops = ops

    def children(self):
        return self.ops

class Binary:

    "A binary operator."

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def children(self):
        return self.left, self.right

class Unary:

    "A unary operator."

    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def children(self):
        return self.operand,

class Value:

    "A general value."

    def __init__(self, value):
        self.value = value

    def children(self):
        return ()

class Visitor:

    "Visit nodes in an expression tree."

    def __init__(self):
        self.indent = 0

    def visit(self, node):

        # Obtain the method for the node name.

        fn = getattr(self, node.__name__)

        # Call the method.

        fn(node)

        # Visit the node's children.

        self.visitChildren(node)

    def visitChildren(self, node):
        self.indent += 1
        for n in node.children():
            self.visit(n)
        self.indent -= 1

    def writeIndent(self):
        i = 0
        while i < self.indent:
            print "",
            i += 1

    def Expr(self, node):
        self.writeIndent()
        print "Expression..."

    def Binary(self, node):
        self.writeIndent()
        print "Binary operation", node.op

    def Unary(self, node):
        self.writeIndent()
        print "Unary operation", node.op

    def Value(self, node):
        self.writeIndent()
        print "Value", node.value

# Test the visitor with an example expression.

expr = Expr([Binary(Value(1), "+", Binary(Unary("-", Value(2)), "*", Value(3)))])
Visitor().visit(expr)
