from kdeui import KMessageBox

from useless.base.util import excepthook_message

class MethodNotImplementedError(NotImplementedError):
    def __init__(self, parent, message):
        KMessageBox.error(parent, message)

def excepthook(type, value, tracebackobj):
    msg = excepthook_message(type, value, tracebackobj)
    KMessageBox.error(None, msg)
    
