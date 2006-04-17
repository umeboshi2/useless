import os
from forgethtml import Anchor
from forgethtml import TableHeader, TableCell
from forgethtml import TableRow, Table
from forgethtml import Header

from forgethtml import Image

#from base import HOSTNAME, Bold
#from base import reroot_href
#from util import get_file_dir_list
#from util import OutOfBasePathError
#from util import InvalidPathError

class BaseMenu(Table):
    def __init__(self, header='BaseMenu', **args):
        Table.__init__(self, **args)
        self._menu = {}
        self.set_header(header)
        self.top_entry = None
        self.bottom_entry = None
        
    def set_header(self, header=None):
        if header is not None:
            self._header = header
        self.set(TableRow(TableHeader(self._header)))
        
    def append_new_entry(self, name, page):
        atts = {}
        if 'class' in self.attributes:
            atts['class'] = self['class']
        self._menu[name] = Anchor(name, href=page)
        td = TableCell(self._menu[name], **atts)
        self.append(TableRow(td, **atts))

    def set_new_entries(self, entries, header=None):
        self.set_header(header)
        if self.top_entry:
            self.append_new_entry(*self.top_entry)
            #self.append_new_entry('home', reroot_href('/')
        for name, page in entries:
            self.append_new_entry(name, page)
        if self.bottom_entry:
            self.append_new_entry(*self.bottom_entry)
            #self.append_new_entry('logout', reroot_href('/doLogout'))
        
class MainMenu(BaseMenu):
    def __init__(self, **args):
        header = 'Main Menu'
        BaseMenu.__init__(self, header=header, class_='mainmenu', **args) 
        self._base_header = header
        self.entries = []
        self.reset_entries()

    def reset_entries(self):
        self.set_new_entries(self.entries, self._base_header)

    def clear_entries(self):
        self.entries = []
        self.reset_entries()
        
class OneCellTable(Table):
    def __init__(self, cell='One Cell', **args):
        Table.__init__(self, **args)
        self.mainrow = TableRow()
        self.cell = TableCell(cell)
        self.mainrow.set(self.cell)
        self.set(self.mainrow)

    def set_celldata(self, data):
        self.cell.set(data)
        
class MainHeader(Table):
    def __init__(self, subhead='subhead', image_=None, **args):
        Table.__init__(self, width='100%', class_='mainheader', colspan=0, **args)
        atts = {'class' : 'mainheader'}
        self.h1 = Header('hello there', 1)
        self.h2 = Header(subhead, 2)
        toprow = TableRow(**atts)
        if image_ is None:
            image_ = Image()
        self._image = image_
        toprow.append(TableCell(image_, align='left', **atts))
        toprow.append(TableCell(self.h1, align='center', **atts))
        self.append(toprow)
        self.append(TableRow(TableCell(self.h2, colspan=3, align='center',
                                       **atts), **atts))

    def set_h1(self, info):
        self.h1.set(info)

    def set_h2(self, info):
        self.h2.set(info)

    def set_image(self, **atts):
        self._image.attributes.update(atts)
    
class MainFooter(Table):
    def __init__(self, subhead='subhead', **args):
        Table.__init__(self, width='100%', _class='mainfooter', **args)
        self.anchors = []
    
        home = Anchor('Home', href='/')
        up = Anchor('Up', href='index')
        rel = Anchor('Reload', href='javascript:document.location.reload()')
        row = TableRow()
        row.extend(map(TableCell, [home, rel, up]))
        self._subhead = TableCell(subhead, colspan=3)
        head = TableRow(self._subhead)
        self.extend([head, row])

    def set_subhead(self, subhead):
        self._subhead.set(subhead)
        
class MainFooterNew(Table):
    def __init__(self, subhead='subhead', **args):
        Table.__init__(self, width='100%', _class='mainfooter', **args)
        self.a_home = Anchor('Home', href='/')
        self.a_up = Anchor('Up', href='index')
        self.a_reload = Anchor('Reload', href='javascript:document.location.reload()')
        self.mainrow = TableRow()
        self.cell_subhead = TableCell(subhead)
        self.headrow = TableRow(self.cell_subhead)
        self.extend([self.headrow, self.mainrow])
        self.reset_nav_anchors()
        
    def reset_nav_anchors(self):
        anchors = [self.a_home, self.a_reload, self.a_up]
        self.mainrow.clear()
        self.mainrow.extend(anchors)
        
    def set_subhead(self, subhead):
        self.cell_subhead.set(subhead)
        
class MainTable(Table):
    def __init__(self, page, **args):
        class_atts = dict(class_='maintable')
        headfoot_atts = dict(colspan=2)
        headfoot_atts.update(class_atts)
        Table.__init__(self, width='100%', **class_atts)
        self._header = MainHeader('hello')
        self._footer = MainFooter('hello')
        self._headcell = TableCell(self._header, **headfoot_atts)
        self._footcell = TableCell(self._footer, **headfoot_atts)
        headrow = TableRow(self._headcell, **class_atts)
        self.append(headrow)
        self._mainrow = TableRow(**class_atts)
        self._mainmenu = MainMenu(width='100%')
        self._mainmenu_cell = TableCell(self._mainmenu, rowspan=1,
                                        colspan=1, valign='top', **class_atts)
        self._mainrow.append(self._mainmenu_cell)
        self._mainpage = TableCell(page, width='75%', align='center', **class_atts)
        self._mainrow.append(self._mainpage)
        self.append(self._mainrow)
        footrow = TableRow(self._footcell, **class_atts)
        self.append(footrow)

    def update_mainpage_attributes(self, **atts):
        self._mainpage.attributes.update(atts)
        
    def set_page_data(self, page):
        self._mainpage.set(page)

    def append_page_data(self, item):
        self._mainpage.append(item)

    def clear_page_data(self):
        self._mainpage.clear()
        
    def set_header(self, data):
        self._header.set_h1(data)

    def set_header_image(self, **atts):
        self._header.set_image(**atts)
        
    def set_subhead(self, data):
        self._header.set_h2(data)
        
    def set_footer(self, data):
        self._footer.set_subhead(data)

    def set_mainrow(self, data, tablecell=False):
        if not tablecell:
            self._mainrow.set(data)
        else:
            raise IndexError, "not an index error, passing tablecell is unimplemented now"

    def reset_mainrow(self):
        self._mainrow.set(self._mainmenu_cell)
        self._mainrow.append(self._mainpage)

    def set_menu_entries(self, entries, header=None):
        self._mainmenu.set_new_entries(entries, header)

    def reset_menu_entries(self):
        self._mainmenu.reset_entries()
