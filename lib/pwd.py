#!/usr/bin/env python

class struct_passwd:

    def __init__(self, pw_dir, pw_gecos, pw_gid, pw_name, pw_passwd, pw_shell, pw_uid):
        self.pw_dir = pw_dir
        self.pw_gecos = pw_gecos
        self.pw_gid = pw_gid
        self.pw_name = pw_name
        self.pw_passwd = pw_passwd
        self.pw_shell = pw_shell
        self.pw_uid = pw_uid

    n_fields = 7
    n_sequence_fields = 7
    n_unnamed_fields = 0
    
def getpwall(): pass
def getpwnam(name): pass
def getpwuid(uid): pass

# vim: tabstop=4 expandtab shiftwidth=4
