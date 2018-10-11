# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.naming.naming as naming
import lib.common.attributes as attributes
import lib.common.nodeUtils as nodeUtils
import lib.common.packages as packages
import lib.rigging.constraints as constraints
import lib.rigging.joints as joints
import lib.rigging.controls.controls as controls
# ---- import end ----

# -- import component
import rigSys.core.componentsPackage as componentsPackage
import rigSys.core.space as space
reload(componentsPackage)
# ---- import end ----

class ComponentsBlendPackage(componentsPackage.ComponentsPackage):
	"""componentsBlendPackage template"""
	def __init__(self, *args,**kwargs):
		super(ComponentsBlendPackage, self).__init__(*args,**kwargs)
		
	def _registerDefaultKwargs(self):
		super(ComponentsBlendPackage, self)._registerDefaultKwargs()
		kwargs = {'components': {'value': {}, 'type': dict},
				  'defaultA': {'value': '', 'type': basestring},
				  'defaultB': {'value': '', 'type': basestring} }
		## components example
			#{Key name: 
			#  { 'componentType': module path,
			#	 'kwargs': kwargs,}
			#}
		self._kwargs.update(kwargs)

	def _setVariables(self):
		super(ComponentsBlendPackage, self)._setVariables()
		self._suffix = 'Blend'
		self._rigComponentType = 'rigSys.components.package.componentsBlendPackage'

	def _createComponent(self):		
		super(ComponentsBlendPackage, self)._createComponent()
		# set sub components visible
		cmds.setAttr('{}.subComponents'.format(self._rigComponent), 1)
		# create joints
		bpJntType = naming.getName('blueprintJoint', 'type', returnType = 'shortName')
		jntType = naming.getName('joint', 'type', returnType = 'shortName')
		self._joints = joints.createOnHierarchy(self._blueprintJoints, 
						bpJntType, jntType, suffix = self._suffix, parent = self._jointsGrp)

		# create rig components
		componentsJnts = []
		blendCtrl = naming.Naming(type = 'control', side = self._side, 
									part = '{}Blend'.format(self._part), index = self._index).name
		subComponentNodes = []

		for key in self._components.keys():
			componentType = self._components[key]['componentType']
			componentFunc = componentType.split('.')[-1]
			componentFunc = componentFunc[0].upper() + componentFunc[1:]
			kwargs = self._components[key]['kwargs']
			kwargs.update({'blueprintJoints': self._blueprintJoints,
						  'parent': self._subComponents,
						  'part': self._part + key[0].upper() + key[1:],
						  'side': self._side,
						  'index': self._index})

			componentImport = packages.importModule(componentType)
			Limb = getattr(componentImport, componentFunc)(**kwargs)
			Limb.create()

			componentsJnts.append(Limb.joints.list)

			controls.addCtrlShape(Limb.controls.list, asCtrl = blendCtrl)

			for attr in ['jointsVis', 'rigNodesVis']:
				cmds.connectAttr('{}.{}'.format(self._rigComponent, attr),
								 '{}.{}'.format(Limb._rigComponent, attr),)

			subComponentNodes.append(Limb._rigComponent)

		# add attrs
		indexList = []
		indexCustom = 100
		enumName = ''
		for key in self._components.keys():
			if key in space.spaceDict:
				indexKey = space.spaceDict[key]
			else:
				indexKey = indexCustom
				indexCustom += 1
			indexList.append(indexKey)
			enumName += '{}={}:'.format(key, indexKey)

		indexDefault = []
		for default in [self._defaultA, self._defaultB]:
			if default in self._components.keys():
				index = indexList[self._components.keys().index(default)]
			else:
				index = indexList[0]
			indexDefault.append(index)

		attributes.addAttrs(blendCtrl, ['modeA', 'modeB'], attributeType = 'enum', 
							defaultValue = indexDefault, enumName = enumName[:-1])
		cmds.addAttr(blendCtrl, ln = 'blend', at = 'float', min = 0, max = 10, keyable = True)
		multBlend = nodeUtils.create(type = 'multDoubleLinear',
								 side = self._side, 
								 part = '{}Blend'.format(self._part),
								 index = self._index)
		cmds.connectAttr('{}.blend'.format(blendCtrl), '{}.input1'.format(multBlend))
		cmds.setAttr('{}.input2'.format(multBlend), 0.1)
		rvsBlend = nodeUtils.create(type = 'reverse',
								side = self._side, 
								part = '{}Blend'.format(self._part),
								index = self._index)
		cmds.connectAttr('{}.output'.format(multBlend), '{}.inputX'.format(rvsBlend))

		# control vis

		condBlend = nodeUtils.create(type = 'condition',
								 side = self._side, 
								 part = '{}Blend'.format(self._part),
								 index = self._index)
		cmds.connectAttr('{}.output'.format(multBlend), '{}.firstTerm'.format(condBlend))
		cmds.setAttr('{}.secondTerm'.format(condBlend), 0.5, lock = True)
		cmds.setAttr('{}.operation'.format(condBlend), 4)
		cmds.connectAttr('{}.modeA'.format(blendCtrl), '{}.colorIfTrueR'.format(condBlend))
		cmds.connectAttr('{}.modeB'.format(blendCtrl), '{}.colorIfFalseR'.format(condBlend))

		for i, component in enumerate(subComponentNodes):
			NamingNode = naming.Naming(component)
			condCtrlVis = nodeUtils.create(type = 'condition',
									   side = NamingNode.side,
									   part = '{}BlendCtrlVis'.format(NamingNode.part),
									   index = NamingNode.index)
			cmds.connectAttr('{}.outColorR'.format(condBlend), '{}.firstTerm'.format(condCtrlVis))
			cmds.setAttr('{}.secondTerm'.format(condCtrlVis), indexList[i], lock = True)
			cmds.setAttr('{}.colorIfTrueR'.format(condCtrlVis), 1, lock = True)
			cmds.setAttr('{}.colorIfFalseR'.format(condCtrlVis), 0, lock = True)
			NamingNode.type = 'multDoubleLinear'
			multVis = nodeUtils.create(type = 'multDoubleLinear',
								   side = NamingNode.side,
								   part = '{}BlendCtrlVis'.format(NamingNode.part),
								   index = NamingNode.index)
			cmds.connectAttr('{}.outColorR'.format(condCtrlVis), '{}.input1'.format(multVis))
			cmds.connectAttr('{}.controlsVis'.format(self._rigComponent), '{}.input2'.format(multVis))
			cmds.connectAttr('{}.output'.format(multVis), '{}.controlsVis'.format(component))
		
		# blend constraints
		for i in range(len(self._joints)):
			NamingJnt = naming.Naming(self._joints[i])

			attrType = ['Translate', 'Rotate', 'Scale']
			
			for j, attr in enumerate(attrType):
				choiceList = []
				inputMatrixList = []
				for m, mode in enumerate(['A', 'B']):
					choice = nodeUtils.create(type = 'choice',
									  	  side = NamingJnt.side,
									  	  part = '{}Mode{}{}'.format(NamingJnt.part, mode, attr),
									  	  index = NamingJnt.index)

					cmds.connectAttr('{}.mode{}'.format(blendCtrl, mode), '{}.selector'.format(choice))

					choiceList.append(choice)
					inputMatrixList.append('{}.output'.format(choice))

				# feed all components matrix
				for n in range(len(indexList)):
					componentJnt = componentsJnts[n][i]
					NamingComposeMatrix = naming.Naming(componentJnt)
					composeMatrix = nodeUtils.create(type = 'composeMatrix',
												 side = NamingComposeMatrix.side,
												 part = '{}Blend{}'.format(NamingComposeMatrix.part, attr),
												 index = NamingComposeMatrix.index)
					for axis in 'XYZ':
						cmds.connectAttr('{}.{}{}'.format(componentJnt, attr.lower(), axis), 
							'{}.input{}{}'.format(composeMatrix, attr, axis))
					cmds.connectAttr('{}.outputMatrix'.format(composeMatrix),
									'{}.input[{}]'.format(choiceList[0], indexList[n]))
					cmds.connectAttr('{}.outputMatrix'.format(composeMatrix),
									'{}.input[{}]'.format(choiceList[1], indexList[n]))

				translate = (attr == attrType[0])
				rotate = (attr == attrType[1])
				scale = (attr == attrType[2])

				constraints.constraintBlend(inputMatrixList, self._joints[i], 
						weightList = ['{}.outputX'.format(rvsBlend), '{}.output'.format(multBlend)], 
						translate = translate, rotate = rotate, scale = scale)

		# pass info
		self._controls.append(blendCtrl)
		self._subComponentNodes = subComponentNodes

