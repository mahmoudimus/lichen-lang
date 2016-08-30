#!/usr/bin/env python

class stat_result:
    def __init__(self, st_atime, st_blksize, st_blocks, st_ctime, st_dev, st_gid, st_ino, st_mode, st_mtime, st_nlink, st_rdev, st_size, st_uid):
        self.st_atime = st_atime
        self.st_blksize = st_blksize
        self.st_blocks = st_blocks
        self.st_ctime = st_ctime
        self.st_dev = st_dev
        self.st_gid = st_gid
        self.st_ino = st_ino
        self.st_mode = st_mode
        self.st_mtime = st_mtime
        self.st_nlink = st_nlink
        self.st_rdev = st_rdev
        self.st_size = st_size
        self.st_uid = st_uid

    n_fields = 16
    n_sequence_fields = 10
    n_unnamed_fields = 3

class statvfs_result:
    def __init__(self, f_bavail, f_bfree, f_blocks, f_bsize, f_favail, f_ffree, f_files, f_flag, f_frsize, f_namemax):
        self.f_bavail = f_bavail
        self.f_bfree = f_bfree
        self.f_blocks = f_blocks
        self.f_bsize = f_bsize
        self.f_favail = f_favail
        self.f_ffree = f_ffree
        self.f_files = f_files
        self.f_flag = f_flag
        self.f_frsize = f_frsize
        self.f_namemax = f_namemax

    n_fields = 10
    n_sequence_fields = 10
    n_unnamed_fields = 0

def stat(path): pass
def stat_float_times(newval=None): pass
def statvfs(path): pass

ST_APPEND = 256
ST_MANDLOCK = 64
ST_NOATIME = 1024
ST_NODEV = 4
ST_NODIRATIME = 2048
ST_NOEXEC = 8
ST_NOSUID = 2
ST_RDONLY = 1
ST_RELATIME = 4096
ST_SYNCHRONOUS = 16
ST_WRITE = 128

# vim: tabstop=4 expandtab shiftwidth=4
