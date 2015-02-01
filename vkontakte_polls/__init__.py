try:
    from . import signals
except:
    pass

VERSION = (0, 7, 2)
__version__ = '.'.join(map(str, VERSION))
