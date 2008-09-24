import os
from os.path import join, isdir, isfile

from pyPgSQL.libpq import PgQuoteString as quote

from useless.base import debug
from useless.base.config import Configuration
from useless.base.util import makepaths
from useless.base.objects import Parser

from useless.sqlgen.statement import Statement

from lowlevel import BasicConnection
from midlevel import StatementCursor

def dquote(string):
    return '"%s"' %string

class AdminConnection(object):
    """This isn't being used anymore.  It's been updated to use
    the BasicConnection class, but it's probably going to be
    transferred to another object one day, or removed
    completely."""
    def __init__(self, user=None, host=None, dbname=None, passwd=None,
                 port=5432):
        object.__init__(self)
        self.conn = BasicConnection(user=user, host=host, dbname=dbname,
                                    passwd=passwd, port=port)
        self.cursor = StatementCursor(self.conn, name='AdminConnection')
        self.stmt = Statement('select')
        self.dbname = dbname
        self.set_path(cfg.get('database', 'export_path'))

    def set_path(self, directory):
        self.path = directory
        makepaths(self.path)
        os.system('chmod 777 %s' % self.path)
        
    def to_tsv(self, table, key=None):
        self.stmt.table = table
        query = self.stmt.select(order=key)
        tsv = file(join(self.path, table + '.tsv'), 'w')
        self.cursor.execute(query)
        fields = [x[0] for x in self.cursor.description]
        tsv.write('\t'.join(map(quote, fields))+'\n')
        row = self.cursor.fetchone()
        while row:
            line = []
            for field in row:
                if field == None:
                    field = 'NULL'
                else:
                    field = str(field)
                line.append(quote(field))
            tsv.write('\t'.join(line)+'\n')
            row = self.cursor.fetchone()
        tsv.close()
        
    def set_table(self, table):
        self.stmt.set_table(table)

    def insert(self, table):
        self.cursor.set_table(table)
        tsv = Parser(join(self.path, table + '.tsv'))
        for row in tsv:
            self.cursor.insert(data=row)

    def copyto(self, table):
        path = join(self.path, table + '.bkup')
        self.cursor.copyto(table, path)

    def copyfrom(self, table):
        path = join(self.path, table + '.bkup')
        self.cursor.copyfrom(table, path)


    def backup(self):
        map(self.copyto, self.cursor.tables())

        
