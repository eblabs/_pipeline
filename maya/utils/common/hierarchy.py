#=================#
# IMPORT PACKAGES #
#=================#

## import maya packages
import maya.cmds as cmds

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
def parent_node(nodes, parent):
	'''
	parent nodes under given parent node

	Args:
		nodes(str/list): given nodes
		parent(str): given parent node
	'''
	if isinstance(nodes, basestring):
		nodes=[nodes]
	if parent and cmds.objExists(parent):
		for n in nodes:
			p = cmds.listRelatives(n, p=True)
			if not p or p[0] != parent:
				cmds.parent(n, parent)

def parent_chain(nodes, reverse=False, parent=None):
	'''
	chain parent given nodes

	Args:
		nodes(list): given nodes
	Kwargs:
		reverse(bool)[False]: reverse parent order
		parent(str): parent chain
	Return:
		nodes(list)
	'''
	chainNodes = nodes[:]
	if reverse:
		chainNodes.reverse()
	chainNodes.append(parent)
	num = len(chainNodes)
	for i in range(num-1):
		parent_node(chainNodes[i], chainNodes[i+1])
	nodesReturn = chainNodes[:-1]
	if reverse:
		nodesReturn.reverse()
	return nodesReturn


