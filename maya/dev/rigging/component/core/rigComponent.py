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
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.common.hierarchy as hierarchy
import utils.common.nodeUtils as nodeUtils
import constraints
#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#

class RigComponent(object):
	"""RigComponent base class"""
	def __init__(self, *arg, **kwargs):
		pass

	def create(self):
		'''
		create rig component
		'''
		pass

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
			attrDict.update({trans: Namer.name})
		self._add_attr_from_dict(attrDict)

		# parent hierarchy
		hierarchy.parent(self.rigComponent, self.parent)
		cmds.parent(self.rigLocalGrp, self.rigWorldGrp, self.subComponentsGrp, self.rigComponent)
		cmds.parent(self.controlsGrp, self.jointsGrp, self.nodesLocalGrp, self.rigLocalGrp)
		cmds.parent(self.nodesHideGrp, self.nodesShowGrp, self.rigWorldGrp)

		# inheritsTransform
		cmds.setAttr(self.rigWorldGrp+'.inheritsTransform', 0)
		attributes.set_attrs([self.nodesLocalGrp+'.v', self.nodesHideGrp+'.v'], 0)

		# add attrs
		attributes.add_attr(self.rigComponent, ['inputMatrix', 'offsetMatrix'],
							attributeType='matrix', lock=True)
		cmds.addAttr(self.rigComponent, ln='inputComponent', at='message')
		attributes.add_attr(self.rigComponent, ['controls', 'joints'],
							attributeType='message', multi=True)
		attributes.add_attr(self.rigComponent, ['controlsVis', 'jointsVis', 
												'rigNodesVis', 'subComponentsVis'],
							attributeType='long', minValue=0, maxValue=1, 
							defaultValue=[1,0,0,1], keyable=False, channelBox=True)
		attributes.add_attr(self.rigComponent, 'componentType', attributeType='string',
							lock=True)
		# connect attrs
		attributes.connect_attrs(['controlsVis', 'jointsVis', 'rigNodesVis', 
								  'rigNodesVis', 'subComponentsVis'], 
								 [self.controlsGrp+'.v', self.jointsGrp+'.v',
								  self.rigLocalGrp+'.v', self.nodesHideGrp+'.v',
								  self.subComponentsGrp+'.v'], driver=self.rigComponent)

		# mult matrix
		multMatrix = nodeUtils.mult_matrix([self.rigComponent+'.inputMatrix',
											self.rigComponent+'.offsetMatrix'],
										   side=self._side, description=self._des,
										   index=self._index)

		constraints.matrix_connect(multMatrix+'.matrixSum', self.rigLocalGrp)


	def _add_attr_from_dict(attrDict):
		'''
		add class attributes from given dictionary
		'''
		for key, val in attrDict.iteritems():
			setattr(self, key, val)