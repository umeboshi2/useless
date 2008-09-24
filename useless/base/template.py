import os
import re

from defaults import DELIMITERS

re_atts = ['match', 'search', 'split', 'findall',
           'finditer', 'sub', 'subn', 'flags', 'groupindex',
           'pattern']

class Tag(object):
    def __init__(self, delimiters=DELIMITERS['out-arrows']):
        object.__init__(self)
        left, right = map(re.escape, delimiters)
        pattern = '%s[\w_:]+%s' % (left, right)
        self.re_object = re.compile(pattern)

    def __getattr__(self, name, *args):
        if name in re_atts:
            return getattr(self.re_object, name, *args)


class Template(dict):
    def __init__(self, data={}):
        dict.__init__(data)
        self.delimiters = DELIMITERS['out-arrows']
        self.template = ''
        self.tag = Tag(self.delimiters)
        
    def _strip_tag_(self, tag):
        left, right = self.delimiters
        return tag.split(left)[1].split(right)[0]

    def _replace_function_(self, match):
        left, right = match.span()
        key = self._strip_tag_(self.template[left:right])
        #print 'key is', key
        #return self.dereference(key)
        return self[key]

    def dereference(self, key):
        raise RuntimeError, 'Template.dereference should not be called anymore.'
        print 'in dereference, keys', self.keys()
        value = self[key]
        if value[0] == '$':
            key = value[1:]
            if key[0] == '$':
                return key
            else:
                return self.dereference(key)
        else:
            return value
        

    def set_template(self, template):
        self.template = template

    def sub(self):
        orig = self.template
        sub = self.tag.sub(self._replace_function_, self.template)
        count = 0
        #print 'sub', count +1, sub
        self.template = sub
        sub = self.tag.sub(self._replace_function_, self.template)
        while sub != self.template:
            self.template = sub
            sub = self.tag.sub(self._replace_function_, self.template)
            count += 1
            #print '%d extra subs' % count
        self.template = orig
        return sub
                
    def spans(self):
        matches = self.tag.finditer(self.template)
        return [match.span() for match in matches]


if __name__ == '__main__':
    t = Template()
    t['foo'] = 'bar'
    t['bar'] = '$foo'
    
if False:
    t = Template()
    f = file('updatedb.conf.template')
    s = f.read()
    t.set_template(s)
    data = {}
    data['required_updatedb_prunefs'] = 'prunerr'
    data['required_updatedb_prunepaths'] = 'prunepatrffs'
    data['required_updatedb_netpaths'] = 'nett paffs'
    #t.set_data(data)
    t.update(data)
    
