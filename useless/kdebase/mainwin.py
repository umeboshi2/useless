from qt import QSplitter
from qt import SIGNAL

from kdeui import KMainWindow
from kdeui import KListView
from kdeui import KStdAction
from kdeui import KPopupMenu

from base import get_application_pointer
from base import HasDialogs

from error import MethodNotImplementedError

# This is the base KMainWindow class for applications using useless.
# Includes self.app, and dialog handling members.
class BaseMainWindow(KMainWindow, HasDialogs):
    def __init__(self, parent, name='BaseMainWindow'):
        KMainWindow.__init__(self, parent, name)
        HasDialogs.__init__(self)
        self.app = get_application_pointer()

# This is a simple main window for applications
# Includes helpers to add actions, a menu and a toolbar
# This is very simple class
class SimpleMainWindow(BaseMainWindow):
    def __init__(self, parent, name='SimpleMainWindow'):
        BaseMainWindow.__init__(self, parent, name=name)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        
    # in subclass at end of initActions call
    # SimpleMainWindow.initActions(self, collection)
    # to automatically add the quitAction
    def initActions(self, collection=None):
        if collection is None:
            collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)

    # in subclass at end of initMenus call
    # SimpleMainWindow.initMenus(self, mainmenu)
    # to automatically plug the quitAction into the mainmenu
    # and create the help menu
    def initMenus(self, mainmenu=None):
        if mainmenu is None:
            mainmenu = KPopupMenu(self)
        self.quitAction.plug(mainmenu)
        self.menuBar().insertItem('&Main', mainmenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
    
    def initToolbar(self):
        raise MethodNotImplementedError(self, 'initToolbar not implemented in base class')

class BaseSplitWindow(BaseMainWindow):
    def __init__(self, parent, view, listview=None, name='BaseSplitWIndow'):
        BaseMainWindow.__init__(self, parent, name=name)
        self.splitter = QSplitter(self, 'mainView')
        if listview is None:
            self.listView = KListView(self.splitter)
        else:
            self.listView = listview(self.splitter)
        self.mainView = view(self.splitter)
        self.setCentralWidget(self.splitter)
        if hasattr(self, 'initlistView'):
            self.initlistView()
        elif hasattr(self.listView, 'initlistView'):
            self.listView.initlistView()
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)

class BaseViewWindow(BaseMainWindow):
    def __init__(self, parent, view, name='BaseViewWindow'):
        BaseMainWindow.__init__(self, parent, name)
        self.view = view(self)
        self.setCentralWidget(self.view)
        
