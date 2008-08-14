from qt import QFrame
from qt import QVBoxLayout
from qt import QLabel
from qt import SIGNAL

from kdecore import KApplication

from kdeui import KDialogBase
from kdeui import KActionSelector
from kdeui import KLineEdit

from frame import BaseRecordFrame

def get_application_pointer():
    return KApplication.kApplication()

class BaseDialogWindow(KDialogBase):
    'This object has an "app" attribute for the application'
    def __init__(self, parent, name='BaseDialogWindow'):
        KDialogBase.__init__(self, parent, name)
        self.app = get_application_pointer()
        
class VboxDialog(BaseDialogWindow):
    '''This dialog has a QFrame at self.frame and
    a QVBoxLayout at self.vbox'''
    def __init__(self, parent, name='VboxDialog'):
        BaseDialogWindow.__init__(self, parent, name=name)
        self.frame = QFrame(self)
        self.setMainWidget(self.frame)
        margin = 5
        spacing = 7
        self.vbox = QVBoxLayout(self.frame, margin, spacing)

class BaseAssigner(VboxDialog):
    '''This dialog has a KActionSelector at self.listBox'''
    def __init__(self, parent, name='BaseAssigner', udbuttons=False):
        VboxDialog.__init__(self, parent, name=name)
        self.listBox = KActionSelector(self.frame)
        self.listBox.setShowUpDownButtons(udbuttons)
        self.vbox.addWidget(self.listBox)
        self.initView()
        self.setModal(False)

    def initView(self):
        raise NotImplementedError, 'initView not implemented in base class'
    
class BaseRecordDialog(BaseDialogWindow):
    """This dialog has a BaseRecordFrame at self.frame.  It takes,
    as arguments, an ordered list of fields, and a dictionary containing
    at least those fields and it's values."""
    def __init__(self, parent, fields, record=None, name='BaseRecordDialog'):
        BaseDialogWindow.__init__(self, parent, name=name)
        text = 'This is a base record dialog.'
        self.frame = BaseRecordFrame(self, fields, text=text, record=record)
        self.showButtonApply(False)
        self.setButtonOKText('insert', 'insert')
        self.dialogs = {}
        self.refbuttons = self.frame._refbuttons
        self.setMainWidget(self.frame)
        
    def getRecordData(self):
        return self.frame.getRecordData()

    def setRecordData(self, data):
        self.frame.setRecordData(data)

class EditRecordDialog(BaseRecordDialog):
    def __init__(self, parent, fields, record, name):
        BaseRecordDialog.__init__(self, parent, fields, record=record, name=name)
        self.setButtonOKText('update', 'update')
        self.setText('Edit this record.')
        
class SimpleEntryDialog(VboxDialog):
    def __init__(self, parent, label="Enter Value", entry='', name='SimpleEntryDialog'):
        VboxDialog.__init__(self, parent, name=name)
        self.showButtonApply(False)
        self.label = QLabel(label, self.frame)
        self.entry = KLineEdit(self.frame, entry)
        self.vbox.setMargin(3)
        self.vbox.setSpacing(2)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.entry)
        self.connect(self, SIGNAL('okClicked()'), self.ok_clicked)
        
    def _get_entry(self):
        return str(self.entry.text())
    
    def ok_clicked(self):
        errmsg = "ok_clicked needs to be defined in subclass of SimpleEntryDialog"
        raise NotImplementedError, errmsg
    
