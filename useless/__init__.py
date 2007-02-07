import warnings

def deprecated(msg):
    warnings.warn(msg, DeprecationWarning, stacklevel=3)

