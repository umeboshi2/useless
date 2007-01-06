from qt import QSplitter, QPixmap, QGridLayout
from qt import QLabel, QFrame, QString
from qt import SIGNAL, SLOT, Qt
from qt import QMimeSourceFactory
from qt import QCheckBox
from qt import QVBoxLayout

from kdecore import KConfigDialogManager
from kdecore import KAboutData
from kdeui import KMainWindow, KEdit, KPushButton
from kdeui import KMessageBox, KAboutDialog
from kdeui import KConfigDialog, KListView
from kdeui import KDialogBase, KLineEdit
from kdeui import KTextBrowser, KPopupMenu
from kdeui import KStdAction
from kdeui import KTabWidget, KActionSelector
from kdeui import KComboBox

import warnings
warnings.warn("useless.kbase.gui shouldn't be used, it needs splitting",
              RuntimeWarning, stacklevel=2)

class MimeSources(QMimeSourceFactory):
    def __init__(self):
        QMimeSourceFactory.__init__(self)
        self.addFilePath('/usr/share/wallpapers')

class MainWindow(KMainWindow):
    def __init__(self, parent, name='MainWindow'):
        KMainWindow.__init__(self, parent, name)
        self.initActions()
        self.initMenus()
        if hasattr(self, 'initToolbar'):
            self.initToolbar()

    def initActions(self, collection=None):
        if collection is None:
            collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)

    def initMenus(self, mainmenu=None):
        if mainmenu is None:
            mainmenu = KPopupMenu(self)
        self.quitAction.plug(mainmenu)
        self.menuBar().insertItem('&Main', mainmenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
    
class SimpleRecord(QGridLayout):
    def __init__(self, parent, fields, text=None, record=None, name=None):
        print 'record, name', record, name
        if name is None:
            print 'I need a name', record
            raise Exception, 'name needed in SimpleRecord'
        QGridLayout.__init__(self, parent, len(fields) + 1, 2, 1, -1, name)
        self.fields = fields
        self.entries = {}
        #self._setupfields(parent)
        self.setSpacing(7)
        self.setMargin(10)
        self.record = record
        self._refbuttons = {}
        self._setupfields(parent)
        
    def _setupfields(self, parent, text=None):
        if text is None:
            text = '<b>insert a simple record</b>'
        for child in self.parent().children():
            print child
            #child.close()
        refdata = None
        if self.record is not None and hasattr(self.record, '_refdata'):
            print 'record is not None', self.record
            refdata = self.record._refdata
        for f in range(len(self.fields)):
            field = self.fields[f]
            print 'field is', field
            if refdata is not None and field in refdata.cols:
                button = KPushButton('select/create', parent)
                self._refbuttons[field] = button
                self.addWidget(button, f + 1, 1)
                label = QLabel(entry, field, parent, field)
                self.addWidget(label, f + 1, 0)
            else:
                entry = KLineEdit('', parent)
                if self.record is not None:
                    entry.setText(str(self.record[field]))
                self.entries[field] = entry
                self.addWidget(entry, f + 1, 1)
                label = QLabel(entry, field, parent, field)
                self.addWidget(label, f + 1, 0)
        self.addMultiCellWidget(QLabel(text, parent), 0, 0, 0, 1)

    def getRecordData(self):
        return dict([(k,str(v.text())) for k,v in self.entries.items()])

    def setRecordData(self, data):
        for k, v in data.items():
            self.entries[k].setText(v)

class SimpleRecordDialog(KDialogBase):
    def __init__(self, parent, fields, record=None, name='SimpleRecordDialog'):
        KDialogBase.__init__(self, parent, name)
        self.page = QFrame(self)
        self.setMainWidget(self.page)
        text = 'this is a <em>simple</em> record dialog'
        self.grid = SimpleRecord(self.page, fields, text,
                                 record=record,name=name)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.dialogs = {}
        self.refbuttons = self.grid._refbuttons
        self.show()

    def getRecordData(self):
        return self.grid.getRecordData()
    
    def setRecordData(self, data):
        self.grid.setRecordData(data)
        
class EditRecordDialog(SimpleRecordDialog):
    def __init__(self, parent, fields, record, name):
        SimpleRecordDialog.__init__(self, parent, fields, record=record, name=name)
        self.record = record
        if hasattr(record, '_refdata'):
            print 'record has refdata'
        self.setButtonOKText('update', 'update')
        
class ConfigureDialogorig(KConfigDialog):
    def __init__(self, parent, cfg, name='ConfigureDialog'):
        print 'repreper'
        #skel = DefaultSkeleton()
        skel = KonsultantConfig()
        print 'hwllo'
        #skel.readConfig()
        print skel
        KConfigDialog.__init__(self, parent, name, skel)
        #self.manager = KConfigDialogManager(self, skel, 'ConfigureDialogManager')

class ConfigLayout(QGridLayout):
    def __init__(self, parent):
        QGridLayout.__init__(self, parent)

class _SimpleConfigLayout(QGridLayout):
    def __init__(self, parent, cfg, group, keys):
        cfg.setGroup(group)
        QGridLayout.__init__(self, parent, len(keys), 2)
        self.entries = {}.fromkeys(keys)
        row = 0
        for k in keys:
            self.addWidget(QLabel(k, parent), row, 0)
            entry = KLineEdit(parent)
            self.addWidget(entry, row, 1)
            self.entries[k] = entry
            entry.setText(cfg.readEntry(k))
            row += 1

class DbConfigLayout(_SimpleConfigLayout):
    def __init__(self, parent, cfg):
        keys = ['dbhost', 'dbname', 'dbpass', 'dbport', 'dbuser']
        _SimpleConfigLayout.__init__(self, parent, cfg, 'database', keys)
    
class PgPoolConfigLayout(QGridLayout):
    def __init__(self, parent, cfg):
        cfg.setGroup('pgpool')
        keys = ['command', 'connection_life_time', 'max_pool', 'num_init_children',
                'port', 'usepgpool']
        QGridLayout.__init__(self, parent, len(keys), 2)
        self.entries = {}.fromkeys(keys)
        row = 0
        for k in keys[:-1]:
            self.addWidget(QLabel(k, parent), row, 0)
            entry = KLineEdit(parent)
            self.addWidget(entry, row, 1)
            self.entries[k] = entry
            row += 1
        self.addWidget(QLabel('usepgpool', parent), row, 0)
        entry = QCheckBox('usepgpool', parent)
        self.addWidget(entry, row, 1)
        self.entries['usepgpool'] = entry

class ConfigureDialog(KDialogBase):
    def __init__(self, app, parent):
        KDialogBase.__init__(self, parent, 'ConfigureDialog')
        self.app = app
        self.cfg = app.cfg
        self.page = KTabWidget(self)
        self.grouplist = ['database', 'pgpool']
        self.groups = {}
        frame = QFrame(self.page)
        self.groups['database'] = DbConfigLayout(frame, self.cfg)
        frame = QFrame(self.page)
        self.groups['pgpool'] = PgPoolConfigLayout(frame, self.cfg)
        
        
        for t in self.grouplist:
            self.page.addTab(self.groups[t].parent(), t)
        self.setMainWidget(self.page)
        self.show()

class VboxDialog(KDialogBase):
    def __init__(self, parent, name='VboxDialog'):
        KDialogBase.__init__(self, parent, name)
        self.page = QFrame(self)
        self.setMainWidget(self.page)
        self.vbox = QVBoxLayout(self.page, 5, 7)

class BaseAssigner(VboxDialog):
    def __init__(self, app, parent, name='BaseAssigner', udbuttons=False):
        VboxDialog.__init__(self, parent, name=name)
        self.listBox = KActionSelector(self.page)
        self.listBox.setShowUpDownButtons(udbuttons)
        self.vbox.addWidget(self.listBox)
        self.app = app
        self.initView()
        self.setModal(False)
        self.show()

    def initView(self):
        print 'you need to override initView'
        

class MyCombo(KComboBox):
    def fill(self, alist):
        self.clear()
        for item in alist:
            self.insertItem(item)
            

#############################
## from paella-kde need to remove

class SimpleSplitWindow(KMainWindow):
    def __init__(self, app, parent, view, name):
        KMainWindow.__init__(self, parent, name)
        self.app = app
        self.conn = app.conn
        self.mainView = QSplitter(self, 'mainView')
        self.listView = KListView(self.mainView)
        self.listView.setRootIsDecorated(True)
        self.view = view(self.app, self.mainView)
        self.setCentralWidget(self.mainView)
        if hasattr(self, 'initlistView'):
            self.initlistView()
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.show()

class ViewWindow(KMainWindow):
    def __init__(self, app, parent, view, name):
        KMainWindow.__init__(self, parent, name)
        self.app = app
        self.conn = app.conn
        self.view = view(self.app, self)
        self.setCentralWidget(self.view)
        self.show()
