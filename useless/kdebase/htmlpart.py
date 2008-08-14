from qt import QWidget

from kdecore import KURL
from khtml import KHTMLPart

from base import get_application_pointer
from base import HasDialogs

class BaseInfoPart(KHTMLPart, HasDialogs):
    """This is a KHTMLPart that has methods for handling dialogs.
    The parent for the dialogs is a QWidget at self.dialog_parent .
    There is also an application pointer at self.app .
    """
    def __init__(self, parent, name='BaseInfoPart'):
        KHTMLPart.__init__(self, parent, name)
        HasDialogs.__init__(self)
        self.app = get_application_pointer()
        self.dialog_parent = QWidget(self.parent(), 'dialog_parent')

    def _clearit(self):
        """deprecated helper method to clear the view"""
        import warnings
        warnings.warn("_clearit method is deprecated, use clear_view instead",
                      stacklevel=2)
        self.clear_view()

    def clear_view(self):
        """helper method to clear the view"""
        self.begin()
        self.write('')
        self.end()
        
    def urlSelected(self, url, button, state, target, args):
        """this protected slot should be implemented in a subclass
        it does nothing by default.
        """        
        pass

    def openURL(self, url):
        if not isinstance(url, KURL):
            url = KURL(url)
        return KHTMLPart.openURL(self, url)
        

    
    
