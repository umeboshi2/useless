import os


# this is an ugly hack to fix a problem with using a quote
# function specific to postgresql in the past.  The workaround
# that I'm using now sets an environment variable in os.environ
# the code is set to default back to the previous behaviour in the
# absence of the variable
# The main advantage to using this method is that it is not very
# intrusive to the previously written code (I had previously imported
# PgQuoteString aliased as "quote" in anticipation of using different quote
# functions)
# The main disadvantage to this method is that it make communication
# between two different db backend types more difficult, since it depends on
# an enviroment variable
# In the future, it may be better to instantiate each sqlgen class from a connection
# or cursor object

from pyPgSQL.libpq import PgQuoteString
from sqlite.main import _quote as sqlite_quote
# here we make a basic quote function
def quote(text):
    return "'%s'" % text

pg_quote = PgQuoteString
backend_key = '_USELESS_DB_BACKEND'
if os.environ.has_key(backend_key):
    if os.environ[backend_key] == 'sqlite':
        quote = sqlite_quote
    else:
        quote = pg_quote
else:
    # if there is no environment variable we default back to the old quote
    quote = pg_quote
