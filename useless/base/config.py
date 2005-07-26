from ConfigParser import SafeConfigParser, NoSectionError
from ConfigParser import ConfigParser
import os, os.path

from useless.base import Error



def list_rcfiles(rcfilename):
    rcfiles = [os.path.join('/etc', rcfilename),
               os.path.expanduser('~/.'+rcfilename)]
    return rcfiles


class Configure(SafeConfigParser):
    def __init__(self, files=[]):
        SafeConfigParser.__init__(self)
        self.read(files)

    #default config files are case sensitive
    def optionxform(self, optionstr):
        return optionstr


class ConfigurationNew(ConfigParser):
    """Configuration has the ablity to have a current section,
    and be used as a dictionary.  If there is no current
    section, DEFAULT is used.
    """
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
        
    def items(self):
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
        
    def get_dsn(self):
        """returns information needed to connect to database"""
        return self.get_subdict(['dbname', 'dbhost', 'dbusername',
                                 'dbpassword', 'autocommit'])
    
    def has_key(self, option):
        section = self.section
        if section is None:
            section = 'DEFAULT'
        return self.__cfg__.has_option(section, option)
        
    def sections(self, filter=None):
        sections = ConfigParser.sections(self)
        if filter is not None:
            return [s for s in sections if filter(s)]
        else:
            return sections

    def get_list(self, option, section=None, delim=','):
        """This method is useful for getting a comma separated
        list of values from a config option.
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

    def is_it_true(self, section, option):
        """Simple true/false yes/no parsing."""
        truelist = ['true', 'True', 'TRUE', 'yes', 'Yes', 'YES', 't', 'T', 'y', 'Y'] 
        return self.get(section, option) in truelist

    def is_it_false(self, section, option):
        """Simple true/false yes/no parsing."""
        falselist = ['false', 'False', 'FALSE', 'no', 'No', 'NO', 'f', 'F', 'n', 'N']
        return self.get(section, option) in falselist
    
class ConfigurationOrig(object):
    """Configuration has the ablity to have a current section,
    and be used as a dictionary.  If there is no current
    section, DEFAULT is used.
    """
    def __init__(self, section=None, files=[]):
        if not files:
            raise Error, 'need a list of files'
        object.__init__(self)
        self.__cfg__ = Configure(files=files)
        self.change(section)

    def read(self, files):
        if type(files) is str:
            self.__cfg__.read([files])
        elif type(files) is file:
            self.__cfg__.readfp(files)
        elif type(files) is list:
            self.__cfg__.read(files)

    def __getitem__(self, key):
        if self.section is None:
            return self.__cfg__.defaults()[key]
        else:
            return self.__cfg__.get(self.section, key)

    def keys(self):
        if self.section is None:
            return self.__cfg__.defaults().keys()
        else:
            return self.__cfg__.options(self.section)
        
    def items(self):
        return [(k, self[k]) for k in self.keys()]

    def values(self):
        return [self[k] for k in self.keys()]

    def write(self, path):
        f = file(path, 'w')
        self.__cfg__.write(f)
        f.close()

    def change(self, section):
        """This changes the current section."""
        if self.__cfg__.has_section(section):
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
        
    def get_dsn(self):
        """returns information needed to connect to database"""
        return self.get_subdict(['dbname', 'dbhost', 'dbusername',
                                 'dbpassword', 'autocommit'])
    
    def get(self, section, name):
        return self.__cfg__.get(section, name)

    def has_section(self, section):
        return self.__cfg__.has_section(section)

    def has_option(self, section, option):
        return self.__cfg__.has_option(section, option)

    def has_key(self, option):
        section = self.section
        if section is None:
            section = 'DEFAULT'
        return self.__cfg__.has_option(section, option)
        
    
    def set(self, section, option, value):
        self.__cfg__.set(section, option, value)

    def add_section(self, section):
        self.__cfg__.add_section(section)

    def sections(self, filter=None):
        sections = self.__cfg__.sections()
        if filter is not None:
            return [s for s in sections if filter(s)]
        else:
            return sections

    def get_list(self, option, section=None, delim=','):
        """This method is useful for getting a comma separated
        list of values from a config option.
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

    def is_it_true(self, section, option):
        """Simple true/false yes/no parsing."""
        truelist = ['true', 'True', 'TRUE', 'yes', 'Yes', 'YES', 't', 'T', 'y', 'Y'] 
        return self.get(section, option) in truelist

    def is_it_false(self, section, option):
        """Simple true/false yes/no parsing."""
        falselist = ['false', 'False', 'FALSE', 'no', 'No', 'NO', 'f', 'F', 'n', 'N']
        return self.get(section, option) in falselist
    
Configuration = ConfigurationNew        
if __name__ == '__main__':
    cfg = Configuration()
