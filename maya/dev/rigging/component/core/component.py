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

## import base class
import dev.rigging.component.base as base

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger, COMPONENT_PATH

#=================#
#      CLASS      #
#=================#

class Component(base.Base):
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
		super(Component, self).__init__(*arg, **kwargs)
		self._componentType = COMPONENT_PATH + '.component'
		self._nodesWorld = []
		self._nodesShow = []
		self._nodesHide = []

	def register_kwargs(self):
		super(Component, self).register_kwargs()
		self._kwargs.update({'offsets': ['offsets', 1, naming.Type.offset],
						'ctrlSize': ['controlSize', 1, 'size'],
						'ctrlCol': ['controlColor', None, 'color'],
						'sub': ['subControl', True, 'sub']})
	
	def create_component(self):
		super(Component, self).create_component()
		'''
		create component node hierarchy
		
		component
			-- localGrp
				-- controlsGrp
				-- jointsGrp
				-- nodesShowGrp
				-- nodesHideGrp
			-- worldGrp
				-- nodesWorldGrp
		'''

		Namer = naming.Namer(type=naming.Type.component,
							 side=self._side,
							 description=self._des,
							 index=self._index)

		# create transforms
		attrDict = {}
		for trans in ['nodesHideGrp', 'nodesShowGrp',
					  'worldGrp', 'nodesWorldGrp']:
			Namer.type = trans
			transforms.create(Namer.name, lockHide=attributes.Attr.all)
			attrDict.update({'_'+trans: Namer.name})
		self._add_attr_from_dict(attrDict)

		# parent hierarchy
		cmds.parent(self._worldGrp, self._component)
		cmds.parent(self._nodesHideGrp, self._nodesShowGrp, self._localGrp)
		cmds.parent(self._nodesWorldGrp, self._worldGrp)

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

		attributes.add_attrs(self._component, ['rigNodesVis'], attributeType='long', 
							 range=[0,1], defaultValue=0, keyable=False, 
							 channelBox=True)
		attributes.add_attrs(self._component, 'componentType', attributeType='string',
							lock=True)
		cmds.addAttr(self._component, ln='outputMatrix', at='matrix', multi=True)
		
		# connect attrs
		attributes.connect_attrs(['rigNodesVis', 'rigNodesVis'], 
								 [self._nodesWorldGrp+'.v', self._nodesHideGrp+'.v'], 
								  driver=self._component)