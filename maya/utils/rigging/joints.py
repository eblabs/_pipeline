#=================#
# IMPORT PACKAGES #
#=================#

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.hierarchy as hierarchy

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
	create single joint

	Args:
		name(str): joint's name
	Kwargs:
		rotateOrder(int)[0]: joint's rotate order
		parent(str): parent joint
		pos(str/list): match joint's position to given node/transform value
					   str: match translate and rotate to the given node
					   [str/None, str/None]: match translate/rotate to the given node
					   [[x,y,z], [x,y,z]]: match translate/rotate to given values
		vis(bool)[True]: visibility
	Returns:
		joint(str)
	'''
	# get vars
	ro = variables.kwargs('rotateOrder', 0, kwargs, shortName='ro')
	parent = variables.kwargs('parent', None, kwargs, shortName='p')
	pos = variables.kwargs('pos', None, kwargs)
	vis = variables.kwargs('vis', True, kwargs, shortName='v')

	# create joint
	if cmds.objExists(name):
		Logger.error('{} already exists in the scene'.format(name))
		return

	jnt = cmds.createNode('joint', name=name)
	cmds.setAttr(jnt+'.ro', ro)
	cmds.setAttr(jnt+'.v', vis)

	# pos
	# match pos
	if pos:
		if isinstance(pos, basestring):
			cmds.matchTransform(jnt, pos, pos=True, rot=True)
		else:
			if isinstance(pos[0], basestring):
				cmds.matchTransform(jnt, pos[0], pos=True, rot=False)
			else:
				cmds.xform(jnt, t=pos[0], ws=True)
			if isinstance(pos[1], basestring):
				cmds.matchTransform(jnt, pos[1], pos=False, rot=True)
			else:
				cmds.xform(jnt, rot=pos[1], ws=True)
		cmds.makeIdentity(jnt, apply=True, t=True, r=True, s=True)
	
	# parent
	hierarchy.parent_node(jnt, parent)

	return jnt

def create_on_node(node, search, replace, **kwargs):
	'''
	create joint base on given transform node

	Args:
		node(str): given transform node
		search(str/list): search name
		replace(str/list): replace name
	Kwargs:	
		suffix(str): add suffix description
		rotateOrder(int)[None]: joint's rotate order, 
								None will copy transform's rotate order
		parent(str): parent joint
		vis(bool)[True]: joint visibility
	Returns:
		joint(str) 
	'''
	# get vars
	if isinstance(search, basestring):
		search = [search]
	if isinstance(replace, basestring):
		replace = [replace]

	suffix = variables.kwargs('suffix', '', kwargs, shortName='sfx')
	ro = variables.kwargs('rotateOrder', None, kwargs, shortName='ro')
	parent = variables.kwargs('parent', None, kwargs, shortName='p')
	vis = variables.kwargs('vis', True, kwargs, shortName='v')

	# get joint name
	jnt = node
	for s, r in zip(search, replace):
		jnt = jnt.replace(s, r)
	Namer = naming.Namer(jnt)
	Namer.description = Namer.description + suffix
	jnt = Namer.name
	# check node exist
	if not cmds.objExists(node):
		Logger.error('{} does not exist'.format(node))
		return

	# create joint
	# get ro
	if ro == None:
		ro = cmds.getAttr(node+'.ro')
	# create
	jnt = create(jnt, rotateOrder=ro, parent=parent, pos=node, vis=vis)

	return jnt

def create_on_hierarchy(nodes, search, replace, **kwargs):
	'''
	create joints base on given hierarchy

	Args:
		nodes(list): given nodes
		search(str/list): search 
		replace(str/list): replace
	Kwargs:	
		suffix(str): add suffix description
		rotateOrder(int)[None]: joint's rotate order, 
								None will copy transform's rotate order
		parent(str): parent joint
		vis(bool)[True]: joint visibility
		reverse(bool)[False]: reverse parent 
	Returns:
		joints(list)
	'''
	# get vars
	suffix = variables.kwargs('suffix', '', kwargs, shortName='sfx')
	ro = variables.kwargs('rotateOrder', None, kwargs, shortName='ro')
	parent = variables.kwargs('parent', None, kwargs, shortName='p')
	vis = variables.kwargs('vis', True, kwargs, shortName='v')
	reverse = variables.kwargs('reverse', False, kwargs)
	
	# create jnts
	jntList = []

	for n in nodes:
		jnt = create_on_node(n, search, replace, suffix=suffix, 
							 rotateOrder=ro, parent=parent, vis=vis)
		jntList.append(jnt)

	# connect
	jntList = hierarchy.parent_chain(jntList, reverse=reverse, parent=parent)

	return jntList
