from pyPgSQL import PgSQL
from pyPgSQL.PgSQL import Connection, Cursor, PgLargeObject
from pyPgSQL.PgSQL import PgResultSet, make_PgResultSetClass
from pyPgSQL.libpq import IntegrityError, OperationalError

class Record(PgResultSet):
    def __init__(self, value, desc):
        PgResultSet._desc_ = desc
        PgResultSet._xlatkey = {}
        for column in range(len(desc)):
            self._xlatkey[desc[column][0]] = column
        PgResultSet.__init__(self, value)
        
class RefRecordOrig(PgResultSet):
    def __init__(self, record, refdata):
        PgResultSet._desc_ = record._desc_
        PgResultSet._xlatkey = {}
        PgResultSet._refdata = refdata
        desc = record._desc_
        for column in range(len(desc)):
            self._xlatkey[desc[column][0]] = column
        PgResultSet.__init__(self, record.baseObj)

def RefRecord(record, refdata):
    record.__dict__['_refdata'] = refdata
    return record

class EmptyRefRecord(dict):
    def __init__(self, fields, refdata):
        dict.__init__(self, [(f, '') for f in fields])
        self._refdata = refdata
        
class PsyCursor(object):
    def __init__(self, conn):
        object.__init__(self)
        self.__dict__['_cursor'] = conn.cursor()
        self.__dict__['conn'] = conn

    def __getattr__(self, member):
        print '__getattr__', member
        return getattr(self._cursor, member)

    def __setattr__(self, member, value):
        print '__setattr__', member
        setattr(self._cursor, member, value)
        
if __name__ == '__main__':
    import psycopg
    conn = psycopg.connect('host=zathras dbname=konsultant')
    c = PsyCursor(conn)
    c.execute('select * from locations')
    rows = c.fetchall()
    
    desc = c.description
    recs = [Record(row, desc) for row in rows]
    r = recs[2]
    rr = RefRecord(r, dict(foo='hello'))
    
