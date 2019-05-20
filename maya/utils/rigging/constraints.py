#=================#
# IMPORT PACKAGES #
#=================#

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.naming as naming
import utils.common.attributes as attributes
import utils.common.variables as variables
import utils.common.nodeUtils as nodeUtils
import utils.common.mathUtils as mathUtils
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

def matrix_connect(inputMatrix, nodes, **kwargs):
	'''
	connect input matrix to given nodes

	Args:
		inputMatrix(str): input matrix attribute
		nodes(str/list): given nodes
	Kwargs:
		offset(bool)[False]: maintain offset
		skip(list): skip channels
		force(bool)[True]: force connect
	'''
	offset = variables.kwargs('offset', '', kwargs)
	skip = variables.kwargs('skip', [], kwargs)
	force = variables.kwargs('force', True, kwargs, shortName='f')

	driver = inputMatrix.split('.')[0]
	attrName = cmds.ls(inputMatrix)[0].split('.')[-1]
	
	NameDriver = naming.Namer(driver)
	NameDriver.type = naming.Type.decomposeMatrix
	NameDriver.description = NameDriver.description + attrName[0].upper() + attrName[1:]

	desOffset = NameDriver.description+'Offset'

	if isinstance(nodes, basestring):
		nodes = [nodes]

	if offset:
		matrixOffset = cmds.getAttr(offset+'.worldMatrix[0]')

	driverAttrs = []
	drivenAttrs = []
	for attr in attributes.Attr.transform:
		attrShort = attr[0]+attr[-1].lower()
		if attr not in skip and attrShort not in skip:
			driverAttrs.append('output{}{}'.format(attr[0].upper(), attr[1:]))
			drivenAttrs.append(attr)

	if not offset:
		decomposeMatrix = nodeUtils.node(name=NameDriver.name, useExist=True)
		cmds.connectAttr(inputMatrix, decomposeMatrix+'.inputMatrix')
		for n in nodes:
			attributes.connect_attrs(driverAttrs, drivenAttrs,
									 driver=decomposeMatrix, driven=n, force=force)
	else:
		# get latest suffix
		multMatrixOffset = naming.Namer(type=naming.Type.multMatrix,
										side=NameDriver.side,
										description=desOffset,
										index=NameDriver.index).name
		multMatrixOffset = cmds.ls(multMatrixOffset+'_???')
		if multMatrixOffset:
			multMatrixOffset.sort()
			NameOffset = naming.Namer(multMatrixOffset[-1])
			if NameOffset.suffix:
				suffix = NameOffset.suffix
			elif NameOffset.index:
				suffix = NameOffset.index
		else:
			suffix = 0
		for i, n in enumerate(nodes):
			offsetMatrix = cmds.getAttr(n+'.worldMatrix[0]')
			offsetMatrixInv = mathUtils.inverse_matrix(offsetMatrix)
			multMatrix = nodeUtils.mult_matrix([inputMatrix, offsetMatrixInv],
											   side=NameDriver.side,
											   description=desOffset,
											   index=NameDriver.index,
											   suffix=suffix+i+1)
			decomposeMatrix = nodeUtils.node(type=naming.Type.decomposeMatrix,
											 side=NameDriver.side,
											 description=desOffset,
											 index=NameDriver.index,
											 suffix=suffix+i+1)
			cmds.connectAttr(multMatrix+'.matrixSum', decomposeMatrix+'.inputMatrix')
			attributes.connect_attrs(driverAttrs, drivenAttrs,
									 driver=decomposeMatrix, driven=n, force=force)

#=================#
#  SUB FUNCTION   #
#=================#