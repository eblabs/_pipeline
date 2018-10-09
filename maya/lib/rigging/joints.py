# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.naming.naming as naming
import lib.common.transforms as transforms
import lib.modeling.curves as curves
# ---- import end ----

def create(name, rotateOrder=0, parent=None, posPoint=None, posOrient=None, posParent=None, scaleCompensate=True):
	cmds.select(clear = True)
	jnt = cmds.joint(name = name)
	cmds.setAttr('{}.ro'.format(jnt), rotateOrder)
	transforms.setNodePos(jnt, posPoint = posPoint, posOrient = posOrient, posParent = posParent)
	cmds.makeIdentity(jnt, apply = True, t = 1, r = 1, s = 1)
	cmds.setAttr('{}.segmentScaleCompensate'.format(jnt), scaleCompensate)
	if parent and cmds.objExists(parent):
		cmds.parent(jnt, parent)
	return jnt

def createOnNode(node, search, replace, suffix='', parent=None, rotateOrder=False, scaleCompensate=True):
	jnt = node.replace(search, replace)
	NamingJnt = naming.Naming(jnt)
	NamingJnt.part = NamingJnt.part + suffix
	jnt = NamingJnt.name
	if rotateOrder:
		ro = cmds.getAttr('{}.ro'.format(node))
	else:
		ro = 0
	jnt = create(jnt, rotateOrder = ro, parent = parent, posParent = node, scaleCompensate = scaleCompensate)
	return jnt

def createOnHierarchy(nodes, search, replace, suffix='', parent=None, rotateOrder=False, scaleCompensate=True):
	jntList = []
	if isinstance(search, basestring):
		search = [search]
	if isinstance(replace, basestring):
		replace = [replace]
	for i, n in enumerate(nodes):
		jntNew = n
		for name in zip(search, replace):
			jntNew = jntNew.replace(name[0], name[1])
		jnt = createOnNode(n, n, jntNew, suffix = suffix, parent = parent, 
							rotateOrder = rotateOrder, scaleCompensate = scaleCompensate)
		jntList.append(jnt)
		
	# connect
	for jnts in zip(jntList, nodes):
		parentNode = cmds.listRelatives(jnts[1], p = True)
		if parentNode and parentNode[0] in nodes:
			index = nodes.index(parentNode[0])
			parent = jntList[index]
			cmds.parent(jnts[0], parent)

	return jntList

def getJointOrient(jnt):
	jointOrient = []
	for axis in ['X', 'Y', 'Z']:
		orient = cmds.getAttr('{}.jointOrient{}'.format(jnt, axis))
		jointOrient.append(orient)
	return jointOrient

def createJointsAlongCurve(curve, num, suffix=None, parent = None, startNode=None, endNode=None, scaleCompensate=True):
	NamingNode = naming.Naming(curve)
	NamingNode.part += suffix
	NamingNode.type = 'joint'
	paramList = curves.getCurveParamRange(curve)
	for i, node in enumerate([startNode, endNode]):
		if node:
			param, pos = curves.getClosestPointOnCurve(curve, node)
			paramList[i] = param
	startParam = min(paramList)
	endParam = max(paramList)

	jntList = []
	if num > 1:
		paramEach = float(endParam - startParam) / float(num - 1)
		for i in range(num):
			param = paramEach * i + startParam
			NamingNode.suffix = i + 1
			posJnt = curves.getPointAtParam(curve, param)
			jnt = create(NamingNode.name, parent = parent, posPoint = posJnt, scaleCompensate = scaleCompensate)
			jntList.append(jnt)
	else:
		NamingNode.suffix = 1
		posJnt = curves.getPointAtParam(curve, startParam)
		jnt = create(NamingNode.name, parent = parent, posPoint = posJnt, scaleCompensate = scaleCompensate)
		jntList.append(jnt)

	return jntList

def createInBetweenJoints(startJoint, endJoint, num, overrideName=None, chain=True, parent=None, type='joint'):
	NamingNode = naming.Naming(startJoint)
	if not overrideName:
		overrideName = NamingNode.part
	NamingNode.type = type

	dis = cmds.getAttr('{}.tx'.format(endJoint))
	disDiv = float(dis)/float(num - 1)
	
	jntList = []
	for i in range(num):
		NamingNode.part = '{}{:03d}'.format(overrideName, i+1)
		transformInfo = transforms.getWorldTransformOnParent(translate = [disDiv*i,0,0], parent = startJoint)
		jnt = create(NamingNode.name, parent = parent, posParent = transformInfo)
		if chain:
			parent = jnt
		jntList.append(jnt)
	return jntList

# tag joints
def tagJoints(jnts):
	sideKey = {'m': 0,
			   'l': 1,
			   'r': 2}
	for j in jnts:
		NamingJnt = naming.Naming(j)
		cmds.setAttr('{}.side'.format(j), sideKey[NamingJnt.side])
		cmds.setAttr('{}.type'.format(j), 18)
		tagPart = ''
		for part in [NamingJnt.part, NamingJnt.index, NamingJnt.suffix]:
			if part:
				tagPart += '{}_'.format(part) 
		cmds.setAttr('{}.otherType'.format(j), tagPart[:-1], type = 'string')