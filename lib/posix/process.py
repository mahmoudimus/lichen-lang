#!/usr/bin/env python

def abort(): pass
def chroot(path): pass
def ctermid(): pass
def execv(path, args): pass
def execve(path, args, env): pass
def fork(): pass
def forkpty(): pass
def getcwd(): pass
def getcwdu(): pass
def getegid(): pass
def geteuid(): pass
def getgid(): pass
def getgroups(): pass
def getloadavg(): pass
def getlogin(): pass
def getpgid(pid): pass
def getpgrp(): pass
def getpid(): pass
def getppid(): pass
def getresgid(): pass
def getresuid(): pass
def getsid(pid): pass
def getuid(): pass
def initgroups(username, gid): pass
def kill(pid, sig): pass
def killpg(pgid, sig): pass
def nice(inc): pass
def popen(command, mode='r', bufsize=None): pass
def setegid(gid): pass
def seteuid(uid): pass
def setgid(gid): pass
def setgroups(list): pass
def setpgid(pid, pgrp): pass
def setpgrp(): pass
def setregid(rgid, egid): pass
def setresgid(rgid, egid, sgid): pass
def setresuid(ruid, euid, suid): pass
def setreuid(ruid, euid): pass
def setsid(): pass
def setuid(uid): pass
def system(command): pass
def tcgetpgrp(fd): pass
def tcsetpgrp(fd, pgid): pass
def wait(): pass
def wait3(options): pass
def wait4(pid, options): pass
def waitpid(pid, options): pass

def WCOREDUMP(status): pass
def WEXITSTATUS(status): pass
def WIFCONTINUED(status): pass
def WIFEXITED(status): pass
def WIFSIGNALED(status): pass
def WIFSTOPPED(status): pass
def WSTOPSIG(status): pass
def WTERMSIG(status): pass

EX_CANTCREAT = 73
EX_CONFIG = 78
EX_DATAERR = 65
EX_IOERR = 74
EX_NOHOST = 68
EX_NOINPUT = 66
EX_NOPERM = 77
EX_NOUSER = 67
EX_OK = 0
EX_OSERR = 71
EX_OSFILE = 72
EX_PROTOCOL = 76
EX_SOFTWARE = 70
EX_TEMPFAIL = 75
EX_UNAVAILABLE = 69
EX_USAGE = 64

NGROUPS_MAX = 65536

P_WAIT = 0
P_NOWAIT = P_NOWAITO = 1

WCONTINUED = 8
WNOHANG = 1
WUNTRACED = 2

# vim: tabstop=4 expandtab shiftwidth=4
