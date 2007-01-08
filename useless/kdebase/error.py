from kdeui import KMessageBox

class MethodNotImplementedError(NotImplementedError):
    def __init__(self, parent, message):
        KMessageBox.error(parent, message)
