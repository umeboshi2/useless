from qt import QFrame
from qt import QGridLayout
from qt import QLabel

from kdeui import KPushButton
from kdeui import KLineEdit

class BaseRecordFrame(QFrame):
    """This is a class that is good for dialog windows
    that display records.
    fields is an ordered list of fields
    the fields will be displayed in rows
    record can either be a dictionary
    or a database row (with dict access)
    """
    def __init__(self, parent, fields, text=None,
                 record=None, name='BaseRecordFrame'):
        QFrame.__init__(self, parent, name)
        numrows = len(fields) + 1
        numcols = 2
        margin = 10
        space = 7
        self.grid = QGridLayout(self, numrows, numcols,
                                margin, space, name)
        self.fields = fields
        self.entries = {}

        #self.grid.setSpacing(7)
        #self.grid.setMargin(10)

        self.record = record

        # need to explain refbuttons and refdata somewhere
        self._refbuttons = {}

        self._setup_fields(text)

    def _setup_fields(self, text):
        if text is None:
            text = '<b>insert a simple record</b>'
        refdata = None
        # check if the record has refdata
        if self.record is not None and hasattr(self.record, '_refdata'):
            refdata = self.record._refdata
        for field_index in range(len(self.fields)):
            field = self.fields[field_index]
            # here we make either a label or button
            if refdata is not None and field in refdata.cols:
                button = KPushButton('select/create', self)
                self._refbuttons[field] = button
                # add button to grid (column 1)
                self.grid.addWidget(button, field_index + 1, 1)
                # make buddy the button
                buddy = button
            else:
                record_value = ''
                if self.record is not None:
                    record_value = self.record[field]
                entry = KLineEdit(record_value, self)
                self.entries[field] = entry
                self.grid.addWidget(entry, field_index + 1, 1)
                # make buddy the entry
                buddy = entry
            # make the label
            lbl_text = '&%s' % field
            lbl_name = '%sLabel' % field
            # buddy may not be well defined, or appropriate here
            label = QLabel(buddy, lbl_text, self, lbl_name)
            self.grid.addWidget(label, field_index + 1, 0)
        self.text_label = QLabel(text, self)
        self.grid.addMultiCellWidget(self.text_label, 0, 0, 0, 1)

    def getRecordData(self):
        """Returns a dictionary of the fields and entries.
        All values will be python strings."""
        entry_items = self.entries.items()
        record_data = {}
        for key, entry in entry_items:
            record_data[key] = str(entry.text())
        return record_data

    def setRecordData(self, record_data):
        """This member sets the entries according to the
        dictionary that is passed to it."""
        for field, value in record_data.items():
            self.entries[field].setText(value)

    def setText(self, text):
        """Sets the text of the main label."""
        self.text_label.setText(text)
        
    
        
