# IMPORT PACKAGES

# import for debug
import logging

# CONSTANT
LOG_LEVEL = {'info': logging.INFO,
             'warning': logging.WARNING,
             'error': logging.ERROR,
             'critical': logging.CRITICAL,
             'debug': logging.DEBUG}


#  FUNCTION
def get_logger(name='debugLogger', level='info'):
    """
    get logger object

    Keyword Args:
        name(str): logger's name, default is 'debugLogger'
        level(str): logger's level, options are ['info', 'warning', 'error', 'critical', 'debug'], default is 'info'

    Returns:
        logger(obj): logger object
    """
    level = LOG_LEVEL[level]
    logging.basicConfig(level=level)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
