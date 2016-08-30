#!/usr/bin/env python

CODESIZE = 4
MAGIC = 20140812

class RegexObject:

    def __init__(self, flags, groups, groupindex, pattern):
        self.flags = flags
        self.groups = groups
        self.groupindex = groupindex
        self.pattern = pattern

    def search(self, string, pos=None, endpos=None): pass
    def match(self, string, pos=None, endpos=None): pass
    def split(self, string, maxsplit=0): pass
    def findall(self, string, pos=None, endpos=None): pass
    def finditer(self, string, pos=None, endpos=None): pass
    def sub(self, repl, string, count=0): pass
    def subn(self, repl, string, count=0): pass

class MatchObject:

    def __init__(self, pos, endpos, lastindex, lastgroup, re, string):
        self.pos = pos
        self.endpos = endpos
        self.lastindex = lastindex
        self.lastgroup = lastgroup
        self.re = re
        self.string = string

    def expand(self, template): pass
    def group(self, *groups): pass
    def groups(self, default=None): pass
    def groupdict(self, default=None): pass
    def start(self, group=None): pass
    def end(self, group=None): pass
    def span(self, group=None): pass

def compile(pattern, flags=0): pass
def getcodesize(): pass
def getlower(c): pass

# vim: tabstop=4 expandtab shiftwidth=4
