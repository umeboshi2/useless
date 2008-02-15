import urlparse
import datetime


from useless.base.forgethtml import SimpleDocument
from useless.base.forgethtml import Anchor, Table
from useless.base.forgethtml import TableRow, TableCell
from useless.base.forgethtml import TableHeader, Header
from useless.base.forgethtml import Image, Paragraph, Break
from useless.base.forgethtml import Inline


def parse_appearance_m3u_url(url):
    utuple = urlparse.urlparse(url)
    m3u_filename = utuple[2].split('/')[-1]
    show_date = m3u_filename.split('_')[0]
    year = int(show_date[:4])
    month = int(show_date[4:6])
    day = int(show_date[6:8])
    date = datetime.date(year, month, day)
    sdate = date.ctime().replace('00:00:00', '')
    return sdate

    
class Bold(Inline):
    tag = 'b'

class BaseDocument(SimpleDocument):
    def __init__(self, app, title='BaseDocument', **args):
        SimpleDocument.__init__(self, title=title)
        self.app = app
        self.maintable = Table(class_='BaseDocumentMainTable',
                               border=1, cellspacing=0, width='100%')
        self.body.set(self.maintable)


class InfoDoc(BaseDocument):
    def set_info(self, guestid):
        guests_db = self.app.guests
        data = guests_db.get_guest_data(guestid)
        name = '%s %s' % (data['firstname'], data['lastname'])
        fullname = TableHeader(name, colspan=0, align='center')
        fullname_row = TableRow(fullname)
        edit_anchor = Anchor('edit',
                             href='guest||edit||%d' % guestid)
        cell = TableCell(edit_anchor)
        fullname_row.append(cell)
        self.maintable.set(fullname_row)
        title = data['title']
        if title:
            title = TableCell(title, colspan=2)
            title_row = TableRow(title)
            self.maintable.append(title_row)
        desc = data['description']
        if desc:
            desc = self.app.guests.unescape_text(desc)
            desc = TableCell(desc, colspan=2)
            desc_row = TableRow(desc)
            self.maintable.append(desc_row)
        #################
        # works section #
        #################
        workheader = TableHeader('Works', colspan=0, align='center')
        new_work_anchor = Anchor('add',
                                 href='work||new||%d' % guestid)
        cell = TableCell(new_work_anchor)
        workheader_row = TableRow(workheader)
        workheader_row.append(cell)
        self.maintable.append(workheader_row)
        # add works
        works = guests_db.get_guest_works(guestid)
        if works:
            worktable = Table(border=1)
            for row in works:
                # the result is from a table join
                # so the row elements are in the form
                # table.column
                title = row['all_works.title']
                url = row['all_works.url']
                wtype = row['all_works.type']
                work_anchor = Anchor(title, href=url)
                cell = TableCell(wtype, colspan=1)
                trow = TableRow(cell)
                cell = TableCell(work_anchor, colspan=3)
                trow.append(cell)
                workid = row['all_works.workid']
                edit_anchor = Anchor('edit',
                                     href='work||edit||%d' % workid)
                trow.append(TableCell(edit_anchor, colspan=1))
                worktable.append(trow)
                cell = TableCell(worktable, colspan=2)
                trow = TableRow(cell)
            self.maintable.append(trow)
        #######################
        # appearances section #
        #######################
        appearance_header = TableHeader('Appearances',
                                        colspan=0, align='center')
        new_appearance_anchor = Anchor('add',
                                       href='appearance||new||%d' % guestid)

        cell = TableCell(new_appearance_anchor)
        appearance_header_row = TableRow(appearance_header)
        appearance_header_row.append(cell)
        self.maintable.append(appearance_header_row)
        appearances = guests_db.get_appearances(guestid)
        if appearances:
            for row in appearances:
                #print row
                url = row['url']
                sdate = parse_appearance_m3u_url(url)
                app_anchor = Anchor(sdate, href=url)
                cell = TableCell(app_anchor)
                trow = TableRow(cell)
                edit_anchor = Anchor('edit',
                                     href='appearance||edit||%s' % url)
                trow.append(TableCell(edit_anchor))
                self.maintable.append(trow)
        
