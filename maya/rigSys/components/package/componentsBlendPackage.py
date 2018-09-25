# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)


# -- import maya lib
import maya.cmds as cmds

# -- import lib
import common.naming.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import rigging.joints as joints
import rigSys.core.componentsPackage as componentsPackage
import rigSys.core.space as space
# ---- import end ----

class ComponentsBlendPackage(componentsPackage.ComponentsPackage):
	"""componentsBlendPackage template"""
	def __init__(self, *args,**kwargs):
		super(ComponentsBlendPackage, self).__init__()
		self._rigComponentType = 'rigSys.components.package.componentsBlendPackage'

		kwargsDefault = {'components': {'value': {}, 'type': dict},
						 'defaultA': {'value': '', 'type': basestring},
						 'defaultB': {'value': '', 'type': basestring} }
		## components example
			#{Key name: 
			#  { 'componentType': module path,
			#	 'kwargs': kwargs,}
			#}
		self._registerAttributes(kwargsDefault)

	def _createComponent(self):		
		super(ComponentsBlendPackage, self)._createComponent()
		# set sub components visible
		cmds.setAttr('{}.subComponents'.format(self._rigComponent), 1)
		# create joints
		blendJnts = self.createJntsFromBpJnts(self._blueprintJoints, type = 'jnt', suffix = 'Blend', parent = self._jointsGrp)
		
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

			componentImport = __import__(componentType)
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
			if key in space.spaceDic:
				indexKey = space.spaceDic[key]
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
		multBlend = cmds.createNode('multDoubleLinear', 
									name = naming.Naming(type = 'multDoubleLinear',
														 side = self._side, 
														 part = '{}Blend'.format(self._part),
														 index = self._index).name)
		cmds.connectAttr('{}.blend'.format(blendCtrl), '{}.input1'.format(multBlend))
		cmds.setAttr('{}.input2'.format(multBlend), 0.1)
		rvsBlend = cmds.createNode('reverse',
									name = naming.Naming(type = 'reverse',
														 side = self._side, 
														 part = '{}Blend'.format(self._part),
														 index = self._index).name)
		cmds.connectAttr('{}.output'.format(multBlend), '{}.inputX'.format(rvsBlend))

		# control vis

		condBlend = cmds.createNode('condition', name = naming.Naming(type = 'condition',
														 side = self._side, 
														 part = '{}Blend'.format(self._part),
														 index = self._index).name)
		cmds.connectAttr('{}.output'.format(multBlend), '{}.firstTerm'.format(condBlend))
		cmds.setAttr('{}.secondTerm'.format(condBlend), 0.5, lock = True)
		cmds.setAttr('{}.operation'.format(condBlend), 4)
		cmds.connectAttr('{}.modeA'.format(blendCtrl), '{}.colorIfTrueR'.format(condBlend))
		cmds.connectAttr('{}.modeB'.format(blendCtrl), '{}.colorIfTrueB'.format(condBlend))

		for i, component in enumermate(subComponentNodes):
			NamingNode = naming.Naming(component)
			NamingNode.type = 'condition'
			NamingNode.part = '{}BlendCtrlVis'.format(NamingNode.part)
			condCtrlVis = cmds.createNode('condition', name = NamingNode.name)
			cmds.connectAttr('{}.outColorR'.format(condBlend), '{}.firstTerm'.format(condCtrlVis))
			cmds.setAttr('{}.secondTerm'.format(condCtrlVis), indexList[i], lock = True)
			cmds.setAttr('{}.colorIfTrueR'.format(condCtrlVis), 1, lock = True)
			cmds.setAttr('{}.colorIfFalseR'.format(condCtrlVis), 0, lock = True)
			NamingNode.type = 'multDoubleLinear'
			multVis = cmds.createNode('multDoubleLinear', name = NamingNode.name)
			cmds.connectAttr('{}.outColorR'.format(condCtrlVis), '{}.input1'.format(multVis))
			cmds.connectAttr('{}.controlsVis'.format(self._rigComponent), '{}.input2'.format(multVis))
			cmds.connectAttr('{}.output'.format(multVis), '{}.controlsVis'.format(component))
		
		# blend constraints
		for i in range(len(blendJnts)):
			NamingJnt = naming.Naming(blendJnts[i])

			constraintList = []
			for j, attr in enumerate(['Translate', 'Rotate', 'Scale']):
				# constraint node
				constraintType = ['pointConstraint', 'orientConstraint', 'scaleConstraint'][j]
				constraint = cmds.createNode(constraintType, 
								  name = naming.Naming(type = constraintType,
									  				   side = NamingJnt.side,
									  				   part = '{}Blend'.format(NamingJnt.part),
									  				   index = NamingJnt.index).name)
				constraintList.append(constraint)

				choiceList = []
				for m, mode in enumerate('AB'):
					# choice node
					choice = cmds.createNode('choice', 
									  name = naming.Naming(type = 'choice',
									  					   side = NamingJnt.side,
									  					   part = '{}Mode{}{}'.format(NamingJnt.part, mode, attr),
									  					   index = NamingJnt.index).name)
					choiceList.append(choice)

					# decomposeMatrix node
					decomposeMatrix = cmds.createNode('decomposeMatrix', 
									  name = naming.Naming(type = 'decomposeMatrix',
									  					   side = NamingJnt.side,
									  					   part = '{}Mode{}{}'.format(NamingJnt.part, mode, attr),
									  					   index = NamingJnt.index).name)
					cmds.connectAttr('{}.output'.format(choice), '{}.inputMatrix'.format(decomposeMatrix))

					# connect decompose matrix to constraint
					for axis in 'XYZ':
						cmds.connectAttr('{}.output{}{}'.format(decomposeMatrix, attr, axis), 
							'{}.target[{}].target{}{}'.format(constraint, m, attr, axis))

					# connect weight
					blendOutput = ['{}.outputX'.format(rvsBlend), '{}.output'.format(multBlend)][m]
					cmds.connectAttr(blendOutput,
						'{}.target[{}].targetWeight'.format(constraint, m))

					# conenct selector
					cmds.connectAttr('{}.mode{}'.format(blendCtrl, mode), '{}.selector'.format(choice))

				# feed each component joint matrix into choice node
				for n in range(len(indexList)):
					componentJnt = componentsJnts[n][i]
					NamingComposeMatrix = naming.NamingJnt(componentJnt)
					NamingComposeMatrix.type = 'composeMatrix'
					NamingComposeMatrix.part = '{}Blend{}'.format(NamingComposeMatrix.part, attr)
					composeMatrix = NamingComposeMatrix.name
					cmds.createNode('composeMatrix', name = composeMatrix)
					for axis in 'XYZ':
						cmds.connectAttr('{}.{}{}'.format(componentJnt, attr, axis), 
							'{}.input{}{}'.format(composeMatrix, attr, axis))
					cmds.connectAttr('{}.outputMatrix'.format(composeMatrix),
									'{}.input[{}]' %(choiceList[j], indexList[n]))

				# connect constraint node to blend joint
				for axis in 'XYZ':
					cmds.connectAttr('{}.constraint{}{}'.format(constraint, attr, axis), 
							'{}.{}{}'.format(blendJnts[i], attr, axis))

			# set orient constraint interpType
			cmds.setAttr('{}.interpType'.format(constraintList[1]), 2)

		# pass info
		self._joints += blendJnts
		self._controls += [blendCtrl]
		self._subComponentNodes = subComponentNodes

