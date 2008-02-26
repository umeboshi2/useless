import os
#from sqlite.main import Connection, Cursor
from useless.db.lowlevel import LocalConnection
from useless.db.midlevel import StatementCursor

from useless.sqlgen.clause import Eq

from utbase import parse_wtprn_m3u_url
from utdbschema import generate_schema

DOUBLE_BS = '\\'
SINGLE_BS = DOUBLE_BS[0]
ESCAPED_ENDL = DOUBLE_BS + 'n'
def unescape_text(text):
    return text.replace(ESCAPED_ENDL, '\n')

class Connection(LocalConnection):
    def stmtcursor(self):
        return StatementCursor(self)


class Guests(object):
    def __init__(self, conn):
        self.conn = conn
        cursor = self.conn.stmtcursor()
        if not cursor.tables():
            generate_schema(cursor)
            if os.environ.has_key('UTDB_TESTING'):
                data = dict(firstname='joe', lastname='sixpack')
                cursor.insert('guests', data)
                data['lastname'] = 'schmoe'
                cursor.insert('guests', data)
                data['firstname'] = 'john'
                data['lastname'] = 'doe'
                cursor.insert('guests', data)
            

    def get_guest_data(self, guestid):
        clause = Eq('guestid', guestid)
        cursor = self.conn.stmtcursor()
        rows = cursor.select(table='guests', clause=clause)
        return rows[0]

    def update_guest_data(self, data):
        guestid = data['guestid']
        clause = Eq('guestid', guestid)
        cursor = self.conn.stmtcursor()
        cursor.update(table='guests', data=data, clause=clause)

    def insert_guest_data(self, data):
        cursor = self.conn.stmtcursor()
        cursor.insert(table='guests', data=data)

    def get_guest_rows(self):
        cursor = self.conn.stmtcursor()
        return cursor.select(table='guests')

    ######################
    # works methods      #
    ######################
    def get_guest_works(self, guestid):
        cursor = self.conn.stmtcursor()
        table = 'all_works natural join guest_works'
        clause = Eq('guestid', guestid)
        return cursor.select(table=table, clause=clause, order=['type'])

    def get_single_work(self, workid):
        cursor = self.conn.stmtcursor()
        clause = Eq('workid', workid)
        table = 'all_works'
        rows = cursor.select(table=table, clause=clause)
        return rows[0]

    def update_work(self, workid, data):
        clause = Eq('workid', workid)
        table = 'all_works'
        cursor = self.conn.stmtcursor()
        cursor.update(table=table, data=data, clause=clause)
        
        
    def insert_new_work(self, guestid, data):
        cursor = self.conn.stmtcursor()
        cursor.insert('all_works', data)
        workid = int(cursor.max('workid', 'all_works')[0]['max(workid)'])
        reldata = dict(guestid=guestid, workid=workid)
        cursor.insert('guest_works', reldata)


    ###########################
    # appearances methods     #
    ###########################
    def get_appearances(self, guestid):
        cursor = self.conn.stmtcursor()
        table = 'appearances'
        clause = Eq('guestid', guestid)
        return cursor.select(table=table, clause=clause, order=['url'])

    # the url here is the .m3u url from wtrpn archives page
    def insert_new_appearance(self, guestid, url):
        cursor = self.conn.stmtcursor()
        showdate = parse_wtprn_m3u_url(url)
        data = dict(guestid=guestid, showdate=showdate, url=url)
        cursor.insert('appearances', data)
        

    ###########################
    # pictures methods        #
    ###########################
    def insert_new_picture(self, guestid, data):
        cursor = self.conn.stmtcursor()
        cursor.insert('all_pictures', data)
        pixnum = int(cursor.max('pixnum', 'all_pictures')[0]['max(pixnum)'])
        reldata = dict(guestid=guestid, pixnum=pixnum)
        cursor.insert('guest_pictures', reldata)

    def get_guest_pictures(self, guestid):
        cursor = self.conn.stmtcursor()
        table = 'all_pictures natural join guest_pictures'
        clause = Eq('guestid', guestid)
        order = ['all_pictures.pixnum']
        return cursor.select(table=table, clause=clause, order=order)
    

    
    ###########################
    # helper methods          #
    ###########################
    def unescape_text(self, text):
        return unescape_text(text)
    
if __name__ == '__main__':
    import os
    dbfile = 'test.db'
    if os.environ.has_key('UTDBFILE'):
        dbfile = os.environ['UTDBFILE']
    conn = Connection(dbname=dbfile,
                      autocommit=True, encoding='ascii')
    cursor = conn.stmtcursor()
    from utdbschema import GuestTable, GuestWorks
    cursor.set_table('guests')
    unt = unescape_text
    
    # using this to make the html page for kma
    from utdoc import AllGuestsDoc
    from utdblite import Guests
    # we need a fake app class to get the
    # doc object to work correctly
    class FakeApp(object):
        def __init__(self, conn):
            self.guests = Guests(conn)
            self.datadir = os.path.dirname(dbfile)

    def makedoc():
        app = FakeApp(conn)
        guests = app.guests.get_guest_rows()
        doc = AllGuestsDoc(app)
        doc.set_info_manually(guests)
        f = file('utguests.html', 'w')
        f.write(doc.output())
        f.close()
        print 'html output complete'
        
    def parse_url(url):
        import urlparse
        import datetime
        utuple = urlparse.urlparse(url)
        m3u_filename = utuple[2].split('/')[-1]
        show_date = m3u_filename.split('_')[0]
        year = int(show_date[:4])
        month = int(show_date[4:6])
        day = int(show_date[6:8])
        date = datetime.date(year, month, day)
        return date
    
    def fill_datecol():
        from useless.sqlgen.clause import Eq
        cursor.set_table('appearances')
        rows = cursor.select()
        for row in rows:
            date = parse_url(row['url'])
            clause = Eq('guestid', row['guestid']) & Eq('url', row['url'])
            #print date, clause
            cursor.update(data=dict(showdate=date), clause=clause)
            #print row
