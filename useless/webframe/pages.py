import cherrypy
from document import BaseDocument


class BasePage(object):
    def __init__(self, docclass=BaseDocument):
        self._docclass = docclass
        
    def get_docobject(self):
        if 'DocumentObject' not in cherrypy.session:
            doc = self._docclass()
            cherrypy.session['DocumentObject'] = doc
        doc = cherrypy.session['DocumentObject']
        self.prepare_doc(doc)
        return doc

    def prepare_doc(self, doc):
        raise NotImplementedError, 'prepare_doc needs to be defined in a subclass'
    
    def get_username(self):
        username = ''
        if 'username' in cherrypy.session:
            username  = cherrypy.session['username']
        return username

    def get_session(self):
        return cherrypy.session
    
    
class DocPage(BasePage):
    h1 = 'Doc Page'
    h2 = 'Doc Page'
    foot = 'Doc Page'
    menu_entries = []
    menu_head = 'Basic Menu'
    image = {}
    
    def prepare_doc(self, doc):
        doc.maintable.set_header(self.h1)
        doc.maintable.set_subhead(self.h2)
        doc.maintable.set_footer(self.foot)
        doc.setTitle(self.h1)
        doc.set_menu_entries(self.menu_entries, self.menu_head)
        doc.maintable.update_mainpage_attributes(align='center')
        doc.maintable.set_header_image(**self.image)
