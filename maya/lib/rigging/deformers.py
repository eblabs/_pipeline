# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import common.naming.naming as naming
import common.attributes
import common.apiUtils
# ---- import end ----

# wire deformer
def createWireDeformer(node, wire, name, dropoffDistance = 200):
	cmds.wire(node, wire = wire, name = name, dropoffDistance = dropoffDistance)
	baseWire = cmds.listConnections('{}.baseWire[0]'.format(name), s = True, d = False, p = False)[0]
	NamingWire = naming.naming(wire)
	NamingWire.type = 'wireBase'
	baseWire = cmds.rename(baseWire, NamingWire.name)
	return [name, baseWire]