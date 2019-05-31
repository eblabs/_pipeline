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
class Pack(object):
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
		components(dict): components as sub components
						  {Key name:
						  	{'componentType'(str): component path,
						  	 'kwargs'(dict): component kwargs}}
	Returns:
		Component(obj)
	"""
	def __init__(self, *arg, **kwargs):
		super(Pack, self).__init__()
		self._componentType = COMPONENT_PATH + '.pack'
		self._subComponents = []

	def register_kwargs(self):
		super(Pack, self).register_kwargs()
		self._kwargs.update({'components': ['components', {}, 
								naming.Type.component]})

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
		self._subComponents = transforms.create(Namer.name, lockHide=attributes.Attr.all, 
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
		attributes.connect_attrs(['subComponentsVis'], [self._subComponents+'.v'], 
								  driver=self._component)

	def register_component_info(self):
		super(Pack, self).register_component_info()

		# sub components
		for i, cpnt in enumerate(self._subComponents):
			cmds.connectAttr(cpnt+'.message',
							 '{}.subComponents[{}]'.format(self._component, i), f=True)

	def get_component_info(self, component):
		super(Pack, self).get_component_info()

		self._subComponents = self._get_attr(self._component+'.subComponents', 
											 message=True, asList=True)
		subComponents = {'names': self._subComponents,
						 'Components': []}
		for i, cpnt in enumerate(self._subComponents):
			Obj = self._get_component_obj(cpnt)
			subComponents['Components'].append(Obj)

		self._add_obj_attr('subComponents', subComponents)

	def _get_component_obj(self, component):
		componentType = cmds.getAttr(cpnt+'.componentType')
		componentFuc = componentType.split('.')[-1]
		componentFuc = componentFuc[0].upper() + componentFuc[1:]
		componentImport = import_module(componentType)
		Obj = getattr(componentImport, componentFuc)(cpnt)
		return Obj

#=================#
#  SUB FUNCTION   #
#=================#
def import_module(path):
	components = path.split('.')
	if len(components) > 1:
		path = ''
		for c in components:
			path += '{}.'.format(c)
		module = __import__(path[:-1], fromlist = [components[-1]])
	else:
		module = __import__(path)
	return module