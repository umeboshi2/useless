from qt import QWidget
from qt import PYSIGNAL, SIGNAL


from kdecore import KURL
from kdeui import KMessageBox
from khtml import KHTMLPart

from utbase import get_application_pointer
from utdoc import InfoDoc

from utdialogs import BaseGuestDialog
from utdialogs import BaseWorksDialog
from utdialogs import BaseGuestAppearanceDialog

class InfoPart(KHTMLPart):
    def __init__(self, parent, name='InfoPart'):
        KHTMLPart.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.doc = InfoDoc(self.app)

        self.dialog_parent = QWidget(None, 'dialog_parent')
        self.begin()
        self.write('')
        self.end()

        # preload dialog attributes with None
        self.edit_guest_dlg = None
        self.new_works_dlg = None
        self.edit_works_dlg = None
        self.new_appearance_dlg = None
        
    def set_guest_info(self, guestid):
        self.begin()
        self.write('')
        self.end()
        self.app.processEvents()
        self.begin()
        self.doc.set_info(guestid)
        self.guestid = guestid
        self.write(self.doc.output())
        self.end()
        self.emit(PYSIGNAL('GuestInfoSet'), (guestid,))

    ####################################################
    # the methods in this section map url's to actions #
    ####################################################
    def urlSelected(self, url, button, state, target, args):
        if url.find('||') > -1:
            self._perform_url_action(url)
        else:
            self.openURL(KURL(url))
            
    def _perform_url_action(self, url):
        entity, action, ident = str(url).split('||')
        if entity == 'guest':
            self._perform_guest_action(action, ident)
        elif entity == 'work':
            self._perform_works_action(action, ident)
        elif entity == 'appearance':
            self._perform_appearance_action(action, ident)
        else:
            KMessageBox.error(self.dialog_parent,
                              'Unable to parse url: %s' % url)

    def _perform_guest_action(self, action, guestid):
        if action == 'edit':
            data = self.app.guests.get_guest_data(int(guestid))
            win = BaseGuestDialog(self.dialog_parent)
            win.set_guest_data(data)
            win.guestid = guestid
            win.show()
            self.connect(win, SIGNAL('okClicked()'), self.update_guest_data)
            self.edit_guest_dlg = win
        else:
            KMessageBox.error(self.dialog_parent, 'unknown action %s' % action)

    def _perform_works_action(self, action, ident):
        if action == 'new':
            win = BaseWorksDialog(self.dialog_parent)
            win.guestid = self.guestid
            win.show()
            self.connect(win, SIGNAL('okClicked()'), self.add_new_work)
            self.new_works_dlg = win
        elif action == 'edit':
            win = BaseWorksDialog(self.dialog_parent)
            win.workid = ident
            data = self.app.guests.get_single_work(ident)
            win.set_data(data)
            win.show()
            self.connect(win, SIGNAL('okClicked()'), self.update_work)
            self.edit_works_dlg = win
        else:
            KMessageBox.error(self.dialog_parent, 'unknown action %s' % action)

    def _perform_appearance_action(self, action, guestid):
        if action == 'new':
            win = BaseGuestAppearanceDialog(self.dialog_parent)
            win.guestid = guestid
            win.show()
            self.connect(win, SIGNAL('okClicked()'), self.add_new_appearance)
            self.new_appearance_dlg = win
        else:
            KMessageBox.error(self.dialog_parent, 'unknown action %s' % action)
            
    ###################################################
    # below here are the slots for the dialog windows #
    ###################################################
    def update_guest_data(self):
        if self.edit_guest_dlg is not None:
            dlg = self.edit_guest_dlg
            data = dlg.get_guest_data()
            self.app.guests.update_guest_data(data)
            guestid = dlg.guestid
            self.edit_guest_dlg = None
            self.emit(PYSIGNAL('GuestInfoUpdated'), (guestid,))

    def add_new_work(self):
        if self.new_works_dlg is not None:
            dlg = self.new_works_dlg
            data = dlg.get_data()
            guestid = dlg.guestid
            self.app.guests.insert_new_work(guestid, data)
            self.new_works_dlg = None
            self.emit(PYSIGNAL('GuestInfoUpdated'), (guestid,))

    def update_work(self):
        if self.edit_works_dlg is not None:
            dlg = self.edit_works_dlg
            data = dlg.get_data()
            self.app.guests.update_work(dlg.workid, data)
            self.edit_works_dlg = None
            self.emit(PYSIGNAL('GuestInfoUpdated'), (self.guestid,))
            
            
            
    def add_new_appearance(self):
        if self.new_appearance_dlg is not None:
            dlg = self.new_appearance_dlg
            data = dlg.get_data()
            guestid = dlg.guestid
            self.app.guests.insert_new_appearance(guestid, data['url'])
            self.new_appearance_dlg = None
            self.emit(PYSIGNAL('GuestInfoUpdated'), (guestid,))
            
            
            
