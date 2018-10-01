# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds
# -- import lib
import naming.naming as naming
# ---- import end ----

def create(type=None, side=None, part=None, index=None, suffix=None, name = None):
	if not name:
		NamingNode = naming.Naming(type = type, 
							 	   side = side, 
							 	   part = part, 
							 	   index = index, 
							 	   suffix = suffix)
	else:
		NamingNode = naming.Naming(name)
	if not cmds.objExists(NamingNode.name):
		node = cmds.createNode(NamingNode.typeLongName, name = NamingNode.name)
	else:
		node = NamingNode.name
		logger.warn('{} already exists, skipped'.format(node))
	return node