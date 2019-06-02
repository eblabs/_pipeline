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
from . import Logger, COMPONENT_PATH, CONFIG_PATH

SPACE_DICT = files.read_json_file(os.path.join(CONFIG_PATH, 'SPACE.cfg'))

#=================#
#      CLASS      #
#=================#

class Blend(pack.Pack):
	"""
	Blend multi component pack

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
		defaults(list): default components
	Returns:
		Component(obj)
	"""
	def __init__(self, *arg, **kwargs):
		super(Blend, self).__init__(*arg, **kwargs)
		self._componentType = COMPONENT_PATH + '.blend'
		self._suffix = 'Blend'

	def register_kwargs(self):
		super(Blend, self).register_kwargs()
		self._kwargs.update({'defaults': ['defaults', [], 'd']})

	def create_component(self):
		super(Blend, self).create_component()

		# create joints
		self._jnts = joints.create_on_hierarchy(self._bpJnts,
					 naming.Type.blueprintJoint, naming.Type.joint,
					 suffix=self._suffix, parent=self._jointsGrp)
		
		# create components
		blendCtrl = naming.Namer(type=naming.Type.control,
								 side=self._side,
								 description=self._des,
								 index=self._index).name

		componentNodes = []
		componentJnts = []

		indexCustom = 101
		enumName = ''
		
		for key, componentInfo in self._components.iteritems():
			componentType = componentInfo['componentType']
			if len(key) > 1:
				keySuffix = key[0].upper() + key[1:]
			else:
				keySuffix = key.title()
			if 'kwargs' not in componentInfo:
				componentInfo.update({'kwargs': {}})
			kwargs = componentInfo['kwargs']
			kwargs.update({'blueprintJoints': self._jnts,
						   'parent': self._subComponentsGrp,
						   'description': self._des + keySuffix,
						   'side': self._side,
						   'index': self._index,
						   })

			Component = self._get_component_build_obj(componentType, **kwargs)
			Component.create()

			componentNodes.append(Component.name)
			componentJnts.append(Component.joints)

			controls.add_ctrls_shape(blendCtrl, transform=Component.controls)

			attributes.connect_attrs(['inputMatrix', 'offsetMatrix'],
									['inputMatrix', 'offsetMatrix'],
									driver=self._component, driven=Component.name)

			if key in SPACE_DICT:
				indexKey = SPACE_DICT[key]
			else:
				indexKey = indexCustom
				indexCustom += 1
			self._components[key].update({'index': indexKey})
			enumName += '{}={}:'.format(key, indexKey)

		indexDefaults = []
		if self._defaults:
			for key in self._defaults:
				if key in self._components:
					indexDefaults.append(self._components[key]['index'])
		if not indexDefaults:
			indexDefaults = None

		# add attrs
		attributes.add_attrs(blendCtrl, ['modeA', 'modeB'],
							 attributeType='enum', defaultValue=indexDefaults,
							 enumName=enumName)
		cmds.addAttr(blendCtrl, ln='blend', at='float', min=0, max=1, keyable=True)
		rvsAttr = nodeUtils.equation('~{}.blend'.format(blendCtrl), side=self._side,
									 description=self._des, index=self._index)

		## control vis
		conditionAttr = nodeUtils.condition(blendCtrl+'.blend',
										0.5, blendCtrl+'.modeA',
										blendCtrl+'.modeB',
										side=self._side,
										description=self._des+'CtrlVis',
										index=self._index,
										operation='<')

		for key, cpnt in zip(self._components.keys(), componentNodes):
			
			if len(key) > 1:
				keySuffix = key[0].upper() + key[1:]
			else:
				keySuffix = key.title()

			conditionAttr_cpnt = nodeUtils.condition(conditionAttr[0],
													self._components[key]['index'],
													1, 0,
													side=self._side,
													description='{}{}CtrlVis'.format(self._des, 
																					 keySuffix),
													index=self._index)

			nodeUtils.equation('{}.controlsVis * {}'.format(self._component, conditionAttr_cpnt[0]),
															side=self._side,
															description='{}{}CtrlVis'.format(self._des, 
																					 keySuffix),
															index=self._index,
															attrs=cpnt+'.controlsVis')

		# blend constraint
		for i, jnt in enumerate(self._jnts):
			Namer = naming.Namer(jnt)
			choiceNodes = []
			for m in 'AB':
				choice = nodeUtils.node(type=naming.Type.choice,
										side=Namer.side,
										description='{}Blend{}'.format(Namer.description, m),
										index=Namer.index)
				cmds.connectAttr('{}.mode{}'.format(blendCtrl, m), choice+'.selector')
				choiceNodes.append(choice)

			# feed in all components joints matrix to choice
			for j, key in enumerate(self._components.keys()):
				attributes.connect_attrs(componentJnts[j][i]+'.matrix',
								 		 ['{}.input[{}]'.format(choiceNodes[0], 
								 		  self._components[key]['index']),
								 		  '{}.input[{}]'.format(choiceNodes[1], 
								 		  self._components[key]['index'])])

			constraints.matrix_blend_constraint([choiceNodes[0]+'.output',
												 choiceNodes[1]+'.output'], 
												 jnt, 
												 weights=[rvsAttr, blendCtrl+'.blend'])

		# pass info
		self._ctrls.append(blendCtrl)
		self._subComponents += componentNodes