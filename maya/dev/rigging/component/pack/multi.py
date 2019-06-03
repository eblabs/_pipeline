#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.files as files
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.common.hierarchy as hierarchy
import utils.common.nodeUtils as nodeUtils
import utils.rigging.joints as joints
import utils.rigging.controls as controls
import utils.rigging.constraints as constraints

# import pack
import pack
#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger, COMPONENT_PATH

#=================#
#      CLASS      #
#=================#

class Multi(pack.Pack):
	"""
	Multi component pack to combine multiple component as one pack
	(like fingers)

	This component is different with others, 
	the pack doesn't contain the info, 
	everything will be under a compound attr to query
	(thumb
		-- joints
		-- controls
		-- outputMatrix
	index
		-- joints
		-- controls
		-- outputMatrix)

	Args:
		component(str)
	Kwargs:
		side(str)
		description(str)
		index(int)
		parent(str)
		subComponents(dict): components as sub components
						  {Key name:
						  	{'componentType'(str): component path,
						  	 'kwargs'(dict): component kwargs}}
	Returns:
		Component(obj)
	"""
	def __init__(self, *arg, **kwargs):
		super(Multi, self).__init__(*arg, **kwargs)
		self._componentType = COMPONENT_PATH + '.multi'

	@property
	def keys(self):
		return self._keys
	
	def create_component(self):
		super(Multi, self).create_component()

		componentNodes = []
		componentObjs = []
		for key, componentInfo in self._subComponentsDict.iteritems():

			componentType = componentInfo['componentType']
			kwargs = componentInfo['kwargs']
			kwargs.update({'parent': self._subComponentsGrp,
						   'description': key,
						   'side': self._side,
						   'index': self._index})

			Component = self._get_component_build_obj(componentType, **kwargs)
			Component.create()

			componentNodes.append(Component.name)
			componentObjs.append(Component)
			attributes.connect_attrs(['inputMatrix', 'offsetMatrix', 
									  'jointsVis', 'controlsVis'],
									['inputMatrix', 'offsetMatrix',
									 'jointsVis', 'controlsVis'],
									driver=self._component, driven=Component.name)

		self._subComponents += componentNodes
		self._subComponentObjs = componentObjs

	def register_component_info(self):
		super(Multi, self).register_component_info()

		# add keys
		self._add_list_as_string_attr('subComponentsKey', self._subComponentsDict.keys())

		# add compound attrs
		# subComponentsInfo
		#	-- subComponentsInfo[0]
		# 		-- subComponentsJoints
		#   	-- subComponentsControls
		#   	-- subComponentsOutputMatrix
		#   	-- subComponentsName
		cmds.addAttr(self._component, ln='subComponentsInfo', at='compound', multi=True,
					 numberOfChildren=4)
		cmds.addAttr(self._component, ln='subComponentName', at='message', parent='subComponentsInfo')
		cmds.addAttr(self._component, ln='subComponentJoints', at='message', multi=True,
					 parent='subComponentsInfo')
		cmds.addAttr(self._component, ln='subComponentControls', at='message', multi=True,
					 parent='subComponentsInfo')
		cmds.addAttr(self._component, ln='subComponentOutputMatrix', at='matrix', multi=True,
					 parent='subComponentsInfo')

		# add compound attrs
		for i, Obj in enumerate(self._subComponentObjs):
			# name			
			cmds.connectAttr(Obj.name+'.message', 
					'{}.subComponentsInfo[{}].subComponentName'.format(self._component, i))
			
			# joints and outputMatrix
			for j, jnt in enumerate(Obj.joints):
				cmds.connectAttr(jnt+'.message', 
					'{}.subComponentsInfo[{}].subComponentJoints[{}]'.format(self._component, i, j))
				cmds.connectAttr(jnt+'.worldMatrix[0]', 
					'{}.subComponentsInfo[{}].subComponentOutputMatrix[{}]'.format(self._component, i, j))
			
			# controls
			for j, ctrl in enumerate(Obj.controls):
				cmds.connectAttr(ctrl+'.message', 
					'{}.subComponentsInfo[{}].subComponentControls[{}]'.format(self._component, i, j))
	
	def get_component_info(self, component):
		super(Multi, self).get_component_info(component)

		self._keys = self._get_string_attr_as_list('subComponentsKey')
		self.subComponents.keys = self._keys

		for key, Obj in zip(self._keys, self.subComponents.Components):
			self._add_obj_attr('subComponents.'+key, 
								{'name': Obj.name,
								 'joints': Obj.joints,
								 'controls': Obj.controls,
								 'outputMatrix': Obj.outputMatrix,
								 'outputMatrixAttr': Obj.outputMatrixAttr})