from dcopext import DCOPObj

from base import get_application_pointer

# dcop parameter is application.dcopClient()
def kaffeine(dcop):
    iface = DCOPObj('kaffeine', dcop, 'KaffeineIface')


class Kaffeine(object):
    def __init__(self):
        self.app = get_application_pointer()
        self.dcop = self.app.dcopClient()
        self.iface = DCOPObj('kaffeine', self.dcop, 'KaffeineIface')

    def __getattr__(self, attr):
        return getattr(self.iface, attr)

    
