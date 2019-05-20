#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.common.hierarchy as hierarchy
import utils.common.nodeUtils as nodeUtils
import utils.rigging.constraints as constraints
#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger, COMPONENT_PATH

#=================#
#      CLASS      #
#=================#

class RigComponent(object):
	"""RigComponent base class"""
	def __init__(self, *arg, **kwargs):
		self._side = variables.kwargs('side', 'middle', kwargs, shortName='s')
		self._des = variables.kwargs('description', '', kwargs, shortName='des')
		self._index = variables.kwargs('index', None, kwargs, shortName='i')
		self._parent = variables.kwargs('parent', None, kwargs, shortName='p')

		self._componentType = COMPONENT_PATH + '.rigComponent'
		self._ctrls = []
		self._jnts = []

		if arg:
			self.get_component_info(arg[0])

	@property
	def name(self):
		return self._rigComponent
	
	@property
	def controls(self):
		return self._ctrls

	@property
	def joints(self):
		return self._jnts

	@property
	def componentType(self):
		return self._componentType

	@property
	def inputComponent(self):
		return self._inputComponent

	@property
	def inputMatrixAttr(self):
		return self._inputMatrixAttr

	@property
	def inputMatrix(self):
		return self._get_attr_val(self._inputMatrixAttr)
	
	@property
	def offsetMatrixAttr(self):
		return self._offsetMatrixAttr

	@property
	def offsetMatrix(self):
		return self._get_attr_val(self._offsetMatrixAttr)

	@property
	def outputMatrixAttr(self):
		return self._outputMatrixAttr

	@property
	def outputMatrix(self):
		return self._get_attr_val(self._outputMatrixAttr, asList=True)

	def create(self):
		'''
		create rig component
		'''
		self.create_component()
		self.register_component_info()
		self.get_component_info(self._rigComponent)

	def create_component(self):
		'''
		create rig component node hierarchy
		
		rigComponent
			-- rigLocalGrp
				-- controlsGrp
				-- jointsGrp
				-- nodesLocalGrp
			-- rigWorldGrp
				-- nodesHideGrp
				-- nodesShowGrp
			-- subComponentsGrp
		'''

		Namer = naming.Namer(type=naming.Type.rigComponent,
							 side=self._side,
							 description=self._des,
							 index=self._index)

		# create transforms
		attrDict = {}
		for trans in ['rigComponent', 'controlsGrp', 'rigLocalGrp',
					  'jointsGrp', 'nodesLocalGrp', 'rigWorldGrp',
					  'nodesHideGrp', 'nodesShowGrp', 'subComponentsGrp']:
			Namer.type = trans
			transforms.create(Namer.name, lockHide=attributes.Attr.all)
			attrDict.update({'_'+trans: Namer.name})
		self._add_attr_from_dict(attrDict)

		# parent hierarchy
		hierarchy.parent(self._rigComponent, self._parent)
		cmds.parent(self._rigLocalGrp, self._rigWorldGrp, self._subComponentsGrp, self._rigComponent)
		cmds.parent(self._controlsGrp, self._jointsGrp, self._nodesLocalGrp, self._rigLocalGrp)
		cmds.parent(self._nodesHideGrp, self._nodesShowGrp, self._rigWorldGrp)

		# inheritsTransform
		cmds.setAttr(self._rigWorldGrp+'.inheritsTransform', 0)
		attributes.set_attrs([self._nodesLocalGrp+'.v', self._nodesHideGrp+'.v'], 0)

		# add attrs
		# input matrix: input connection from other component
		# offset matrix: offset from the input to the current component
		# inputComponent: message info to get input component name
		# controls: message info to get all the controllers' names
		# joints: message info to get all the joints' names
		# controlsVis: controls visibility switch
		# jointsVis: joints visibility switch
		# rigNodesVis: rig nodes visibility switch
		# subComponentsVis: sub components visibility switch
		# componentType: component class type to get the node wrapped as object
		# outputMatrix: joints' output matrices

		attributes.add_attrs(self._rigComponent, ['inputMatrix', 'offsetMatrix'],
							attributeType='matrix', lock=True)
		cmds.addAttr(self._rigComponent, ln='inputComponent', at='message')
		attributes.add_attrs(self._rigComponent, ['controls', 'joints'],
							attributeType='message', multi=True)
		attributes.add_attrs(self._rigComponent, ['controlsVis', 'jointsVis', 
												'rigNodesVis', 'subComponentsVis'],
							attributeType='long', range=[0,1], 
							defaultValue=[1,0,0,1], keyable=False, channelBox=True)
		attributes.add_attrs(self._rigComponent, 'componentType', attributeType='string',
							lock=True)
		cmds.addAttr(self._rigComponent, ln='outputMatrix', at='matrix', multi=True)
		
		# connect attrs
		attributes.connect_attrs(['controlsVis', 'jointsVis', 'rigNodesVis', 
								  'rigNodesVis', 'subComponentsVis'], 
								 [self._controlsGrp+'.v', self._jointsGrp+'.v',
								  self._nodesLocalGrp+'.v', self._nodesHideGrp+'.v',
								  self._subComponentsGrp+'.v'], driver=self._rigComponent)

		# mult matrix
		multMatrixAttr = nodeUtils.mult_matrix([self._rigComponent+'.inputMatrix',
											self._rigComponent+'.offsetMatrix'],
										   side=self._side, description=self._des,
										   index=self._index)

		constraints.matrix_connect(multMatrixAttr, self._rigLocalGrp)

	def register_component_info(self):
		# rig component type
		attributes.set_attrs(self._rigComponent+'.componentType', self._componentType, type='string')

		# control message
		for i, ctrl in enumerate(self._ctrls):
			cmds.connectAttr(ctrl+'.message', 
							 '{}.controls[{}]'.format(self._rigComponent, i), f=True)

		# joint message and output matrix
		for i, jnt in enumerate(self._jnts):
			cmds.connectAttr(jnt+'.message',
							 '{}.joints[{}]'.format(self._rigComponent, i), f=True)
			cmds.connectAttr(jnt+'.worldMatrix[0]',
							 '{}.outputMatrix[{}]'.format(self.rigComponent, i), f=True)

	def get_component_info(self, component):
		self._rigComponent = component
		self._componentType = cmds.getAttr(self._rigComponent+'.componentType')
		self._inputComponent = self._get_message_attr(self._rigComponent+'.inputComponent')
		self._ctrls = self._get_message_attr(self._rigComponent+'.controls', asList=True)
		self._jnts = self._get_message_attr(self._rigComponent+'.joints', asList=True)

		# input matrix
		self._inputMatrixAttr = self._rigComponent+'.inputMatrix'
		self._offsetMatrixAttr = self._rigComponent+'.offsetMatrix'
		
		# output matrix
		outputMatrixDict = {'_outputMatrixAttr': []}
		if self._jnts:
			for i in range(len(self._jnts)):
				outputMatrixDict['_outputMatrixAttr'].append(self._rigComponent+'.outputMatrix[{}]'.format(i))

		self._add_attr_from_dict(outputMatrixDict)

	def _add_attr_from_dict(self, attrDict):
		'''
		add class attributes from given dictionary
		'''
		for key, val in attrDict.iteritems():
			setattr(self, key, val)

	def _get_message_attr(self, attr, asList=False):
		val = cmds.listConnections(attr, s=True, d=False, p=False)
		if asList:
			return val
		elif val:
			return val[0]
		else:
			return None

	def _get_attr_val(self, attr, asList=False):
		if not asList:
			return cmds.getAttr(attr)
		else:
			attrList=[]
			for atr in attr:
				val = cmds.getAttr(atr)
				attrList.append(atr)
			return attrList
