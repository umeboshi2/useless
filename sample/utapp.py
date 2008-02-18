import os
import traceback
from StringIO import StringIO

from qt import SIGNAL, SLOT

from kdecore import KAboutData
from kdecore import KApplication
from kdecore import KStandardDirs

from kdeui import KAboutDialog
from kdeui import KMessageBox

from utdblite import Connection, Guests
from utdbschema import generate_schema

# about this program
class AboutData(KAboutData):
    def __init__(self):
        version = '0.0.0'
        KAboutData.__init__(self,
                            'utguests',
                            'utguests',
                            version,
                            "Another database frontend")
        self.addAuthor('Joseph Rawson', 'author',
                       'umeboshi3@gmail.com')
        self.setCopyrightStatement('public domain')

class AboutDialog(KAboutDialog):
    def __init__(self):
        KAboutDialog.__init__(self, parent, *args)
        self.setTitle('Uncover Truth Frontend')
        self.setAuthor('Joseph Rawson')
        
# main application class
class MainApplication(KApplication):
    def __init__(self):
        KApplication.__init__(self)
        # in case something needs done before quitting
        self.connect(self, SIGNAL('aboutToQuit()'), self.quit)
        self._setup_standard_directories()
        #self._generate_data_directories()
        dbfile = os.path.join(self.datadir, 'guests.db')
        self.conn = Connection(dbname=dbfile, autocommit=True,
                               encoding='ascii')
        self.guests = Guests(self.conn)
        
        
    # this method sets up the directories used by the application
    # with respect to the KDE environment
    # currently the main config file is placed in self.datadir
    # changes in the file dialogs used in the application will
    # be stored in the config file in its proper location
    # when I am ready to deal with changes to that config file
    # that my code doesn't use, I will probably move the main
    # config file to the regular config location
    def _setup_standard_directories(self):
        self._std_dirs = KStandardDirs()
        self.tmpdir_parent = str(self._std_dirs.findResourceDir('tmp', '/'))
        self.datadir_parent = str(self._std_dirs.findResourceDir('data', '/'))
        self.tmpdir = os.path.join(self.tmpdir_parent, 'utguests')
        self.datadir = os.path.join(self.datadir_parent, 'utguests')
        # we need this in dosbox object (for now)
        self.main_config_dir = self.datadir
        if not os.path.exists(self.datadir):
            os.mkdir(self.datadir)

    # This method is currently useless, but may be useful later
    # if some house cleaning needs doing before quitting
    def quit(self):
        # house cleaning chores go here
        KApplication.quit(self)


if __name__ == '__main__':
    print "testing module"
    
