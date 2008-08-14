import os
from ConfigParser import RawConfigParser as ConfigParser

from kdecore import KConfigBackEnd
from kdecore import KConfig, KConfigBase       
from kdecore import KSimpleConfig
from kdecore import KConfigSkeleton

class BaseConfig(KSimpleConfig):
    def __init__(self):
        KSimpleConfig.__init__(self, 'konsultantrc')
        skel = BaseSkel()
        data = skel.getdata()
        for section in skel.sections():
            self.setGroup(section)
            for opt in skel.options(section):
                if not self.hasKey(opt):
                    self.writeEntry(opt, data[section][opt])
        self.sync()

