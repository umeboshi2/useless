from pyPgSQL.libpq import PgQuoteString as quote
from pyPgSQL.libpq import OperationalError

from useless.base import Error, debug, NoExistError
from useless.base.util import ujoin
from useless.sqlgen.statement import Statement
from useless.sqlgen.classes import Table, Sequence
from useless.sqlgen.defaults import ActionIdentifier, LogTable, ActionTrigger

from lowlevel import CommandCursor
from midlevel import StatementCursor

plpgsql_log_action = """create or replace function action_stamp() returns trigger as '
        declare
           logtable varchar ;
           row RECORD ;
	begin
        logtable :=  ''lp_log_'' || TG_RELNAME ;
	execute ''insert into '' || logtable
        || ''  values (''''''
        || new, TG_OP || '''''')'';
        return new  ;
	end ;
' language 'plpgsql';
"""

class MainCursor(StatementCursor):
    def __init__(self, conn, name=None):
        StatementCursor.__init__(self, conn, name=name)

    def create_table(self, table):
        if table.name[:7] != 'lp_log_':
            StatementCursor.create_table(self, table)
            logtable = LogTable(table)
            StatementCursor.create_table(self, logtable)
            self.create_trigger(ActionTrigger(table.name))

