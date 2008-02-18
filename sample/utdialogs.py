from qt import SIGNAL, SLOT, PYSIGNAL
from qt import QFrame
from qt import QLabel, QGridLayout

from kdeui import KLineEdit, KTextEdit
from kdeui import KDialogBase
from kdeui import KPushButton
from kdeui import KStdGuiItem

from utbase import get_application_pointer

class BaseDialogWindow(KDialogBase):
    def __init__(self, parent, name='BaseDialogWindow'):
        KDialogBase.__init__(self, parent, name)
        self.app = get_application_pointer()

class BaseWorksEntryFrame(QFrame):
    def __init__(self, parent, name='BaseWorksEntryFrame'):
        QFrame.__init__(self, parent, name)
        margin = 0
        space = 1
        self.grid = QGridLayout(self, 6, 1, margin, space)
        
        self.worktype_lbl = QLabel('Work Type', self)
        self.worktype_entry = KLineEdit('website', self)
        self.title_lbl = QLabel('Title', self)
        self.title_entry = KLineEdit('', self)
        self.url_lbl = QLabel('Url', self)
        self.url_entry = KLineEdit('', self)

        row = 0
        for widget in [self.worktype_lbl, self.worktype_entry,
                       self.title_lbl, self.title_entry,
                       self.url_lbl, self.url_entry]:
            self.grid.addWidget(widget, row, 0)
            row += 1
            
    def get_data(self):
        wtype = str(self.worktype_entry.text())
        title = str(self.title_entry.text())
        url = str(self.url_entry.text())
        return dict(title=title, url=url, type=wtype)

    def set_data(self, data):
        self.title_entry.setText(data['title'])
        self.url_entry.setText(data['url'])
        wtype = data['type']
        if wtype is None:
            wtype = 'website'
        self.worktype_entry.setText(wtype)
        
class BaseGuestAppearanceFrame(QFrame):
    def __init__(self, parent, name='BaseGuestAppearanceFrame'):
        QFrame.__init__(self, parent, name)
        margin = 0
        space = 1
        self.grid = QGridLayout(self, 4, 1, margin, space)
        self.appearance_lbl = QLabel('Appearance', self)
        self.appearance_url = KLineEdit('', self)
        row = 0
        for widget in [self.appearance_lbl, self.appearance_url]:
            self.grid.addWidget(widget, row, 0)
            row += 1

    def get_data(self):
        url = str(self.appearance_url.text())
        return dict(url=url)

    def set_data(self, data):
        self.appearance_url.setText(data['url'])
        

# ha ha picture frame :)
class BaseGuestPictureFrame(QFrame):
    def __init__(self, parent, name='BaseGuestPictureFrame'):
        QFrame.__init__(self, parent, name)
        margin = 0
        space = 1
        self.grid = QGridLayout(self, 2, 2, margin, space)
        self.picture_lbl = QLabel('Picture', self)
        self.picture_url = KLineEdit('', self)
        self.picture_btn = KPushButton(KStdGuiItem.Open(),
                                       'Browse for picture', self)

        self.grid.addMultiCellWidget(self.picture_lbl, 0, 0, 0, 1)
        self.grid.addWidget(self.picture_url, 0, 1)
        self.grid.addWidget(self.picture_btn, 1, 1)
        
    def get_data(self):
        url = str(self.appearance_url.text())
        return dict(url=url)

    def set_data(self, data):
        self.appearance_url.setText(data['url'])
        
        
class BaseGuestWorksFrame(QFrame):
    def __init__(self, parent, name='BaseGuestWorksFrame'):
        QFrame.__init__(self, parent, name)
        self.works_entries = []
        margin = 0
        space = 1
        self.grid = QGridLayout(self, 2, 6, margin, space)
        self.works_lbl = QLabel('Works', self)
        self.grid.addMultiCellWidget(self.works_lbl, 0, 0, 0, 4)
        self.add_works_btn = KPushButton('+', self, 'add_works_button')
        self.add_works_btn.connect(self.add_works_btn,
                                   SIGNAL('clicked()'),
                                   self.add_works_entries)
        self.grid.addWidget(self.add_works_btn, 0, 5)
        
    def add_works_entries(self):
        frame = BaseWorksEntryFrame(self)
        row = len(self.works_entries) + 1
        self.grid.addMultiCellWidget(frame, row, row, 0, -1)
        self.works_entries.append(frame)
        frame.show()
        
    
class BaseGuestDataFrame(QFrame):
    def __init__(self, parent, name='BaseGuestDataFrame'):
        QFrame.__init__(self, parent, name)
        self.guestid = None
        numrows = 2
        numcols = 2
        margin = 0
        space = 1
        self.grid = QGridLayout(self, numrows, numcols,
                                margin, space, 'BaseGuestDataLayout')
        self.app = get_application_pointer()


        self.fname_lbl = QLabel('First Name', self)
        self.fname_entry = KLineEdit('', self)

        self.grid.addWidget(self.fname_lbl, 0, 0)
        self.grid.addWidget(self.fname_entry, 1, 0)

        self.lname_lbl = QLabel('Last Name', self)
        self.lname_entry = KLineEdit('', self)

        self.grid.addWidget(self.lname_lbl, 0, 1)
        self.grid.addWidget(self.lname_entry, 1, 1)

        self.title_lbl = QLabel('Title', self)
        self.title_entry = KLineEdit('', self)

        self.grid.addMultiCellWidget(self.title_lbl, 2, 2, 0, 1)
        self.grid.addMultiCellWidget(self.title_entry, 3, 3, 0, 1)

        self.desc_lbl = QLabel('Description', self)
        self.desc_entry = KTextEdit(self, 'description_entry')

        self.grid.addMultiCellWidget(self.desc_lbl, 4, 4, 0, 1)
        self.grid.addMultiCellWidget(self.desc_entry, 5, 7, 0, 1)

        #self.works_frame = BaseGuestWorksFrame(self)
        #self.grid.addMultiCellWidget(self.works_frame, 8, 8, 0, 1)
        
        
    def get_guest_data(self):
        fname = str(self.fname_entry.text())
        lname = str(self.lname_entry.text())
        title = str(self.title_entry.text())
        desc = str(self.desc_entry.text())
        # take the newlines out for now
        # until the sqlgen is fixed to work with sqlite
        desc = desc.replace('\n', ' ')
        data = dict(firstname=fname, lastname=lname,
                    description=desc, title=title)
        if self.guestid is not None:
            data['guestid'] = self.guestid
        return data

    def set_guest_data(self, data):
        self.guestid = data['guestid']
        self.fname_entry.setText(data['firstname'])
        self.lname_entry.setText(data['lastname'])
        if data['title']:
            self.title_entry.setText(data['title'])
        if data['description']:
            desc = data['description']
            desc = self.app.guests.unescape_text(desc)
            self.desc_entry.setText(desc)
            
    
class BaseGuestDialog(BaseDialogWindow):
    def __init__(self, parent, name='BaseGuestDialog'):
        BaseDialogWindow.__init__(self, parent, name=name)
        self.frame = BaseGuestDataFrame(self)
        self.setMainWidget(self.frame)
        
    def get_guest_data(self):
        return self.frame.get_guest_data()

    def set_guest_data(self, data):
        self.frame.set_guest_data(data)


class BaseWorksDialog(BaseDialogWindow):
    def __init__(self, parent, name='BaseWorksDialog'):
        BaseDialogWindow.__init__(self, parent, name=name)
        self.frame = BaseWorksEntryFrame(self)
        self.setMainWidget(self.frame)
        

    def get_data(self):
        return self.frame.get_data()

    def set_data(self, data):
        self.frame.set_data(data)
        
class BaseGuestAppearanceDialog(BaseDialogWindow):
    def __init__(self, parent, name='BaseGuestAppearanceDialog'):
        BaseDialogWindow.__init__(self, parent, name=name)
        self.frame = BaseGuestAppearanceFrame(self)
        self.setMainWidget(self.frame)

    def get_data(self):
        return self.frame.get_data()

    def set_data(self, data):
        self.frame.set_data(data)
        
