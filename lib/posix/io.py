#!/usr/bin/env python

def close(fd): pass
def closerange(fd_low, fd_high): pass
def dup(fd): pass
def dup2(old_fd, new_fd): pass
def fchdir(fildes): pass
def fchmod(fd, mode): pass
def fchown(fd, uid, gid): pass
def fdatasync(fildes): pass
def fdopen(fd, mode='r', bufsize=None): pass
def fpathconf(fd, name): pass
def fstat(fd): pass
def fstatvfs(fd): pass
def fsync(fildes): pass
def ftruncate(fd, length): pass
def isatty(fd): pass
def lseek(fd, pos, how): pass
def open(filename, flag, mode=0777): pass
def openpty(): pass
def pipe(): pass
def putenv(key, value): pass
def times(): pass
def ttyname(fd): pass
def umask(new_mask): pass
def uname(): pass
def unsetenv(key): pass
def write(fd, string): pass

O_APPEND = 1024
O_ASYNC = 8192
O_CREAT = 64
O_DIRECT = 16384
O_DIRECTORY = 65536
O_DSYNC = 4096
O_EXCL = 128
O_LARGEFILE = 32768
O_NDELAY = 2048
O_NOATIME = 262144
O_NOCTTY = 256
O_NOFOLLOW = 131072
O_NONBLOCK = 2048
O_RDONLY = 0
O_RDWR = 2
O_RSYNC = 1052672
O_SYNC = 1052672
O_TRUNC = 512
O_WRONLY = 1

SEEK_CUR = 1
SEEK_END = 2
SEEK_SET = 0

# vim: tabstop=4 expandtab shiftwidth=4
