import os, sys
from os.path import isfile, isdir, join
from gzip import GzipFile
from StringIO import StringIO
from md5 import md5

from pipes import Template as PipeTemplate
import pycurl

from useless.base import debug, Error

from defaults import BLOCK_SIZE

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
    >>> """
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
        

    


def makepaths_orig(*paths):
    for path in paths:
        if not isdir(path):
            os.makedirs(path)

def makepaths(*paths):
    for path in paths:
        try:
            os.makedirs(path)
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

def wget(url, path='.'):
    """this will download a file with wget
    optionally into a path of your choosing,
    by default it's in the current directory.
    """
    here = os.getcwd()
    if path == '.':
        path = here
    os.chdir(os.path.dirname(path))
    cmd = 'wget %s' % url
    os.system(cmd)
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
    """This class shouldn't be instantiated
    directly, but sublassed with a command
    that de/compresses from stdin to stdout.
    """
    def __init__(self, cmd, decompress):
        PipeTemplate.__init__(self)
        if decompress:
            cmd.append(' -d')
        self.append(cmd, '--')
        
class GzipPipe(_zipPipe):
    def __init__(self, decompress=False):
        _zipPipe.__init__(self, 'gzip', decompress)

class BzipPipe(_zipPipe):
    def __init__(self, decompress=False):
        _zipPipe.__init__(self, 'bzip2', decompress)
        
def gunzip(path):
    return os.popen2('gzip -cd %s' %path)[1]

def bunzip(path):
    return os.popen2('bzip2 -cd %s' %path)[1]

def check_file(path, md5_, quick=False):
    """This function will check a file with a
    given md5sum.  It can also be used to
    just check existence.
    """
    package = os.path.basename(path)
    if isfile(path):
        if not quick:
            debug('checking ', package)
            if md5sum(path) == md5_:
                return 'ok'
            else:
                print package, md5_, md5sum(path)
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
    dir, package = os.path.split(lpath)
    if result == 'corrupt':
        while isfile(lpath):
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
    
def parse_vars(path):
    f = file(path)
    lines = [x.strip() for x in f.readlines()]
    items = [(x[0],x[1].strip()) for x in lines if x and x[0] !='#']
    return dict(items)

def parse_vars_eq(path):
    f = file(path)
    lines = [x.strip() for x in f.readlines()]
    items = [x.split('=') for x in lines if x and x[0] !='#']
    return dict(items)

def writefile(path, string):
    """this funcion will quickly write a
    string to a path.
    """
    f = file(path, 'w')
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

def filecopy(afile, path):
    """Simple copy of a fileobject to a path
    """
    newfile = file(path, 'w')
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
        raise Error, 'fullpath not in rootpath\n%s\n%s' %(fullpath, rootpath)
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
    output to a logfile.
    """
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
        raise Error, 'error in command %s , check %s' % (command, logfile)
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
    run = os.system(cmd)
    if run and not keeprunning:
        raise Error, 'error in command %s , check %s' % (command, logfile)
    return run

def echo(message, logvar='LOGFILE'):
    """echo a quick message into the log."""
    runlog('echo %s' % message, logvar=logvar)
    
def str2list(data, delim=','):
    """separates a comma joined list of terms."""
    return [x.strip() for x in data.split(delim)]

if __name__ == '__main__':
    print 'hello'
    
