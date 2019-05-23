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

class Component(object):
	"""
	Component base class

	Args:
		component(str)
	Kwargs:
		side(str)
		description(str)
		index(int)
		parent(str)
		blueprintJoints(list)
		offsets(int): controls' offset groups
		controlSize(float)
		controlColor(str/int): None will follow the side's preset
		subControl(bool)[True]
	Returns:
		Component(obj)
	"""
	def __init__(self, *arg, **kwargs):
		self._componentType = COMPONENT_PATH + '.component'
		self._ctrls = []
		self._jnts = []
		self._nodesLocal = []
		self._nodesShow = []
		self._nodesHide = []

		self.register_attributes(kwargs)

		if arg:
			self.get_component_info(arg[0])

	@property
	def name(self):
		return self._component
	
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

	def register_attributes(self, kwargs):
		self.register_kwargs()
		self.register_inputs(kwargs)

	def register_kwargs(self):
		self._kwargs = {'side': ['side', naming.Side.middle, 's'],
						'des': ['description', '', 'des'],
						'index': ['index', None, 'i'],
						'parent': ['parent', None, 'p'],
						'bpJnts': ['blueprintJoints', [], 'bpJnts'],
						'offsets': ['offsets', 1, naming.Type.offset],
						'ctrlSize': ['controlSize', 1, 'size'],
						'ctrlCol': ['controlColor', None, 'color'],
						'sub': ['subControl', True, 'sub']}
	
	def register_inputs(self, kwargs):
		for key, val in self._kwargs.iteritems():
			if len(val) > 2:
				shortName = val[2]
			else:
				shortName = None
			attrVal = variables.kwargs(val[0], val[1], kwargs, shortName=shortName)
			self.__setattr__('_'+key, attrVal)

	def create(self):
		'''
		create rig component
		'''
		self.create_component()
		self.register_component_info()
		self.get_component_info(self._component)

	def create_component(self):
		'''
		create component node hierarchy
		
		component
			-- localGrp
				-- controlsGrp
				-- jointsGrp
				-- nodesLocalGrp
			-- worldGrp
				-- nodesHideGrp
				-- nodesShowGrp
		'''

		Namer = naming.Namer(type=naming.Type.component,
							 side=self._side,
							 description=self._des,
							 index=self._index)

		# create transforms
		attrDict = {}
		for trans in ['component', 'controlsGrp', 'localGrp',
					  'jointsGrp', 'nodesLocalGrp', 'worldGrp',
					  'nodesHideGrp', 'nodesShowGrp']:
			Namer.type = trans
			transforms.create(Namer.name, lockHide=attributes.Attr.all)
			attrDict.update({'_'+trans: Namer.name})
		self._add_attr_from_dict(attrDict)

		# parent hierarchy
		hierarchy.parent_node(self._component, self._parent)
		cmds.parent(self._localGrp, self._worldGrp, self._component)
		cmds.parent(self._controlsGrp, self._jointsGrp, self._nodesLocalGrp, self._localGrp)
		cmds.parent(self._nodesHideGrp, self._nodesShowGrp, self._worldGrp)

		# inheritsTransform
		cmds.setAttr(self._worldGrp+'.inheritsTransform', 0)

		# add attrs
		# input matrix: input connection from other component
		# offset matrix: offset from the input to the current component
		# inputComponent: message info to get input component name
		# controls: message info to get all the controllers' names
		# joints: message info to get all the joints' names
		# controlsVis: controls visibility switch
		# jointsVis: joints visibility switch
		# rigNodesVis: rig nodes visibility switch
		# componentType: component class type to get the node wrapped as object
		# outputMatrix: joints' output matrices

		attributes.add_attrs(self._component, ['inputMatrix', 'offsetMatrix'],
							attributeType='matrix', lock=True)
		cmds.addAttr(self._component, ln='inputComponent', at='message')
		attributes.add_attrs(self._component, ['controls', 'joints'],
							attributeType='message', multi=True)
		attributes.add_attrs(self._component, ['controlsVis', 'jointsVis', 'rigNodesVis'],
							attributeType='long', range=[0,1], 
							defaultValue=[1,0,0,1], keyable=False, channelBox=True)
		attributes.add_attrs(self._component, 'componentType', attributeType='string',
							lock=True)
		cmds.addAttr(self._component, ln='outputMatrix', at='matrix', multi=True)
		
		# connect attrs
		attributes.connect_attrs(['controlsVis', 'jointsVis', 'rigNodesVis', 
								  'rigNodesVis'], 
								 [self._controlsGrp+'.v', self._jointsGrp+'.v',
								  self._nodesLocalGrp+'.v', self._nodesHideGrp+'.v'], 
								  driver=self._component)

		# mult matrix
		multMatrixAttr = nodeUtils.mult_matrix([self._component+'.inputMatrix',
											self._component+'.offsetMatrix'],
										   side=self._side, description=self._des,
										   index=self._index)

		constraints.matrix_connect(multMatrixAttr, self._localGrp)

	def register_component_info(self):
		# rig component type
		attributes.set_attrs(self._component+'.componentType', self._componentType, type='string')

		# control message
		for i, ctrl in enumerate(self._ctrls):
			cmds.connectAttr(ctrl+'.message', 
							 '{}.controls[{}]'.format(self._component, i), f=True)

		# joint message and output matrix
		for i, jnt in enumerate(self._jnts):
			cmds.connectAttr(jnt+'.message',
							 '{}.joints[{}]'.format(self._component, i), f=True)
			cmds.connectAttr(jnt+'.worldMatrix[0]',
							 '{}.outputMatrix[{}]'.format(self._component, i), f=True)

	def get_component_info(self, component):
		self._component = component
		self._componentType = self._get_attr(self._component+'.componentType')
		self._inputComponent = self._get_attr(self._component+'.inputComponent', message=True)
		self._ctrls = self._get_attr(self._component+'.controls', message=True, asList=True)
		self._jnts = self._get_attr(self._component+'.joints', message=True, asList=True)

		# input matrix
		self._inputMatrixAttr = self._component+'.inputMatrix'
		self._offsetMatrixAttr = self._component+'.offsetMatrix'
		
		# output matrix
		outputMatrixDict = {'_outputMatrixAttr': []}
		if self._jnts:
			for i in range(len(self._jnts)):
				outputMatrixDict['_outputMatrixAttr'].append(self._component+'.outputMatrix[{}]'.format(i))

		self._add_attr_from_dict(outputMatrixDict)

	def _add_attr_from_dict(self, attrDict):
		'''
		add class attributes from given dictionary
		'''
		for key, val in attrDict.iteritems():
			setattr(self, key, val)

	def _get_attr(self, attr, message=False, asList=False):
		driver = attr.split('.')[0]
		attrName = attr.replace(driver+'.', '')
		if cmds.attributeQuery(attrName, n=driver, ex=True):
			if not message:
				val = self._get_attr_val(attr, asList=asList)
			else:
				val = self._get_message_attr(attr, asList=asList)
		else:
			val = None
		return val

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
				attrList.append(val)
			return attrList
