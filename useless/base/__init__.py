import os
import logging
from logging.handlers import SysLogHandler

from useless import deprecated

def _Log(name, path=None, logformat=''):
    log = logging.getLogger(name)
    if path is not None:
	hdlr = logging.FileHandler(path)
    else:
	hdlr = SysLogHandler()
    if not logformat:
        logformat = '%(name)s - %(levelname)s: %(message)s'
    frmt = logging.Formatter(logformat)
    hdlr.setFormatter(frmt)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)
    return log

def Log(name, path, format=''):
    return _Log(name, path, logformat=format)

def SysLog(name):
    return _Log(name)

if os.environ.has_key('DEBUG'):
    syslog = SysLog('rename this to something else')


def debug(*something):
    if os.environ.has_key('DEBUG'):
	syslog.debug(' '.join(map(str, something)))

class BaseError(StandardError):
    pass

class Error(BaseError):
    def __init__(self, *args):
        deprecated('Use of Error class is now deprecated')
        BaseError.__init__(self, *args)
        
class AlreadyExistsError(BaseError):
    pass

class BaseLookupError(LookupError):
    pass

class NoExistError(BaseLookupError):
    pass

class NoFileError(NoExistError):
    pass

class UnbornError(NoExistError):
    pass


