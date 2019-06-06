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
import dev.rigging.behavior.rotatePlaneIk as rotatePlaneIkBhv

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger, COMPONENT_PATH

#=================#
#      CLASS      #
#=================#
class RotatePlaneIk(component.Component):
	"""
	rotate plane ik component base class
	
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
		ikType(str): rp (spring is not availble due to maya issue)
		blueprintControl(str): control blueprint position
		poleVectorDistance(float)
		singleChainIk(int)[0]: if need to set some joints as single chain ik
						like ik leg
						it will define the number of joints going to be
						set to scIk, maxium is 2
		reverseJoints(list): blueprint of the reverse joints
								 structure: [heel, toe, sideInn, sideOut, ball]
		reverseDescription(list): each reverse joint position's description
	Returns:
		Component(obj)
	"""
	def __init__(self, *arg, **kwargs):
		super(RotatePlaneIk, self).__init__(*arg, **kwargs)
		self._componentType = COMPONENT_PATH + '.singleChainIk'
		self._suffix = self._ikType.title()
		self._iks = []
		self._rvsCtrls = []

	def register_kwargs(self):
		super(RotatePlaneIk, self).register_kwargs()
		self._kwargs.update({'ikType': ['ikType', 'rp'],
							 'bpCtrl': ['blueprintControl', '', 'bpCtrl'],
							 'pvDis': ['poleVectorDistance', 1, 'pvDis'],
							 'sc': ['singleChainIk', 0, 'sc'],
							 'rvsJnts': ['reverseJoints', [], 'rvsJnts'],
							 'rvsDes': ['reverseDescription', ['heel', 'toe', 
							 			'sideInn', 'sideOut', 'ball'], 'rvsDes']})

	def create_component(self):
		super(RotatePlaneIk, self).create_component()

		kwargs = {'side': self._side,
				  'description': self._des,
				  'index': self._index,
				  'blueprintJoints': self._bpJnts,
				  'jointSuffix': self._suffix,
				  'offsets': self._offsets,
				  'controlSize': self._ctrlSize,
				  'controlColor': self._ctrlCol,
				  'subControl': self._sub,
				  'ikType': self._ikType,
				  'blueprintControl': self._bpCtrl,
				  'poleVectorDistance': self._pvDis,
				  'singleChainIk': self._sc,
				  'reverseJoints': self._rvsJnts,

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp,
				  'nodesWorldGrp': self._nodesWorldGrp}

		Behavior = rotatePlaneIkBhv.RotatePlaneIk(**kwargs)
		Behavior.create()

		# pass info
		self._jnts += Behavior._jnts
		self._ctrls += Behavior._ctrls
		self._iks += Behavior._iks
		self._rvsCtrls += Behavior._rvsCtrls
		self._nodesShow += Behavior._nodesShow
		self._nodesHide += Behavior._nodesHide

		# connect vis for guide line
		attributes.connect_attrs(self._component+'.controlsVis',
								 self._nodesShow[0]+'.v')
