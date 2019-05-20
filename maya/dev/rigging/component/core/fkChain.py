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

## import component
import component

## import behavior
import dev.rigging.behavior.fkChain as fkChainBhv

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger, COMPONENT_PATH

#=================#
#      CLASS      #
#=================#
class FkChain(object):
	"""
	fk chain component base class
	
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
		lockHide(list): lock and hide controls channels
	Returns:
		Component(obj)
	"""
	def __init__(self, *arg, **kwargs):
		super(FkChain, self).__init__(*arg, **kwargs)
		self._componentType = COMPONENT_PATH + '.fkChain'
		self._suffix = 'Fk'

	def register_kwargs(self):
		super(FkChain, self).register_kwargs()
		self._kwargs.update({'lockHide': ['lockHide', attributes.Attr.scale, 'lh']})

	def create_component(self):
		super(FkChain, self).create_component()

		kwargs = {'side': self._side,
				  'description': self._des,
				  'index': self._index,
				  'blueprintJoints': self._bpJnts,
				  'jointSuffix': self._suffix,
				  'offsets': self._offsets,
				  'controlSize': self._ctrlSize,
				  'controlColor': self._ctrlCol,
				  'subControl': self._sub,
				  'lockHide': self._lockHide,

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesLocalGrp': self._nodesLocalGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp}

		Behavior = fkChainBhv.FkChain(**kwargs)
		Behavior.create()

		# pass info
		self._jnts += Behavior._jnts
		self._ctrls += Behavior._ctrls
