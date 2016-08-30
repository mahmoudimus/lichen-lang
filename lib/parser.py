#!/usr/bin/env python

class ASTType:
    pass

class ParserError(Exception):
    pass

class STType:
    pass

def ast2list(ast): pass
def ast2tuple(ast): pass
def compileast(ast, filename=None): pass
def compilest(st): pass
def expr(s): pass
def isexpr(ast): pass
def issuite(ast): pass
def sequence2ast(sequence): pass
def sequence2st(sequence): pass
def st2list(st, line_info=None, col_info=None): pass
def st2tuple(st, line_info=None, col_info=None): pass
def suite(suite): pass
def tuple2ast(sequence): pass
def tuple2st(sequence): pass

# vim: tabstop=4 expandtab shiftwidth=4
