from useless.sqlgen.classes import Table, Column
from useless.sqlgen.defaults import Text, Name, Bigname
from useless.sqlgen.defaults import PkNum, Num, NUM

class AutoId(Column):
    def __init__(self, colname):
        Column.__init__(self, colname, NUM)
        self.constraint.pk = True
        self.constraint.unique = True
        self.constraint.null = False
        self.constraint.auto = True

    def __write__(self):
        col = '%s' % self.name
        col += ' INTEGER AUTOINCREMENT'
        return col
        
class GuestTable(Table):
    def __init__(self):
        idcol = AutoId('guestid')
        fname = Name('firstname')
        lname = Name('lastname')
        salutation = Name('salutation')
        title = Bigname('title')
        desc = Text('description')
        cols = [idcol, fname, lname, salutation, title, desc]
        Table.__init__(self, 'guests', cols)

class WorksTable(Table):
    def __init__(self):
        idcol = AutoId('workid')
        type_ = Name('type')
        title = Bigname('title')
        url = Bigname('url')
        desc = Text('description')
        cols= [idcol, type_, title, url, desc]
        Table.__init__(self, 'all_works', cols)
    
class GuestWorks(Table):
    def __init__(self):
        guestid = PkNum('guestid')
        workid = PkNum('workid')
        cols = [guestid, workid]
        Table.__init__(self, 'guest_works', cols)
        
class GuestAppearances(Table):
    def __init__(self):
        idcol = Num('guestid')
        url = Bigname('url')
        cols = [idcol, url]
        Table.__init__(self, 'appearances', cols)
        

def generate_schema(cursor):
    cursor.create_table(GuestTable())
    cursor.create_table(WorksTable())
    cursor.create_table(GuestWorks())
    cursor.create_table(GuestAppearances())
    
    
if __name__ == '__main__':
    gt = GuestTable()
    
