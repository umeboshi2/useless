from qt import QSplitter
from qt import SIGNAL

from kdeui import KListView

class BaseManagerWidget(QSplitter):
    """I use the listbox on the left and textbrowser on the right an awful lot."""
    def __init__(self, parent, mainview, listview=None, name='BaseManagerWidget'):
        QSplitter.__init__(self, parent, name)
        if listview is None:
            self.listView = KListView(self)
        else:
            self.listView = listView(self)
        self.mainView = mainview(self)
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)

    def selectionChanged(self):
        msg = 'BaseManagerWidget.selectionChanged implement in subclass'
        raise NotImplementedError, msg
    
