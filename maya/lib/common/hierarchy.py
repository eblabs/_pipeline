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
import attributes
import apiUtils
# ---- import end ----

def connectChain(nodeList, reverse = False):
	if reverse:
		nodeList.reverse()

	for i, node in enumerate(nodeList[:-1]):
		cmds.parent(node, nodeList[i+1])

	return nodeList[-1]
