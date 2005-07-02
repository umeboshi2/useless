from qt import SIGNAL, SLOT, Qt
from qt import QSplitter

from kdeui import KMainWindow, KPopupMenu
from kdeui import KStdAction, KMessageBox
from kdeui import KListViewItem
from kdeui import KListView


from useless.kbase.actions import AddDbUser, AddDbGroup
from useless.kbase.actions import AddDbSchema
from useless.sqlgen.clause import Eq, In
from useless.sqlgen.admin import create_user, create_schema
from useless.kdb import schema as kschema
from useless.db.midlevel import StatementCursor
from useless.kbase.gui import SimpleRecordDialog

class AdminDb(object):
    def __init__(self, app):
        object.__init__(self)
        self.app = app
        self.db = app.db

    def create_user(self, name, passwd=None, createdb=False,
                    createuser=False, groups=None):
        stmt = create_user(name, passwd=passwd, createdb=createdb,
                          createuser=createuser, groups=groups)
        self.db.mcursor.execute(stmt)

    def create_group(self, name):
        stmt = 'create group %s' % name
        self.db.mcursor.execute(stmt)

    def get_users(self, group=None):
        clause = None
        if group is not None:
            clause = Eq('groname', group)
            row = self.db.select_row(fields=['grolist'], table='pg_group',
                                     clause=clause)
            #clause = In('usesysid', row.grolist)
            if row.grolist is None:
                clause = None
            else:
                clause = 'usesysid in %s' % row.grolist
        fields = ['usename', 'usesysid']
        return self.db.select(fields=fields, table='pg_user',
                              clause=clause)
    
    def get_groups(self):
        fields = ['groname as group', 'grosysid']
        return self.db.select(fields=fields, table='pg_group')
    
    def _altergroup(self, users, group, alter):
        u = ','.join(users)
        cmd = 'alter group %s %s user %s' % (group, u, alter)
        self.db.mcursor.execute(cmd)
        
    def adduser(self, users, group):
        self._altergroup(users, group, 'add')
        
    def deluser(self, users, group=None):
        if group is not None:
            self._altergroup(users, group, 'drop')
        else:
            cmd = 'drop user %s' % users[0]
            self.db.mcursor.execute(cmd)
            
    def create_schema(self, name):
        cmd = create_schema(name)
        self.db.mcursor.execute(cmd)
        self.db.conn.commit()
        
class AddUserDialog(SimpleRecordDialog):
    def __init__(self, parent, name='AddUserDialog'):
        fields = ['username']
        SimpleRecordDialog.__init__(self, parent, fields, name=name)
        
class AddGroupDialog(SimpleRecordDialog):
    def __init__(self, parent, name='AddGroupDialog'):
        fields = ['groupname']
        SimpleRecordDialog.__init__(self, parent, fields, name=name)

class AdminWidget(KMainWindow):
    def __init__(self, app, parent):
        KMainWindow.__init__(self, parent, 'AdminWidget')
        self.app = app
        self.db = app.db
        self.manager = AdminDb(self.app)
        self.mainView = QSplitter(self, 'main view')
        self.listView = KListView(self.mainView)
        self.groupView = KListView(self.mainView)
        self.setCentralWidget(self.mainView)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.initlistView()
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.dialogs = {}
        self.show()

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.adduserAction = AddDbUser(self.slotAddDbUser, collection)
        self.addgroupAction = AddDbGroup(self.slotAddDbGroup, collection)
        self.addschemaAction = AddDbSchema(self.slotAddDbSchema, collection)
        
    def initMenus(self):
        mainmenu = KPopupMenu(self)
        actions = [self.adduserAction, self.addgroupAction,
                   self.addschemaAction, self.quitAction]
        for action in actions:
            action.plug(mainmenu)
        self.menuBar().insertItem('&Main', mainmenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.adduserAction, self.addgroupAction,
                   self.addschemaAction, self.quitAction]
        for action in actions:
            action.plug(toolbar)

    def initlistView(self):
        self.listView.addColumn('grouping')
        self.listView.setRootIsDecorated(True)
        self.groupView.addColumn('user')
        self.groupView.setRootIsDecorated(True)
        self.refreshlistView()
        
    def refreshlistView(self):
        self.listView.clear()
        rows = self.manager.get_users()
        print rows
        print 'helo;'
        users = KListViewItem(self.listView, 'user')
        groups = KListViewItem(self.listView, 'group')
        for row in rows:
            c = KListViewItem(users, row.usename)
            c.userid = row.usesysid
        for row in self.manager.get_groups():
            c = KListViewItem(groups, row.group)
            c.grosysid = row.grosysid

    def refreshGroupView(self):
        pass
    
    def selectionChanged(self):
        current = self.listView.currentItem()
        print current
        if hasattr(current, 'userid'):
            print 'user is', current.userid, current.text(0)
        elif hasattr(current, 'grosysid'):
            group = str(current.text(0))
            rows = self.manager.get_users(group=group)
            self.groupView.clear()
            for row in rows:
                c = KListViewItem(self.groupView, row.usename)
                
        
    def slotAddDbGroup(self):
        dlg = AddGroupDialog(self)
        dlg.connect(dlg, SIGNAL('okClicked()'), self.addDbGroupok)
        self.dialogs['new-group'] = dlg
        

    def slotAddDbUser(self):
        dlg = AddUserDialog(self)
        dlg.connect(dlg, SIGNAL('okClicked()'), self.addDbUserok)
        self.dialogs['new-user'] = dlg

    def slotAddDbSchema(self):
        dlg = SimpleRecordDialog(self, ['schema'], 'AddDbSchemaDialog')
        dlg.connect(dlg, SIGNAL('okClicked()'), self.addDbSchemaok)
        self.dialogs['new-schema'] = dlg
        
    def addDbUserok(self):
        dlg = self.dialogs['new-user']
        usename = str(dlg.grid.entries['username'].text())
        self.manager.create_user(usename)
        self.db.conn.commit()
        self.refreshlistView()
        
    def addDbGroupok(self):
        dlg = self.dialogs['new-group']
        group = str(dlg.grid.entries['groupname'].text())
        self.manager.create_group(group)
        self.db.conn.commit()
        self.refreshlistView()
        
    def addDbSchemaok(self):
        dlg = self.dialogs['new-schema']
        schema = str(dlg.grid.entries['schema'].text())
        self.manager.create_schema(schema)
        cursor = StatementCursor(self.db.conn)
        cursor.execute('set SESSION search_path to %s' % schema)
        self.db.conn.commit()
        cursor.execute('show search_path')
        print cursor.fetchall()
        kschema.create_schema(cursor)
        self.refreshlistView()
        
        
