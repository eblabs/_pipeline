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
import lib.common.naming.namingDict as namingDict
import lib.common.hierarchy as hierarchy
import lib.rigging.controls.controls as controls
import lib.rigging.joints as joints
# ---- import end ----

# -- import component
import rigSys.components.base.ikRPsolverComponent as ikRPsolverComponent
import rigSys.behaviors.fkChainBehavior as fkChainBehavior
# -- import end ----

class IkRPsolverPlusComponent(ikRPsolverComponent.IkRPsolverComponent):
	"""
	IkRPsolverPlusComponent

	create ik rp solver with one or two ik sc solver joints attached rig component,
	mainly used for arm and leg

	"""
	
	def __init__(self, *args,**kwargs):
		super(IkRPsolverPlusComponent, self).__init__(*args,**kwargs)

	def _registerDefaultKwargs(self):
		super(IkRPsolverPlusComponent, self)._registerDefaultKwargs()
		kwargs = {'blueprintReverseJoints': {'value': [], 'type': list},
				  'reverseJointsDescriptor': {'value': ['heel', 'toe', 'sideInn', 'sideOut', 'ball'],
						 					  'type': list}}
		self._kwargs.update(kwargs)
		self._kwargsRemove.append('ikSolver')

	def _setVariables(self):
		super(IkRPsolverPlusComponent, self)._setVariables()
		self._rigComponentType = 'rigSys.components.advance.ikRPsolverPlusComponent'
		self._reverseControls = []
		self._reverseJoints = []

	def _createComponent(self):
		if len(self._blueprintJoints) == 4:
			bpJointsSC = self._blueprintJoints[-2:]
			self._blueprintJoints = self._blueprintJoints[:-1]
			descriptor = ['Tip']
		else:
			bpJointsSC = self._blueprintJoints[-3:]
			self._blueprintJoints = self._blueprintJoints[:-2]
			descriptor = ['Roll', 'Tip']

		super(IkRPsolverPlusComponent, self)._createComponent()

		# create rest jnts
		ikJnts = joints.createOnHierarchy(bpJointsSC[1:], 
						namingDict.dNameConvension['type']['blueprintJoint'], 
						namingDict.dNameConvension['type']['joint'], 
						suffix = self._suffix, 
						parent = self._joints[-1], rotateOrder = False)
		ikRpTipJnt = self._joints[-1]
		ikJntsSC = [ikRpTipJnt] + ikJnts
		ikSCHandleList = []

		for i, jnt in enumerate(ikJntsSC[:-1]):
			ikSCHandle = naming.Naming(type = 'ikHandle', side = self._side, part = '{}{}IkSC'.format(self._part, descriptor[i]), index = self._index).name
			cmds.ikHandle(sj = jnt, ee = ikJntsSC[i+1], sol = 'ikSCsolver', name = ikSCHandle)
			ikSCHandleList.append(ikSCHandle)

		if len(ikSCHandleList) == 1:
			# no reverse setup, just use ik ctrl to control the sc handle
			p = cmds.listRelatives(self._ikHandles[0], p = True)[0]
			cmds.parent(ikSCHandleList[0], p)
		else:
			# setup reverse 
			# blueprint reverse structure
			# heel - toe - sideInn - sideOut - ball
			# reverse structure
			# ball - heel - toe - sideInn - sideOut - toeTap - toeTapEnd (delete)
			#                                       - ballRoll - ballRollEnd(delete)
			
			# duplicate joints
			rvsJntPartList = ['{}Twist'.format(self._reverseJointsDescriptor[-1]), 
						  	  '{}Roll'.format(self._reverseJointsDescriptor[0]), 
						  	  '{}Roll'.format(self._reverseJointsDescriptor[1]), 
						  	  self._reverseJointsDescriptor[2], 
						  	  self._reverseJointsDescriptor[3],
						  	  '{}Tap'.format(self._reverseJointsDescriptor[1]),
						  	  '{}Roll'.format(self._reverseJointsDescriptor[-1])]

			rvsBpJntList = [self._blueprintReverseJoints[-1],
							self._blueprintReverseJoints[0],
							self._blueprintReverseJoints[1],
							self._blueprintReverseJoints[2],
							self._blueprintReverseJoints[3],
							ikJntsSC[-2],
							ikJntsSC[-2]]

			rvsAttrList = ['ballTwist', 'heelRoll', 'toeRoll', 'sideInn', 'sideOut',
						   'toeTap', 'ballRoll']

			attrDict = {}
			for i in range(7):
				jnt = joints.createOnNode(rvsBpJntList[i], 
										  rvsBpJntList[i],
										  naming.Naming(type = 'reverseJoint',
										  				side = self._side,
										  				part = rvsJntPartList[i],
										  				index = self._index).name)
				attrDict.update({'_{}'.format(rvsAttrList[i]): jnt})

			self._addAttributeFromDict(attrDict)

			# orient joints
			txJnt = cmds.getAttr('{}.tx'.format(ikJntsSC[1]))
			if txJnt >= 0:
				aimVec = [1, 0, 0]
			else:
				aimVec = [-1, 0, 0]

			aimList = [[self._ballTwist, self._toeRoll],
					   [self._heelRoll, self._toeRoll],
					   [self._toeRoll, self._heelRoll],
					   [self._toeTap, ikJntsSC[-1]],
					   [self._ballRoll, ikJntsSC[0]]]

			for jntList in aimList:
				cmds.delete(cmds.aimConstraint(jntList[1], jntList[0], aimVector = aimVec, 
												upVector = [0,1,0], worldUpType = 'objectrotation', 
												worldUpObject = ikJntsSC[1]))
				cmds.makeIdentity(jntList[0], apply = True, t = 1, r = 1, s = 1)

			aimList = [[self._sideInn, self._sideOut],
					   [self._sideOut, self._sideInn]]

			for jntList in aimList:
				cmds.delete(cmds.aimConstraint(jntList[1], jntList[0], aimVector = aimVec, 
												upVector = [0,1,0], worldUpType = 'objectrotation', 
												worldUpObject = self._ballTwist))
				cmds.makeIdentity(jntList[0], apply = True, t = 1, r = 1, s = 1)

			# parent joints
			p = cmds.listRelatives(self._ikHandles[0], p = True)[0]
			rvsJntList = [self._toeTap, self._sideInn, self._sideOut, 
						  self._toeRoll, self._heelRoll, self._ballTwist]
			rvsRoot = hierarchy.connectChain(rvsJntList)
			cmds.parent(rvsRoot, self._nodesLocal[-1])
			cmds.parent(self._ballRoll, self._sideInn)
			
			ControlIk = controls.Control(self._controls[-1])

			rvsJntList.reverse()

			kwargs = {'side': self._side,
					  'part': self._part,
					  'index': self._index,
					  'blueprintJoints': rvsJntList,
					  'stacks': self._stacks,
					  'jointSuffix': '',
					  'createJoints': False,
					  'lockHide': ['tx', 'ty', 'tz', 'sx', 'sy', 'sz'],
					  'controlShape': 'rotate',

				  	  'controlsGrp': ControlIk.output}
			
			RvsFootRig = fkChainBehavior.FkChainBehavior(**kwargs)
			RvsFootRig.create()

			self._reverseControls += RvsFootRig._controls
			self._reverseJoints += RvsFootRig._joints

			ControlSideInn = controls.Control(RvsFootRig._controls[-2])
			kwargs.update({'blueprintJoints': [self._ballRoll],
						   'controlsGrp': ControlSideInn.output})

			RvsFootRig = fkChainBehavior.FkChainBehavior(**kwargs)
			RvsFootRig.create()

			self._reverseControls += RvsFootRig._controls
			self._reverseJoints += RvsFootRig._joints

			# parent ik handles
			cmds.parent(ikSCHandleList[0], self._ikHandles[0], self._ballRoll)
			cmds.parent(ikSCHandleList[1], self._toeTap)

			# lock hide attrs
			lockHide = [['rx', 'ry'], ['rx', 'ry'], ['rx', 'rz']]
			controlList = [self._reverseControls[-3], 
						   self._reverseControls[-4], 
						   self._reverseControls[0]]
			for ctrlInfo in zip(lockHide, controlList):
				Control = controls.Control(ctrlInfo[1])
				Control.lockHideAttrs(ctrlInfo[0])

			# pass info
			self._controls += self._reverseControls

		# pass info
		self._joints += ikJnts
		self._ikHandles += ikSCHandleList

	def _writeRigComponentInfo(self):
		super(IkRPsolverPlusComponent, self)._writeRigComponentInfo()

		# reverse controls
		self._addListAsStringAttr('reverseControls', self._reverseControls)

	def _getRigComponentInfo(self):
		super(IkRPsolverPlusComponent, self)._getRigComponentInfo()

		# get reverse controls
		self._reverseControls = self._getStringAttrAsList('reverseControls')




