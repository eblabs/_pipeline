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
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
# ---- import end ----

def create(name, rotateOrder=0, parent=None, posPoint=None, posOrient=None, posParent=None):
	cmds.select(clear = True)
	jnt = cmds.joint(name = name)
	cmds.setAttr('{}.ro'.format(jnt), rotateOrder)
	transforms.setNodePos(jnt, posPoint = posPoint, posOrient = posOrient, posParent = posParent)
	cmds.makeIdentity(jnt, apply = True, t = 1, r = 1, s = 1)
	if parent and cmds.objExists(parent):
		cmds.parent(jnt, parent)
	return jnt

def createOnNode(node, search, replace, suffix='', parent=None, rotateOrder=False):
	jnt = node.replace(search, replace)
	NamingJnt = naming.naming(jnt)
	NamingJnt.part = NamingJnt.part + suffix
	jnt = NamingJnt.name
	if rotateOrder:
		ro = cmds.getAttr('{}.ro'.format(node))
	else:
		ro = 0
	jnt = create(jnt, rotateOrder = ro, parent = parent, posParent = node)
	return jnt

def createChainOnNodes(nodes, search, replace, suffix='', parent=None, rotateOrder=False):
	jntList = []
	if isinstance(search, basestring):
		search = [search]
	if isinstance(replace, basestring):
		replace = [replace]
	for i, n in enumerate(nodes):
		jntNew = n
		for name in zip(search, replace):
			jntNew = jntNew.replace(name[0], name[1])
		jnt = createOnNode(n, n, jntNew, suffix = suffix, parent = parent, rotateOrder = rotateOrder)
		parent = jnt
		jntList.append(jnt)
	return jntList

def getJointOrient(jnt):
	jointOrient = []
	for axis in ['X', 'Y', 'Z']:
		orient = cmds.getAttr('{}.jointOrient{}'.format(jnt, axis))
		jointOrient.append(orient)
	return jointOrient