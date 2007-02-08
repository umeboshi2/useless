import warnings

def deprecated(msg, stacklevel=3):
    warnings.warn(msg, DeprecationWarning, stacklevel=stacklevel)

