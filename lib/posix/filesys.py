#!/usr/bin/env python

def access(path, mode): pass
def chdir(path): pass
def chmod(path, mode): pass
def chown(path, uid, gid): pass
def lchown(path, uid, gid): pass
def link(src, dst): pass
def listdir(path): pass
def lstat(path): pass
def major(device): pass
def makedev(major, minor): pass
def minor(device): pass
def mkdir(path, mode=0777): pass
def mkfifo(filename, mode=0666): pass
def mknod(filename, mode=0600, device=None): pass
def read(fd, buffersize): pass
def readlink(path): pass
def remove(path): pass
def rename(old, new): pass
def rmdir(path): pass
def symlink(src, dst): pass
def unlink(path): pass
def utime(path, (atime, mtime)): pass

F_OK = 0
R_OK = 4
W_OK = 2
X_OK = 1

# vim: tabstop=4 expandtab shiftwidth=4
