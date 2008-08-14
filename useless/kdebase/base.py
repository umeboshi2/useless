from qt import SIGNAL
from kdecore import KApplication

#def get_application_pointer():
#    """This function does nothing special, but is easier to remember."""
#    return KApplication.kApplication()

# rename KApplication.kApplication to something easier to remember
get_application_pointer = KApplication.kApplication

class HasDialogs(object):
    """This is a helper class for objects that have child dialogs.
    How to use:
      if self.current_dialog is None:
        win = SomeDialog(self)
        win.show()
        self.connect_dialog(win, self.slot_some_dialog_ok)

      def slot_some_dialog_ok(self):
          win = self.current_dialog
          value = str(win.entry.text())
          self.destroy_current_dialog()
          """
    def __init__(self):
        self.current_dialog = None

    def connect_dialog(self, window, ok_clicked):
        """Connects the okClicked() signal
        on window to ok_clicked"""
        self.connect(window, SIGNAL('okClicked()'), ok_clicked)
        self.connect_destroy_dialog(window)
        
    def connect_destroy_dialog(self, window):
        """Handles the signals cancelClicked() and
        closeClicked() on window"""
        self.connect(window, SIGNAL('cancelClicked()'), self.destroy_current_dialog)
        self.connect(window, SIGNAL('closeClicked()'), self.destroy_current_dialog)
        self.current_dialog = window

    def destroy_current_dialog(self):
        """Call this method at the end of the
        ok_clicked slot to dereference the dialog"""
        self.current_dialog = None
        
