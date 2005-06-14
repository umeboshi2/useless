
class Error(Exception):
    pass

class ExistsError(Error):
    pass

class NoExistError(Error):
    pass
class NoFileError(NoExistError):
    pass

class UnbornError(NoExistError):
    pass

class TableError(ExistsError):
    pass


