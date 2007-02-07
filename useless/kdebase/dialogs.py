from qt import QFrame
from qt import QVBoxLayout

from kdeui import KDialogBase
from kdeui import KActionSelector

from frame import BaseRecordFrame

class VboxDialog(KDialogBase):
    def __init__(self, parent, name='VboxDialog'):
        KDialogBase.__init__(self, parent, name)
        self.frame = QFrame(self)
        self.setMainWidget(self.frame)
        margin = 5
        spacing = 7
        self.vbox = QVBoxLayout(self.frame, margin, spacing)

class BaseAssigner(VboxDialog):
    def __init__(self, parent, name='BaseAssigner', udbuttons=False):
        VboxDialog.__init__(self, parent, name=name)
        self.listBox = KActionSelector(self.frame)
        self.listBox.setShowUpDownButtons(udbuttons)
        self.vbox.addWidget(self.listBox)
        self.initView()
        self.setModal(False)

    def initView(self):
        raise NotImplementedError, 'initView not implemented in base class'
    
class BaseRecordDialog(KDialogBase):
    def __init__(self, parent, fields, record=None, name='BaseRecordDialog'):
        KDialogBase.__init__(self, parent, name)
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
        
