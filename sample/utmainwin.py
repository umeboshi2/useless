from qt import SIGNAL, PYSIGNAL
from qt import QSplitter

from kdeui import KMainWindow
from kdeui import KListView, KListViewItem
from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu

from utbase import get_application_pointer
from utinfo import InfoPart

from utdialogs import BaseGuestDialog

class MainWindow(KMainWindow):
    def __init__(self, parent):
        KMainWindow.__init__(self, parent, 'Uncover Truth Frontend')
        self.app = get_application_pointer()
        self.splitView = QSplitter(self, 'splitView')
        self.listView = KListView(self.splitView, 'guests_view')
        self.textView = InfoPart(self.splitView)
        self.initlistView()

        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.connect(self.textView,
                     PYSIGNAL('GuestInfoUpdated'), self.refreshDisplay)
        self.setCentralWidget(self.splitView)

        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newGuestAction = KStdAction.openNew(self.slotNewGuest, collection)

        mainmenu = KPopupMenu(self)
        self.newGuestAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)

        toolbar = self.toolBar()
        self.newGuestAction.plug(toolbar)
        self.quitAction.plug(toolbar)
        
        self.new_guest_dialog = None

        # resize window
        self.resize(400, 500)
        self.splitView.setSizes([75, 325])
        

    def initlistView(self):
        self.listView.addColumn('guests', -1)
        self.refreshListView()

    def refreshListView(self):
        self.listView.clear()
        cursor = self.app.conn.stmtcursor()
        rows = self.app.guests.get_guest_rows()
        for row in rows:
            name = '%s %s' % (row.firstname, row.lastname)
            item = KListViewItem(self.listView, name)
            item.guestid = row['guestid']
            
    
    def slotNewGuest(self):
        win = BaseGuestDialog(self)
        self.connect(win, SIGNAL('okClicked()'),
                     self._new_guest_added)
        self.new_guest_dialog = win
        win.show()
    
    def _new_guest_added(self):
        dlg = self.new_guest_dialog
        if dlg is not None:
            data = dlg.get_guest_data()
            self.app.guests.insert_guest_data(data)
            self.refreshListView()
            self.new_guest_dialog = None
            
    def selectionChanged(self):
        item = self.listView.currentItem()
        guestid = item.guestid
        self.textView.set_guest_info(item.guestid)

    def refreshDisplay(self):
        #KMessageBox.error(self, 'ack refreshDisplay called')
        #self.refreshListView()
        self.selectionChanged()
        
        
