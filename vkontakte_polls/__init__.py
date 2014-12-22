from django.core.exceptions import ImproperlyConfigured

try:
    from . import signals
except ImproperlyConfigured:
    pass

VERSION = (0, 7, 0)
__version__ = '.'.join(map(str, VERSION))
