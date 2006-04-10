from forgethtml import SimpleDocument

class BaseDocument(SimpleDocument):
    def __init__(self, title='BasePage', stylesheet='/css/default.css', **args):
        SimpleDocument.__init__(self, title=title, stylesheet=stylesheet)
        self.set_stylesheet()
        self._auth_handler = SimpleAuthHandler()
        self._authenticated = False
        self.favicon = Favicon()
        self.head.append(self.favicon)
        self.maintable = MainTable('BasePage', **args)
        #body.set will overwrite the self.header h1 tag
        self.body.set(self.maintable)
        # always start with login
        #self.maintable.set_mainrow(BaseLoginForm('/doLogin'))
            

    def set_stylesheet(self, sheet):
        self.setStylesheet(reroot_href('/css/%s' % sheet))
        
    def set_page_data(self, page):
        self.maintable.set_page_data(page)

    def append_page_data(self, item):
        self.maintable.append_page_data(item)
        
    def clear_page_data(self):
        self.maintable.clear_page_data()
        
    def set_authentication(self, *args):
        self.maintable.reset_mainrow()
        self._authenticated = True
        
    def unset_authentication(self):
        self.maintable.set_mainrow(BaseLoginForm('/doLogin'))
        self._authenticated = False

    def authenticate(self, username, password):
        return self._auth_handler.authenticate(username, password)
    
    def change_login(self, username, password):
        self._auth_handler.change_login(username, password)

    def reset_menu_entries(self):
        self.maintable.reset_menu_entries()

    def set_menu_entries(self, entries, header=None):
        self.maintable.set_menu_entries(entries, header)

    def is_authenticated(self):
        return self._authenticated
    
