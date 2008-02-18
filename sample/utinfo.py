import os
from shutil import copy2 as copyfile

from qt import QWidget
from qt import PYSIGNAL, SIGNAL


from kdecore import KURL
from kdeui import KMessageBox
from khtml import KHTMLPart
from kfile import KFileDialog
from dcopext import DCOPObj
from kio import KIO

from useless.base.util import md5sum

from utbase import get_application_pointer
from utbase import make_2hr_wtprn_mp3_urls
from utdoc import InfoDoc
from utdoc import AllGuestsDoc

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
        self.new_picture_dlg = None
        
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

    def view_all_guests(self):
        self.begin()
        self.write('')
        self.end()
        self.app.processEvents()
        self.begin()
        #self.doc.set_info(guestid)
        self.guestid = None
        doc = AllGuestsDoc(self.app)
        doc.set_info()
        self.write(doc.output())
        self.end()
        

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
        elif entity == 'picture':
            self._perform_picture_action(action, ident)
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

    def _perform_appearance_action(self, action, ident):
        if action == 'new':
            win = BaseGuestAppearanceDialog(self.dialog_parent)
            win.guestid = ident
            win.show()
            self.connect(win, SIGNAL('okClicked()'), self.add_new_appearance)
            self.new_appearance_dlg = win
        elif action == 'play':
            dcop = self.app.dcopClient()
            iface = DCOPObj('kaffeine', dcop, 'KaffeineIface')
            hr1_url, hr2_url = make_2hr_wtprn_mp3_urls(ident)
            hr1_filename = hr1_url.split('/')[-1]
            hr2_filename = hr2_url.split('/')[-1]
            datadir = self.app.datadir
            hr1 = os.path.join(datadir, hr1_filename)
            hr2 = os.path.join(datadir, hr2_filename)
            if not os.path.exists(hr1):
                kl = KURL.List()
                kl.append(KURL(hr1_url))
                KIO.copy(kl, KURL('file://%s' % hr1))
            if not os.path.exists(hr2):
                kl = KURL.List()
                kl.append(KURL(hr2_url))
                KIO.copy(kl, KURL('file://%s' % hr2))
                
            ok, void = iface.openURL(hr1)
            print ok, void, hr1
            ok, void = iface.appendURL(hr2)
            print ok, void, hr2
            
            #KMessageBox.information(self.dialog_parent,
            #                        'play with kaffeine')
        else:
            KMessageBox.error(self.dialog_parent, 'unknown action %s' % action)

    def _perform_picture_action(self, action, guestid):
        if action == 'new':
            win = KFileDialog('', '', self.dialog_parent,
                              'select_picture_file', True)
            win.connect(win, SIGNAL('okClicked()'),
                        self.add_new_picture)
            win.guestid = guestid
            self.new_picture_dlg = win
            win.show()
        else:
            KMessageBox.error(self.dialog_parent,
                              'unknown action %s' % action)
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
            
    def add_new_picture(self):
        if self.new_picture_dlg is not None:
            dlg = self.new_picture_dlg
            url = dlg.selectedURL()
            fullpath = str(url.path())
            filename = os.path.basename(fullpath)
            datadir = self.app.datadir
            guestid = dlg.guestid
            newfile = os.path.join(datadir, filename)
            if os.path.exists(newfile):
                KMessageBox.error(self.dialog_parent,
                                  'File %s already exists' % filename)
                return
            if self.copy_picture_file(fullpath, newfile):
                self.app.guests.insert_new_picture(guestid,
                                                   dict(filename=filename))
                self.emit(PYSIGNAL('GuestInfoUpdated'), (self.guestid,))

            

    def copy_picture_file(self, oldpath, newpath):
        copyfile(oldpath, newpath)
        oldmd5sum = md5sum(file(oldpath))
        newmd5sum = md5sum(file(newpath))
        if oldmd5sum != newmd5sum:
            os.remove(newpath)
            KMessageBox.error(self.dialog_parent,
                              "%s didn't copy properly, try again.")
            return False
        else:
            return True
            
                                      
        
