#=================#
# IMPORT PACKAGES #
#=================#

## import for debug
import logging

#=================#
#   GLOBAL VARS   #
#=================#
logging.basicConfig(level=logging.WARNING)
Logger = logging.getLogger(__name__)
Logger.setLevel(logging.WARNING)

COMPONENT_PATH = 'dev.rigging.component.core'