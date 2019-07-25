# =================#
#  IMPORT PACKAGES #
# =================#

# import for debug
import logging

#=================#
#   GLOBAL VARS   #
#=================#
LOG_LEVEL = {'info': logging.INFO,
			 'warning': logging.WARNING,
			 'error': logging.ERROR,
			 'critical': logging.CRITICAL,
			 'debug': logging.DEBUG}

#=================#
#    FUNCTION     #
#=================#
def get_logger(name='debugLogger', level='info'):
	level = LOG_LEVEL[level]
	logging.basicConfig(level=level)
	logger = logging.getLogger(name)
	logger.setLevel(level)
	return logger