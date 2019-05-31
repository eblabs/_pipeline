#=================#
# IMPORT PACKAGES #
#=================#

## import for debug
import logging

## Component path
from . import COMPONENT_PATH

#=================#
#   GLOBAL VARS   #
#=================#
logging.basicConfig(level=logging.WARNING)
Logger = logging.getLogger(__name__)
Logger.setLevel(logging.WARNING)

COMPONENT_PATH += '.pack'