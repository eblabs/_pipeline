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
class Pack(base.Base):
	"""
	Pack base class

	Args:
		component(str)
	Kwargs:
		side(str)
		description(str)
		index(int)
		parent(str)
		blueprintJoints(list)
		subComponents(dict): components as sub components
						  {Key name:
						  	{'componentType'(str): component path,
						  	 'kwargs'(dict): component kwargs}}
	Returns:
		Component(obj)
	"""
	def __init__(self, *arg, **kwargs):
		super(Pack, self).__init__(*arg, **kwargs)
		self._componentType = COMPONENT_PATH + '.pack'
		self._subComponents = []

	def register_kwargs(self):
		super(Pack, self).register_kwargs()
		self._kwargs.update({'subComponentsDict': ['subComponents', {}, 
								naming.Type.subComponentsGrp]})

	def create_component(self):
		super(Pack, self).create_component()
		'''
		create pack node hierarchy
		
		component
			-- localGrp
				-- controlsGrp
				-- jointsGrp
			-- subComponentsGrp
		'''
		Namer = naming.Namer(type=naming.Type.subComponentsGrp,
							 side=self._side,
							 description=self._des,
							 index=self._index)

		# create transforms
		self._subComponentsGrp = transforms.create(Namer.name, lockHide=attributes.Attr.all, 
						  						parent=self._component)
		# add attrs
		# input matrix: input connection from other component
		# offset matrix: offset from the input to the current component
		# inputComponent: message info to get input component name
		# controls: message info to get all the controllers' names
		# joints: message info to get all the joints' names
		# controlsVis: controls visibility switch
		# jointsVis: joints visibility switch
		# subComponentsVis: sub components visibility switch
		# componentType: component class type to get the node wrapped as object
		# outputMatrix: joints' output matrices

		attributes.add_attrs(self._component, ['subComponentsVis'], attributeType='long', 
							 range=[0,1], defaultValue=1, keyable=False, 
							 channelBox=True)

		cmds.addAttr(self._component, ln='subComponents', at='message', multi=True)
		
		# connect attrs
		attributes.connect_attrs(['subComponentsVis'], [self._subComponentsGrp+'.v'], 
								  driver=self._component)

	def register_component_info(self):
		super(Pack, self).register_component_info()

		# sub components
		for i, cpnt in enumerate(self._subComponents):
			cmds.connectAttr(cpnt+'.message',
							 '{}.subComponents[{}]'.format(self._component, i), f=True)

	def get_component_info(self, component):
		super(Pack, self).get_component_info(component)

		self._subComponents = self._get_attr(self._component+'.subComponents', 
											 message=True, asList=True)
		subComponents = {'names': self._subComponents,
						 'Components': []}
		for i, cpnt in enumerate(self._subComponents):
			Obj = self._get_component_info_obj(cpnt)
			subComponents['Components'].append(Obj)

		self._add_obj_attr('subComponents', subComponents)

	def _get_component_info_obj(self, component):
		componentType = cmds.getAttr(component+'.componentType')
		componentImport, componentFunc = import_module(componentType)
		Obj = getattr(componentImport, componentFunc)(component)
		return Obj

	def _get_component_build_obj(self, componentType, **kwargs):
		componentImport, componentFunc = import_module(componentType)
		Obj = getattr(componentImport, componentFunc)(**kwargs)
		return Obj

#=================#
#  SUB FUNCTION   #
#=================#
def import_module(path):
	components = path.split('.')
	func = components[-1][0].upper() + components[-1][1:]
	if len(components) > 1:
		path = ''
		for c in components:
			path += '{}.'.format(c)
		module = __import__(path[:-1], fromlist = [components[-1]])
	else:
		module = __import__(path)
	return module, func