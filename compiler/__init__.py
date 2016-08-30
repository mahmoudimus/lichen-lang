"""Package for parsing and compiling Python source code

There are several functions defined at the top level that are imported
from modules contained in the package.

parse(buf, mode="exec") -> AST
    Converts a string containing Python source code to an abstract
    syntax tree (AST).  The AST is defined in compiler.ast.

parseFile(path) -> AST
    The same as parse(open(path))
"""

from compiler.transformer import parse, parseFile
