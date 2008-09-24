from os.path import isfile, join, dirname
import shelve
from sets import Set
from threading import Thread
import csv
from Queue import Queue, Full, Empty

import pycurl

from useless.base.util import blank_list, ujoin
from useless.base.util import makepaths

def hide(string):
    return '__%s__' % string

class DbRowDescription(list):
    def __init__(self, keys):
        list.__init__(self, keys)

    def sort(self):
        pass



class DbBaseRow(object):
    def __init__(self, desc, row):
        object.__init__(self)
        self._keylist_ = desc
        self._vallist_ = row
        #print desc, row
        self.__datadict__ = dict(zip(self._keylist_, self._vallist_))
        
    def keys(self):
        return self._keylist_

    def values(self):
        return self._vallist_

    def items(self):
        return zip(self._keylist_, self._vallist_)

    def __getitem__(self, key):
        if key in self._keylist_:
            return self.__datadict__[key]
        elif isinstance(key, int):
            return self._vallist_[key]
        else:
            raise KeyError, 'item %s not found' % key

    def __getattr__(self, key):
        if key in self._keylist_:
            return self.__datadict__[key]
        else:
            return getattr(self, key)
        
    def __len__(self):
        return len(self._keylist_)

    def __repr__(self):
        return str(self._vallist_)

class _Empty(DbBaseRow):
    def __init__(self, desc):
        DbBaseRow.__init__(self, desc, blank_list(len(desc)))



class Parser(list):
    def __init__(self, path, field_sep='\t'):
        csvfile = file(path)
        parser = csv.reader(csvfile, field_sep=field_sep)
        rows = [parser.parse(line) for line in csvfile.readlines()]
        csvfile.close()
        self.fields = rows[0]
        for row in rows[1:]:
            if len(row):
                self.append(DbBaseRow(self.fields, row))


if __name__ == '__main__':
    pass

    
    
