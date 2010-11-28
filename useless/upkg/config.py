from ConfigParser import ConfigParser

from useless.base.path import path

class UpkgConfig(ConfigParser):
    def write(self, fileobj):
        sections = self.sections()
        sections.sort()
        for section in sections:
            fileobj.write('[%s]\n' % section)
            options = self.options(section)
            options.sort()
            for opt in options:
                value = str(self.get(section, opt, raw=True)).replace('\n', '\n\t')
                fileobj.write('%s = %s\n' % (opt, value))
            fileobj.write('\n')
            
                            
