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

def connectChain(nodeList, reverse = False):
	if reverse:
		nodeList.reverse()

	for i, node in enumerate(nodeList[:-1]):
		cmds.parent(node, nodeList[i+1])

	return nodeList[-1]

def parent(nodes, parent):
	if isinstance(nodes, basestring):
		nodes = [nodes]
	if parent and cmds.objExists(parent):
		for n in nodes:
			p = cmds.listRelatives(n, p = True)
			if not p or p[0] != parent:
				cmds.parent(n, parent)
