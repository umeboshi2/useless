import os
#from sqlite.main import Connection, Cursor
from useless.db.lowlevel import LocalConnection
from useless.db.midlevel import StatementCursor

from useless.sqlgen.clause import Eq

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

    def insert_new_appearance(self, guestid, url):
        cursor = self.conn.stmtcursor()
        data = dict(guestid=guestid, url=url)
        cursor.insert('appearances', data)
        

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
    

