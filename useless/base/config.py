from ConfigParser import SafeConfigParser, NoSectionError
from ConfigParser import ConfigParser
import os, os.path

from useless import deprecated

def list_rcfiles(rcfilename):
    rcfiles = [os.path.join('/etc', rcfilename),
               os.path.expanduser('~/.'+rcfilename)]
    return rcfiles

_BOOLEAN_STATES = {}
_BOOLEAN_STATES.update({}.fromkeys(['1', 'yes', 'true', 'on', 'y', 't'], True))
_BOOLEAN_STATES.update({}.fromkeys(['0', 'no', 'false', 'off', 'n', 'f'], False))

class Configure(SafeConfigParser):
    def __init__(self, files=[]):
        SafeConfigParser.__init__(self)
        self.read(files)

    #default config files are case sensitive
    def optionxform(self, optionstr):
        return optionstr


class Configuration(ConfigParser):
    """Configuration has the ablity to have a current section,
    and be used as a dictionary.  If there is no current
    section, DEFAULT is used.
    """
    # need to add t, f, y, and n to _boolean_states
    #_boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
    #                   '0': False, 'no': False, 'false': False, 'off': False,
    #                   # adding single letter options
    #                   't' : True, 'y' : True,
    #                   'f' : False, 'n' : False}
    _boolean_states = _BOOLEAN_STATES
    def __init__(self, section=None, files=[]):
        ConfigParser.__init__(self)
        self.section = section
        if len(files):
            self.read(files)

    def read(self, files):
        if type(files) is str:
            ConfigParser.read(self, [files])
        elif type(files) is file:
            ConfigParser.readfp(self, files)
        elif type(files) is list:
            ConfigParser.read(self, files)

    def __getitem__(self, key):
        if self.section is None:
            return self.defaults()[key]
        else:
            return self.get(self.section, key)

    def keys(self):
        if self.section is None:
            return self.defaults().keys()
        else:
            return self.options(self.section)
        
    def items(self, section=None, raw=False):
        if section is not None:
            return ConfigParser.items(self, section)
        else:
            return [(k, self[k]) for k in self.keys()]

    def values(self):
        return [self[k] for k in self.keys()]

    def write(self, fileorpath):
        closeme = False
        if type(fileorpath) is str:
            f = file(path, 'w')
            closeme = True
        else:
            f  = fileorpath
        ConfigParser.write(self, f)
        if closeme:
            f.close()

    def change(self, section):
        """This changes the current section."""
        if self.has_section(section):
            self.section = section
        elif section in ['DEFAULT', '', None]:
            self.section = None
        else:
            raise NoSectionError
        
    def get_subdict(self, keys):
        """returns a dictionary based on the keys given"""
        data = {}
        for key in keys:
            data[key] = self[key]
        return data
        
    def get_dsn(self, fields=['dbname', 'dbhost', 'dbusername', 'dbpassword',
                              'autocommit']):
        """returns information needed to connect to database"""
        return self.get_subdict(fields)
    
    def has_key(self, option):
        section = self.section
        if section is None:
            section = 'DEFAULT'
        return self.has_option(section, option)
        
    def sections(self, filter=None):
        sections = ConfigParser.sections(self)
        if filter is not None:
            return [s for s in sections if filter(s)]
        else:
            return sections

    def get_list(self, option, section=None, delim=','):
        """This method is useful for getting a comma separated
        list of values from a config option.  Please note
        that the option comes before the section in the
        arguments.
        """
        if section is None:
            section = self.section
        if section is None:
            section = 'DEFAULT'
        vlist = [x.strip() for x in self.get(section, option).split(delim)]
        if len(vlist) == 1 and not vlist[0]:
            return []
        else:
            return vlist

    def getlist(self, section, option, delim=','):
        return self.get_list(option, section=section, delim=delim)
    
    def is_it_true(self, section, option):
        """Simple true/false yes/no parsing."""
        return self.getboolean(section, option)

    def is_it_false(self, section, option):
        """Simple true/false yes/no parsing."""
        return not self.getboolean(section, option)

    def clear_section(self, section):
        for option in self.options(section):
            self.remove_option(section, option)

    def clear_all(self):
        self.defaults().clear()
        for section in self.sections():
            self.clear_section(section)
            
# still being used in advancedpetcare
# remove this one that's fixed
class BaseMainConfig(Configuration):
    def __init__(self, files, environ_var='', cfgsection='configfiles'):
        if environ_var and environ_var in os.environ:
            files.append(os.environ[environ_var])
        Configuration.__init__(self, files=files)
        self._cfgsection = cfgsection

    def getConfig(self, configfile):
        return Configuration(files=[self.get(self._cfgsection, configfile)])
    

if __name__ == '__main__':
    cfg = Configuration()
