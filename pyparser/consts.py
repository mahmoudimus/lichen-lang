"""
Various flags used during the compilation process.
"""

PyCF_SOURCE_IS_UTF8 = 0x0100
PyCF_DONT_IMPLY_DEDENT = 0x0200
PyCF_ONLY_AST = 0x0400
PyCF_ACCEPT_NULL_BYTES = 0x10000000   # PyPy only, for compile()
