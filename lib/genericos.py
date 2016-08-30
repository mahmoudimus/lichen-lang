#!/usr/bin/env python

from posix.io import fstat
from posix.filesys import listdir, lstat, readlink
from posix.process import getcwd, getcwdu, getuid

class OSError(EnvironmentError):
    pass

error = OSError
environ = {}
    
def execl(file, *args): pass
def execle(file, *args): pass
def execlp(file, *args): pass
def execlpe(file, *args): pass
def execv(path, args): pass
def execve(path, args, env): pass
def execvp(file, args): pass
def execvpe(file, args, env): pass
def getenv(key, default=None): pass
def makedirs(name, mode=511): pass
def popen2(cmd, mode='t', bufsize=-1): pass
def popen3(cmd, mode='t', bufsize=-1): pass
def popen4(cmd, mode='t', bufsize=-1): pass
def removedirs(name): pass
def renames(old, new): pass
def spawnl(mode, file, *args): pass
def spawnle(mode, file, *args): pass
def spawnlp(mode, file, *args): pass
def spawnlpe(mode, file, *args): pass
def spawnv(mode, file, args): pass
def spawnve(mode, file, args, env): pass
def spawnvp(mode, file, args): pass
def spawnvpe(mode, file, args, env): pass
def walk(top, topdown=True, onerror=None, followlinks=False): pass

P_WAIT = 0
P_NOWAIT = P_NOWAITO = 1

SEEK_CUR = 1
SEEK_END = 2
SEEK_SET = 0

name = 'posix'
linesep = '\n'

# vim: tabstop=4 expandtab shiftwidth=4
