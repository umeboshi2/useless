#!/usr/bin/env python
import os, sys

from useless.base.path import path


class LogRotator(object):
    def __init__(self, filename):
        self.count = 0
        self.orig_filename = path(filename)
        # set this to False to keep from
        # creating empty log file after rotation
        
        self.make_empty = True

    def _filename(self, sequence, filename=None):
        if filename is None:
            filename = self.orig_filename
        else:
            filename = path(filename)
        seqname = '%s.%d' % (filename, sequence)
        return path(seqname)
    
    def _find_next_sequence(self):
        count = 0
        while self._filename(count).exists():
            count += 1
        return count

    def _rotate(self):
        seq = self._find_next_sequence()
        indices = range(seq)
        indices.reverse()
        for number in indices:
            next_number = number + 1
            oldname = self._filename(number)
            newname = self._filename(next_number)
            os.rename(oldname, newname)
        os.rename(self.orig_filename, self._filename(0))
        
    def rotate(self):
        self._rotate()
        if self.make_empty:
            file(self.orig_filename, 'w')
            
            
    

if __name__ == "__main__":
    f = "logfile"
    l = LogRotator(f)    
