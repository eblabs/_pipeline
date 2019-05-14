#=================#
# IMPORT PACKAGES #
#=================#

## import maya packages
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

## import utils
import naming
import attributes
import variables
#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#

#=================#
#    FUNCTION     #
#=================#
def create(name, **kwargs):
	'''
	create transform node

	Args:
		name(str): transform node's name
	Kwargs:
		lockHide(list)[]: lock and hide transform attrs
		parent(str)[None]: where to parent the transform node
		rotateOrder(int)[0]: transform node's rotate order
		vis(bool)[True]: transform node's visibility
		pos(str/list): match transform's position to given node/transform value
					   str: match translate and rotate to the given node
					   [str/None, str/None]: match translate/rotate to the given node
					   [[x,y,z], [x,y,z]]: match translate/rotate to given values
		inheritsTransform(bool)[True]: set transform node's inheritance attr
	'''
	# get vars
	lockHide = variables.kwargs('lockHide', [], kwargs, shortName='lh')
	parent = variables.kwargs('parent', None, kwargs, shortName='p')
	rotateOrder = variables.kwargs('rotateOrder', 0, kwargs, shortName='ro')
	vis = variables.kwargs('vis', True, kwargs, shortName='v')
	pos = variables.kwargs('pos', None, kwargs)
	inherits = variables.kwargs('inheritsTransform', True, kwargs)

	# create transform
	transform = cmds.createNode('transform', name=name)

	# ro
	cmds.setAttr(transform+'.ro', rotateOrder)

	# vis
	cmds.setAttr(transform+'.v', vis)

	# inheritance
	cmds.setAttr(transform+'.inheritsTransform', inherits)

	# match pos
	if pos:
		if isinstance(pos, basestring):
			cmds.matchTransform(transform, pos, pos=True, rot=True)
		else:
			if isinstance(pos[0], basestring):
				cmds.matchTransform(transform, pos[0], pos=True, rot=False)
			else:
				cmds.xform(transform, t=pos[0], ws=True)
			if isinstance(pos[1], basestring):
				cmds.matchTransform(transform, pos[1], pos=False, rot=True)
			else:
				cmds.xform(transform, rot=pos[1], ws=True)
	# parent
	if parent:
		parent_node(transform, parent)

	# lock hide
	attributes.lock_hide_attrs(transform, lockHide)

	return transform

def parent_node(node, parent):
	'''
	parent node

	Args:
		node(str/list): node
		parent(str): parent node
	'''	
	if isinstance(node, basestring):
		node = [node]
	if not cmds.objExists(parent):
		Logger.warn('{} does not exist'.format(parent))
		return
	for n in node:
		if not cmds.objExists(n):
			Logger.warn('{} does not exist'.format(n))
		# check parent
		p = cmds.listRelatives(n, p=True)
		if p and p[0]==parent:
			Logger.warn('{} is parented to {} already'.format(n, parent))
		else:
			cmds.parent(n, parent)


def bounding_box_info(nodes):
	'''
	get given nodes/pos bounding box info

	Args:
		nodes(list)
	Returns:
		max(list): max X/Y/Z
		min(list): min X/Y/Z
		center(list): pos X/Y/Z
	'''
	posX = []
	posY = []
	posZ = []
	for n in nodes:
		if isinstance(n, basestring) and cmds.objExists(n):
			pos = cmds.xform(n, q=True, t=True, ws=True)
			posX.append(pos[0])
			posY.append(pos[1])
			posZ.append(pos[2])
		elif isinstance(n, list):
			posX.append(n[0])
			posY.append(n[1])
			posZ.append(n[2])
	maxPos = [max(posX), max(posY), max(posZ)]
	minPos = [min(posX), min(posY), min(posZ)]
	centerPos = [(maxPos[0]+minPos[0])*0.5,
				 (maxPos[1]+minPos[1])*0.5,
				 (maxPos[2]+minPos[2])*0.5]

	return maxPos, minPos, centerPos


#=================#
#  SUB FUNCTION   #
#=================#