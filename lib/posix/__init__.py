#!/usr/bin/env python

"POSIX support package."

from posix.core import name, linesep
from posix.conf import confstr, pathconf, strerror, sysconf
from posix.filesys import access, chdir, chmod, chown, lchown, link, listdir, \
                          lstat, major, makedev, minor, mkdir, mkfifo, mknod, \
                          readlink, remove, rename, rmdir, symlink, unlink, \
                          utime
from posix.io import close, closerange, dup, dup2, fchdir, fchmod, fchown, \
                     fdatasync, fdopen, fpathconf, fstat, fstatvfs, fsync, \
                     ftruncate, isatty, lseek, open, openpty, pipe, putenv, \
                     read, times, ttyname, umask, uname, unsetenv, write
from posix.process import abort, chroot, ctermid, execv, execve, fork, \
                          forkpty, getcwd, getcwdu, getegid, geteuid, getgid, \
                          getgroups, getloadavg, getlogin, getpgid, getpgrp, \
                          getpid, getppid, getresgid, getresuid, getsid, \
                          getuid, initgroups, kill, killpg, nice, popen, \
                          setegid, seteuid, setgid, setgroups, setpgid, \
                          setpgrp, setregid, setresgid, setresuid, setreuid, \
                          setsid, setuid, system, tcgetpgrp, tcsetpgrp, wait, \
                          wait3, wait4, waitpid
from posix.random import urandom
from posix.stat import stat, stat_float_times, statvfs
from posix.temp import tempnam, tmpfile, tmpnam

# vim: tabstop=4 expandtab shiftwidth=4
