import os
import md5

class BaseSimpleAuthHandler(object):
    def __init__(self, dbfile):
        self.dbfile=dbfile
        if not os.path.isfile(self.dbfile):
            self._generate_database('admin', 'p22wd')
            
    def _generate_database(self, user, passwd):
        ud, pd = self._make_digests(user, passwd)
        pfile  = file(self.dbfile, 'wb')
        pfile.write(ud + pd)
        pfile.close()

    def _get_dbfile_digest(self):
        data = file(self.dbfile).read()
        size = 16
        udigest = data[:size]
        pdigest = data[size:]
        return udigest, pdigest

    def _make_digests(self, user, passwd):
        return [md5.new(k).digest() for k in [user, passwd]]
    
    def authenticate(self, user, passwd):
        ud, pd = self._make_digests(user, passwd)
        ud_real, pd_real = self._get_dbfile_digest()
        return (ud == ud_real) and (pd == pd_real)

    def change_login(self, user, passwd):
        self._generate_database(user, passwd)

# this function uses the mainconfig
# and doesn't belong here
def reroot_href_bad(href):
    #if hasattr(cherrypy, 'request'):
    #   headerMap = getattr(cherrypy, 'request')
    #   root = headerMap['CP-Location']
    root = mainconfig.get('global', 'base_url_dir')
    if href[0] == '/':
        href = os.path.join(root, href[1:])
    return href

# this function 'fixes' absolute hrefs to
# match the root location of the site
def reroot_href(href, root):
    while href[0] == '/':
        href = href[1:]
    return os.path.join(root, href)



