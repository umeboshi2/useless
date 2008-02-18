import os
import urlparse
import datetime


from useless.base.forgethtml import SimpleDocument
from useless.base.forgethtml import Anchor, Table
from useless.base.forgethtml import TableRow, TableCell
from useless.base.forgethtml import TableHeader, Header
from useless.base.forgethtml import Image, Paragraph, Break
from useless.base.forgethtml import Inline, Ruler, Image, Span

from utbase import parse_wtprn_m3u_url
from utbase import make_2hr_wtprn_mp3_urls

def parse_appearance_m3u_url(url):
    date = parse_wtprn_m3u_url(url)
    sdate = date.ctime().replace('00:00:00', '')
    return sdate

def make_mp3_links(url):
    return make_2hr_wtprn_mp3_urls(url)


    
class Bold(Inline):
    tag = 'b'


class BaseMainTable(Table):
    def __init__(self, app, class_='BaseMainTable',
                 border=1, cellspacing=0, width='100%', **args):
        Table.__init__(self, class_=class_, border=border,
                       cellspacing=cellspacing, width=width)
        self.app = app
        
class BaseDocument(SimpleDocument):
    def __init__(self, app, tableclass=BaseMainTable,
                 title='BaseDocument', **args):
        SimpleDocument.__init__(self, title=title)
        self.app = app
        self.maintable = tableclass(self.app)
        self.body.set(self.maintable)

class GuestWorksTable(Table):
    def __init__(self, border=1, **args):
        Table.__init__(self, border=border, **args)

    # here works is the set of rows returned from
    # db.get_guest_works(guestid)
    def set_info(self, works):
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
            self.append(trow)

        
class GuestTable(BaseMainTable):
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
        self.set(fullname_row)
        title = data['title']
        if title:
            title = TableCell(title, colspan=2)
            title_row = TableRow(title)
            self.append(title_row)
        desc = data['description']
        if desc:
            desc = self.app.guests.unescape_text(desc)
            span = Span(desc)
            cell = TableCell(span, colspan=2)
            if len(desc) > 150:
                span['style'] = 'font-size: x-small'
            desc_row = TableRow(cell)
            self.append(desc_row)

        #################
        # works section #
        #################
        workheader = TableHeader('Works', colspan=0, align='center')
        new_work_anchor = Anchor('add',
                                 href='work||new||%d' % guestid)
        cell = TableCell(new_work_anchor)
        workheader_row = TableRow(workheader)
        workheader_row.append(cell)
        self.append(workheader_row)
        # add works
        works = guests_db.get_guest_works(guestid)
        if works:
            worktable = GuestWorksTable(width='100%')
            worktable.set_info(works)
            cell = TableCell(worktable, colspan=2)
            trow = TableRow(cell)
            self.append(trow)
        else:
            workheader.set('No Works')

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
        self.append(appearance_header_row)
        appearances = guests_db.get_appearances(guestid)
        if appearances:
            for row in appearances:
                #print row
                url = row['url']
                sdate = parse_appearance_m3u_url(url)
                app_anchor = Anchor(sdate, href=url)
                cell = TableCell(app_anchor)
                h1, h2 = make_mp3_links(url)
                h1_anchor = Anchor('(hr1)', href=h1)
                h2_anchor = Anchor('(hr2)', href=h2)
                span = Span(style='font-size: xx-small')
                span.append(h1_anchor)
                span.append(h2_anchor)
                cell.append(span)
                trow = TableRow(cell)
                cell = TableCell()
                edit_anchor = Anchor('edit',
                                     href='appearance||edit||%s' % url)
                play_anchor = Anchor('(play)',
                                     href='appearance||play||%s' % url)
                cell.append(edit_anchor)
                cell.append(play_anchor)
                trow.append(cell)
                self.append(trow)
        else:
            appearance_header.set('No Appearances')
        
        #######################
        # pictures section    #
        #######################
        pix_header = TableHeader('Pictures',
                                 colspan=0, align='center')
        newpix_anchor = Anchor('add',
                               href='picture||new||%d' % guestid)
        cell = TableCell(newpix_anchor)
        pix_header_row = TableRow(pix_header)
        pix_header_row.append(cell)
        self.append(pix_header_row)
        pictures = guests_db.get_guest_pictures(guestid)
        if pictures:
            datadir = self.app.datadir
            for row in pictures:
                filename = row['all_pictures.filename']
                fullpath = os.path.join(datadir, filename)
                image = Image(src=fullpath, width='100', height='100')
                cell = TableCell(image)
                trow = TableRow(cell)
                span = Span(style='font-size: xx-small')
                span.append(filename)
                cell = TableCell(span)
                trow.append(cell)
                self.append(trow)
        else:
            pix_header.set('No Pictures')
        
class InfoDoc(BaseDocument):
    def __init__(self, app, tableclass=GuestTable,
                 title='Guest Information', **args):
        BaseDocument.__init__(self, app, tableclass=tableclass,
                              title=title, **args)

    def set_info(self, guestid):
        self.maintable.set_info(guestid)
        
class AllGuestsDoc(BaseDocument):
    def set_info(self):
        guests = self.app.guests.get_guest_rows()
        for row in guests:
            table = GuestTable(self.app)
            table.set_info(row['guestid'])
            cell = TableCell(table)
            trow = TableRow(cell)
            self.maintable.append(trow)
            splitrow = TableRow(bgcolor='Blue')
            splitrow.set(TableCell(bgcolor='Blue'))
            self.maintable.append(splitrow)
        #print self.output()

    def set_info_manually(self, guests):
        for row in guests:
            table = GuestTable(self.app)
            table.set_info(row['guestid'])
            cell = TableCell(table)
            trow = TableRow(cell)
            self.maintable.append(trow)
            splitrow = TableRow(bgcolor='Blue')
            splitrow.set(TableCell(bgcolor='Blue'))
            self.maintable.append(splitrow)
        #print self.output()
            
class InfoDocOrig(BaseDocument):
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
        else:
            workheader.set('No Works')
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
        else:
            appearance_header.set('No Appearances')
        
        #######################
        # pictures section    #
        #######################
        pix_header = TableHeader('Pictures',
                                 colspan=0, align='center')
        newpix_anchor = Anchor('add',
                               href='picture||new||%d' % guestid)
        cell = TableCell(newpix_anchor)
        pix_header_row = TableRow(pix_header)
        pix_header_row.append(cell)
        self.maintable.append(pix_header_row)
        pictures = guests_db.get_guest_pictures(guestid)
        if pictures:
            datadir = self.app.datadir
            for row in pictures:
                filename = row['all_pictures.filename']
                fullpath = os.path.join(datadir, filename)
                image = Image(src=fullpath, width='100', height='100')
                print image
                cell = TableCell(image)
                trow = TableRow(cell)
                cell = TableCell(filename)
                trow.append(cell)
                self.maintable.append(trow)
        else:
            pix_header.set('No Pictures')
            
