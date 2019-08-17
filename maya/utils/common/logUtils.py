# IMPORT PACKAGES

# import for debug
import logging

# import PySide
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2 import __version__
    from shiboken2 import wrapInstance
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import __version__
    from shiboken import wrapInstance

# CONSTANT
LOG_LEVEL = {'info': logging.INFO,
             'warning': logging.WARNING,
             'error': logging.ERROR,
             'critical': logging.CRITICAL,
             'debug': logging.DEBUG}

LOG_LEVEL_INDEX = {'debug': -1,
                   'info': 0,
                   'warning': 1,
                   'error': 2,
                   'critical': 3}

logger_debug = logging.getLogger('debug')


# class
class Connector(QObject):
    SIGNAL_EMIT = Signal(str, str)


class Log(object):
    def __init__(self):
        self.connector = Connector()

    def info(self, message):
        logger_debug.setLevel(LOG_LEVEL['info'])
        logger_debug.info(message)

        message = self.format_message('info', message)
        self.connector.SIGNAL_EMIT.emit(message, 'info')

    def warning(self, message):
        logger_debug.setLevel(LOG_LEVEL['warning'])
        logger_debug.warning(message)

        message = self.format_message('warning', message)
        self.connector.SIGNAL_EMIT.emit(message, 'warning')

    def error(self, message):
        logger_debug.setLevel(LOG_LEVEL['error'])
        logger_debug.error(message)

        message = self.format_message('error', message)
        self.connector.SIGNAL_EMIT.emit(message, 'error')

    def critical(self, message):
        logger_debug.setLevel(LOG_LEVEL['critical'])
        logger_debug.critical(message)

        message = self.format_message('critical', message)
        self.connector.SIGNAL_EMIT.emit(message, 'critical')

    def debug(self, message):
        logger_debug.setLevel(LOG_LEVEL['debug'])
        logger_debug.debug(message)

        message = self.format_message('debug', message)
        self.connector.SIGNAL_EMIT.emit(message, 'debug')

    @staticmethod
    def format_message(level, message):
        return '[log info] - [{}] - {}'.format(level, message)


# logger
logger = Log()
