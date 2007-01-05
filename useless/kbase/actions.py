from qt import QString
from kdecore import KShortcut
from kdeui import KGuiItem, KAction


# This is a quick way to make KGuiItem's
class BaseItem(KGuiItem):
    def __init__(self, text, icon, ttip, whatsit):
        KGuiItem.__init__(self, QString(text), QString(icon), QString(ttip),
                          QString(whatsit))
        
# This only bypasses passing a shortcut argument to KAction
# useful for items that have no shortcuts
class BaseAction(KAction):
    def __init__(self, item, slot, parent, name='BaseAction'):
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)
        
