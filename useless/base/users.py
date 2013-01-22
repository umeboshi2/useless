import os
import subprocess

# This is vulnerable to ps command as
# the plaintext password is present on
# the commandline for the yes command.
def set_plaintext_password(username, password):
    yes_cmd = ['yes', password]
    pass_cmd = ['passwd', username]
    yes_proc = subprocess.Popen(yes_cmd, stdout=subprocess.PIPE)
    pass_proc = subprocess.Popen(pass_cmd, stdin=yes_proc.stdout)
    pass_proc.wait()
    if pass_proc.returncode:
        msg = "process returned %d" % pass_proc.returncode
        raise RuntimeError, msg
    
def set_encrypted_password(username, password):
    cmd = ['usermod', '-p', password, username]
    subprocess.check_call(cmd)
    
def add_group(group, gid=None):
    cmd = ['addgroup']
    if gid is not None:
        cmd += ['--gid', str(int(gid))]
    cmd.append(group)
    subprocess.check_call(cmd)

def add_user(name, uid=None, gid=None, gecos=None, password=None,
             homedir=None, shell='/bin/bash'):
    cmd = ['adduser']
    opts = []
    if password is None:
        opts.append('--disabled-password')
    if uid is not None:
        opts += ['--uid', str(int(uid))]
    if gid is not None:
        opts += ['--gid', str(int(gid))]
    if gecos is None:
        gecos = '%s,,,' % name
    opts += ['--gecos', gecos]
    cmd = cmd + opts + [username]
    subprocess.check_call(cmd)
    if password is not None:
        set_plaintext_password(name, password)
        
    
    

    
