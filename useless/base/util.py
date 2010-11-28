import os, sys
import traceback
from gzip import GzipFile
from StringIO import StringIO
from md5 import md5
import subprocess
import urlparse
import tempfile
import random

from pipes import Template as PipeTemplate
import pycurl

from useless.base import debug

from path import path

from defaults import BLOCK_SIZE, BYTE_UNITS
from defaults import PASSWDCHARS


class ShellError(OSError):
    pass

class strfile(StringIO):
    """I don't like the looks of StringIO and prefer
    a more pythonic type name.  Nothing special about
    this class.
    """
    def __init__(self, string=''):
        StringIO.__init__(self, string)

class Pkdictrows(dict):
    def __init__(self, rows, keyfield):
        dict.__init__(self, [(x[keyfield], x) for x in rows])


class Gpg(object):
    def __init__(self):
        self.directory = path(tempfile.mkdtemp('gpg'))
        self.keyring = self.directory / 'keyring'
        self.cmdbase = ['gpg', '--no-default-keyring', '--keyring', self.keyring]

    def __del__(self):
        self.directory.rmtree()
        
    def importkey(self, keydata):
        cmd = self.cmdbase + ['--import']
        prefix = 'gpg: key '
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        proc.stdin.write(keydata)
        proc.stdin.close()
        retval = proc.wait()
        lines = []
        errorlines = []
        for line in proc.stderr:
            errorlines.append(line)
            if line.startswith(prefix):
                lines.append(line)
        error = ''.join(errorlines)
        if len(lines) != 1:
            print "gpg returned an unexpected error:"
            print error
            raise RuntimeError, "gpg returned an unexpected error"
        if retval:
            raise RuntimeError, "gpg returned %d\n%s" % (retval, error)
        line = lines[0]
        keyid = line.split(prefix)[1].split(':')[0]
        return keyid
    
class Mount(dict):
    """A Mount is a very special dictionary that contains
    information about a line in /etc/fstab, it will be
    more valuable when it parses a line in the fstab file.
    """
    def __init__(self, device, mtpnt, fstype, opts, dump, pass_):
        dict.__init__(self, device=device, mtpnt=mtpnt, fstype=fstype,
                      opts=opts, dump=dump)
        self['pass'] = pass_

    def __repr__(self):
        fields = ['device', 'mtpnt', 'fstype', 'opts', 'dump', 'pass']
        values = [self[field] for field in fields]
        return 'Mount:  %s'  % ' '.join(values)

    def isnfs(self):
        return self['fstype'] == 'nfs'

    def istmpfs(self):
        return self['fstype'] == 'tmpfs'

    def isrootfs(self):
        return self['fstype'] == 'rootfs'

    def isproc(self):
        return self['fstype'] == 'proc'
    
class RefDict(dict):
    """This dictionary can reference other keys in
    it by having $key as a value.  For example,
    >>> from useless.base.util import RefDict
    >>> d = RefDict(foo='bar')
    >>> d['key1'] = '$foo'
    >>> d['key1']
    '$foo'
    >>> d.dereference('key1')
    'bar'
    >>>
    
    If the value needs to start with a '$',
    then it needs to be stored in the dictionary
    as $$foo, 
    >>> d = RefDict(key1='$$foo')
    >>> d['key1']
    '$$foo'
    >>> d.dereference('key1')
    '$foo'
    >>>

    This class was used in paella, but paella
    now uses it's template system for referring
    to other keys.  This class is probably obsolete
    at the moment.
    """
    def dereference(self, key):
        value = self[key]
        if value[0] == '$':
            key = value[1:]
            if key[0] == '$':
                return key
            else:
                return self.dereference(key)
        else:
            return value
        

def has_error(errorclass):
    clsname = errorclass.__name__
    def decorator(fun):
        setattr(fun, clsname, errorclass)
        return fun
    return decorator


@has_error(ShellError)
def shell(cmd):
    retval = subprocess.call(cmd, shell=True)
    if retval != 0:
        raise ShellError, '%s returned %d' % (cmd, retval)

def makepaths(*dirs):
    """This calls os.makedirs on all arguments.
    This function won't raise an exception on
    making an existing directory.
    """
    for adir in dirs:
        try:
            os.makedirs(adir)
        except OSError, inst:
            # expect the error 17, 'File exists'
            if inst.args[0] == 17:
                pass
            else:
                raise inst
            
def blank_values(count, value=None):
    """This is a simple generator that
    makes count amount of value.
    """
    for x in range(count):
        yield value

def blank_list(length, value=None):
    return list(blank_values(length, value))


def diff_dict(adict, bdict):
    diffdict = {}
    for key in adict.keys():
        diffdict[key] = bool(adict[key] == bdict[key])
    return diffdict

def apply2file(function, path, *args):
    """apply a function with arguements to a
    readable file at path.
    """
    f = file(path)
    result = function(f, *args)
    f.close()
    return result

def wget(url, directory='.'):
    """this will download a file with wget
    optionally into a path of your choosing,
    by default it's in the current directory.
    """
    here = path.getcwd()
    if directory.relpath() == '.':
        directory = here
    os.chdir(directory.dirname())
    cmd = ('wget', url)
    subprocess.call(cmd)
    os.chdir(here)

def md5sum(afile):
    """returns the standard md5sum hexdigest
    for a file object"""
    m = md5()
    block = afile.read(BLOCK_SIZE)
    while block:
        m.update(block)
        block = afile.read(BLOCK_SIZE)
    return m.hexdigest()

class _zipPipe(PipeTemplate):
    """This class, and it's subclasses,
    GzipPipe and BzipPipe will be deprecated
    in favor of using the subprocess module
    to handle piping.
    This class shouldn't be instantiated
    directly, but sublassed with a command
    that de/compresses from stdin to stdout.
    """
    def __init__(self, cmd, decompress):
        PipeTemplate.__init__(self)
        if decompress:
            cmd.append(' -d')
        self.append(cmd, '--')
        
class GzipPipe(_zipPipe):
    """This class will be deprecated
    in favor of using the subprocess module
    to handle piping."""
    def __init__(self, decompress=False):
        _zipPipe.__init__(self, 'gzip', decompress)

class BzipPipe(_zipPipe):
    """This class will be deprecated
    in favor of using the subprocess module
    to handle piping."""
    def __init__(self, decompress=False):
        _zipPipe.__init__(self, 'bzip2', decompress)
        
def gunzip(filename):
    cmd = ('gzip', '-cd', filename)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout

def bunzip(filename):
    cmd = ('bzip2', '-cd', filename)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout

def check_file(filename, md5_, quick=False):
    """This function will check a file with a
    given md5sum.  It can also be used to
    just check existence.
    """
    filename = path(filename)
    package = filename.basename()
    if filename.isfile():
        if not quick:
            debug('checking ', package)
            if md5sum(filename) == md5_:
                return 'ok'
            else:
                print package, md5_, md5sum(filename)
                return 'corrupt'
        else:
            return 'ok'
    else:
        return 'gone'

def get_file(rpath, lpath, result='gone'):
    """This function is really specific to
    mirroring debian and should be moved to
    a better spot.
    """
    rpath = path(rpath)
    lpath = path(lpath)
    
    dir, package = lpath.splitpath()
    if result == 'corrupt':
        while lpath.isfile():
            os.remove(lpath)
        wget(rpath, lpath)
        print lpath, ' was corrupt, got it'
    else:
        print package, ' not there'
        makepaths(dir)
        wget(rpath, lpath)


def ujoin(*args):
    """I think that this function name
    looks a little better and makes the code
    look a little better.
    """
    return '_'.join(args)

def oneliner(path, line):
    """This function is fairly useless so it
    will stay.
    """
    f = file(path, 'w')
    f.write(line + '\n')
    f.close()
    

def export_vars(out, variables):
    """This function is used for writing
    export lines to a shell script.
    """
    lines = ['export %s=%s\n' %(k,v) for k,v in variables.items()]
    out.write(lines)
    
def parse_vars(filename):
    f = file(filename)
    lines = [x.strip() for x in f.readlines()]
    items = [(x[0],x[1].strip()) for x in lines if x and x[0] !='#']
    return dict(items)

def parse_vars_eq(filename):
    f = file(filename)
    lines = [x.strip() for x in f.readlines()]
    items = [x.split('=') for x in lines if x and x[0] !='#']
    return dict(items)

def writefile(filename, string):
    """this funcion will quickly write a
    string to a path.
    """
    f = file(filename, 'w')
    f.write(string)
    f.close()

def readfile(filename):
    """this function will quickly read
    a filname and return a string of
    its contents.
    """
    f = file(filename)
    s = f.read()
    f.close()
    return s

def get_url(url):
    """This function uses pycurl to
    get the contents of a url and
    return it as a strfile.
    """
    string = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, string.write)
    c.setopt(c.MAXREDIRS, 5)
    c.perform()
    c.close()
    string.seek(0)
    return string

def filecopy(afile, filename):
    """Simple copy of a fileobject to a path
    """
    newfile = file(filename, 'w')
    if afile.tell() != 0:
        afile.seek(0)
    block = afile.read(1024)
    while block:
        newfile.write(block)
        block = afile.read(1024)
    newfile.close()

def backuptree(directory, backup):
    """This function takes two directory arguements.
    The backup directory is not required to exist,
    but needs to be on the same device as the first
    arguement.  It uses hard links to backup the files
    in the directory.  It doesn't handle symbolic links.
    """
    input, output = os.popen2('find %s -type d' %directory)
    dir = output.readline().strip()
    while dir:
        makepaths(join(backup, dir))
        dir = output.readline().strip()
    input, output = os.popen2('find %s -type f' %directory)
    file = output.readline().strip()
    while file:
        os.link(file, join(backup, file))
        file = output.readline().strip()
        
def has_extension(filename, extension, dot=True):
    """This function can test if a filename is a
    .bz2 or whatever.
    """
    if extension[0] != '.' and dot:
        extension = '.' + extension
    return filename[-len(extension):] == extension

def indexed_items(items):
    """This should be a generally useless function."""
    return dict([(v[0], k) for k,v in enumerate(items)])

def get_sub_path(fullpath, rootpath):
    if fullpath[:len(rootpath)] != rootpath:
        raise RuntimeError, 'fullpath not in rootpath\n%s\n%s' %(fullpath, rootpath)
    if rootpath[-1] != '/':
        rootpath += '/'
    tpath = fullpath.split(rootpath)[1]
    return tpath

def parse_proc_cmdline():
    """This function returns a dictionary of the arguements
    of the kernel commandline in /proc/cmdline.
    """
    _opts = file('/proc/cmdline').read().strip().split()
    return dict([o.split('=') for o in _opts if o.find('=') >= 0])

def parse_proc_mounts():
    """This returns a list of special Mount dictionaries
    about the mounts in /proc/mounts.
    """
    mounts = [Mount(*x.strip().split()) for x in file('/proc/mounts').readlines()]
    return mounts

def ismounted(mtpnt):
    """Simple test of parsing /proc/mounts and
    seeing if mtpnt is mounted.
    """
    mounts = parse_proc_mounts()
    mounted = False
    for m in mounts:
        if m['mtpnt'] == mtpnt:
            mounted = True
    return mounted

def runlog(command, destroylog=False,
           keeprunning=False, logvar='LOGFILE'):
    """This function will run a command and write all
    output to a logfile.  This function is likely
    to be deprecated.  It was only called from paella,
    and now paella has it's own runlog function.
    """
    from useless import deprecated
    deprecated("runlog is deprecated")
    logfile = os.environ[logvar]
    if isfile(logfile) and destroylog:
        os.remove(logfile)
    sysstream = dict(in_=sys.stdin, out=sys.stdout, err=sys.stderr)
    newstream = dict(in_=file('/dev/null'),
                     out=file(logfile, 'a'),
                     err=file(logfile, 'a+', 0))
    backup = {}
    for stream  in sysstream:
        backup[stream] = [os.dup(sysstream[stream].fileno()),
                          sysstream[stream].fileno()]
    for stream  in sysstream:
        os.dup2(newstream[stream].fileno(), backup[stream][1])
    
    run = os.system(command)
    
    if run and not keeprunning:
        raise RuntimeError, 'error in command %s , check %s' % (command, logfile)
    for stream in sysstream:
        os.dup2(backup[stream][0], backup[stream][1])
    for stream in newstream:
        newstream[stream].close()
    for stream in backup:
        os.close(backup[stream][0])
    return run

def runlog_script(command, destroylog=False,
           keeprunning=False, logvar='LOGFILE'):
    """This function will run a command and write all
    output to a logfile.  This function makes an os.system
    call to script
    """
    scriptcmd = 'script -a -f'
    if destroylog:
        print 'ignoring destroylog'
    logfile = os.environ[logvar]
    cmd  = '%s -c "%s" %s' % (scriptcmd, command, logfile)
    #cmd = [scriptcmd, '-c', command, logfile]
    run = os.system(cmd)
    #run = subprocess.call(cmd)
    if run and not keeprunning:
        raise RuntimeError, 'error in command %s , check %s' % (command, logfile)
    return run

def echo(message, logvar='LOGFILE'):
    """echo a quick message into the log."""
    runlog('echo %s' % message, logvar=logvar)
    
def str2list(data, delim=','):
    """separates a comma joined list of terms."""
    return [x.strip() for x in data.split(delim)]

def traceback_to_string(tracebackobj):
    tbinfofile = strfile()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    return tbinfo

def excepthook_message(type, value, tracebackobj):
    tbinfo = traceback_to_string(tracebackobj)
    separator = '-' * 80
    sections = [str(type), str(value), separator, tbinfo, separator]
    msg = '\n'.join(sections)
    return msg

class Url(str):
    """This class is useful for parsing and unparsing
    urls, and having attribute access to a parsed url.
    attributes are protocol, host, path, parameters, query, and frag_id.
    """
    
    def __init__(self, url=''):
        str.__init__(self, str(url))
        self.url_orig = url
        self.seturl(url)
        
    def seturl(self, url):
        """Uses urlparse to set the attributes for url"""
        url = str(url)
        protocol, host, path_, parameters, query, frag_id = urlparse.urlparse(url)
        self.protocol = protocol
        self.host = host
        self.path = path(path_)
        self.parameters = parameters
        self.query = query
        self.frag_id = frag_id

    def astuple(self):
        """return url as tuple from urlparse"""
        return (self.protocol, self.host, self.path, self.parameters,
                self.query, self.frag_id)

    def asdict(self):
        """return url as a dictionary where the url attributes are keys"""
        return dict(protocol=self.protocol, host=self.host, path=self.path,
                    parameters=self.parameters, query=self.query, frag_id=self.frag_id)

    def set_path(self, path_):
        """Method for setting the path attribute, and coercing it to be
        a path instance."""
        if not isinstance(path_, path):
            path_ = path(path_)            
        self.path = path_
        
    def output(self):
        return str(urlparse.urlunparse(self.astuple()))

    def __repr__(self):
        return 'Url(%s)' % self.output()

    def __str__(self):
        return self.output()

    def __eq__(self, other):
        return other.__eq__(self.output())
    

def format_bytes(bytes, format='%2.1f', split=True):
    power = 0
    block = 1024
    while bytes > block:
        bytes /= float(block)
        power += 1
    value = format % bytes
    unit = BYTE_UNITS[power]
    if split:
        return value, unit
    else:
        return '%s %s' % (value, unit)

def make_random_passwd(length=8, choices=None):
    "make random passwords"
    if choices is None:
        choices = PASSWDCHARS
    myrange = range(length + 1)
    passwd = ''
    while myrange.pop():
        passwd += random.choice(choices)
    return passwd

def make_debian_passwd(plaintext=None, salt=None):
    """This will make a password suitable for debian login.
    This will only work if you are using the default md5
    passwords.  The choices for the salt may not be correct.
    If this function is called without arguments, a random
    password will be generated, and the plaintext will be
    returned, along with the encrypted password.  Passing
    a plaintext argument will just return the encrypted
    password.
    """
    return_plaintext = False
    if plaintext is None:
        plaintext = make_random_passwd()
        return_plaintext = True
    # it's possible that '$' should be added
    # to salt_choices, but I'm not really sure.
    # The reason that we don't already have
    # The extra characters in the PASSWDCHARS,
    # is because we don't want users to have to
    # remember and use the funny characters (the
    # random string of alpanumeric characters is
    # hard enough).
    salt_choices = PASSWDCHARS + './'
    if salt is None:
        salt = make_random_passwd(choices=salt_choices)
    cmd = ['mkpasswd', '--salt=%s' % salt, '--method=md5',
           '--stdin']
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.stdin.write('%s\n' % plaintext)
    retval = proc.wait()
    if retval:
        raise RuntimeError , 'mkpasswd returned %d' % retval
    passwd = proc.stdout.read()
    # strip the newline from the end
    passwd = passwd.strip()
    if return_plaintext:
        return plaintext, passwd
    else:
        return passwd


def pipeline(*commands, **kw):
    orig_stdout = None
    if 'stdout' in kw:
        orig_stdout = kw['stdout']
    kw['stdout'] = subprocess.PIPE
    # link all commands together except the last one
    for command in commands[:-1]:
        proc = subprocess.Popen(command, **kw)
        # do this after to keep the stdin of the first command
        # and link stdout of the next command to stdin of the previous
        kw['stdin'] = proc.stdout

    # restore original stdout
    kw['stdout'] = orig_stdout
    last_command = commands[-1]
    last_proc = subprocess.Popen(last_command, **kw)
    return last_proc

    
if __name__ == '__main__':
    print 'hello'
    
