from forgethtml import SimpleDocument
from forgethtml import Favicon
from tables import MainTable

class BaseDocument(SimpleDocument):
    def __init__(self, title='BaseDocument', stylesheet='/css/default.css', **args):
        SimpleDocument.__init__(self, title=title, stylesheet=stylesheet)
        self.set_stylesheet(stylesheet)
        self.favicon = Favicon()
        self.head.append(self.favicon)
        self.maintable = MainTable('BasePage', **args)
        #body.set will overwrite the self.header h1 tag
        self.body.set(self.maintable)
        # always start with login
        #self.maintable.set_mainrow(BaseLoginForm('/doLogin'))
            

    def set_stylesheet(self, sheet):
        self.setStylesheet(sheet)
        
    def set_page_data(self, page):
        self.maintable.set_page_data(page)

    def append_page_data(self, item):
        self.maintable.append_page_data(item)
        
    def clear_page_data(self):
        self.maintable.clear_page_data()
        
    def reset_menu_entries(self):
        self.maintable.reset_menu_entries()

    def set_menu_entries(self, entries, header=None):
        self.maintable.set_menu_entries(entries, header)

