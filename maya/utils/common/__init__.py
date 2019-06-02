#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import os

## import for debug
import logging

#=================#
#   GLOBAL VARS   #
#=================#
CONFIG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config')

logging.basicConfig(level=logging.WARNING)
Logger = logging.getLogger(__name__)
Logger.setLevel(logging.WARNING)