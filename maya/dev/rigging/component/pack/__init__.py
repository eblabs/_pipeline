#=================#
# IMPORT PACKAGES #
#=================#

## import os
import os

## import for debug
import logging

#=================#
#   GLOBAL VARS   #
#=================#
logging.basicConfig(level=logging.WARNING)
Logger = logging.getLogger(__name__)
Logger.setLevel(logging.WARNING)

COMPONENT_PATH = 'dev.rigging.component.pack'
CONFIG_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(CONFIG_PATH, 'config')
