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
import common.hierarchy as hierarchy
import rigging.control.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# -- import component
import rigSys.modules.base.ikRPsolverComponent as ikRPsolverComponent
# -- import end ----

class IkRPsolverPlusComponent(ikRPsolverComponent.IkRPsolverComponent):
	"""
	IkRPsolverPlusComponent

	create ik rp solver with one or two ik sc solver joints attached rig component,
	mainly used for arm and leg

	"""
	_reverseControls = []
	def __init__(self, *args,**kwargs):
		super(IkRPsolverPlusComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.modules.advance.ikRPsolverPlusComponent'

		kwargsDefault = {'blueprintReverseJoints': {'value': [], 'type': 'list'}
						 'reverseJointsDescriptor': {'value': ['heel', 'toe', 'sideInn', 'sideOut', 'ball'],
						 							 'type': 'list'}}
		self._registerAttributes(kwargsDefault)

	def _createRigComponent(self):
		if len(self._blueprintJoints) == 4:
			bpJointsSC = self._blueprintJoints[-2:]
			self._blueprintJoints = self._blueprintJoints[:-2]
			descriptor = ['Tip']
		else:
			bpJointsSC = self._blueprintJoints[-3:]
			self._blueprintJoints = self._blueprintJoints[:-3]
			descriptor = ['Roll', 'Tip']

		super(IkRPsolverPlusComponent, self)._createRigComponent()

		# create rest jnts
		ikJnts = self.createJntsFromBpJnts(bpJointsSC[1:], type = 'jnt', suffix = 'Ik', parent = self._joints[-1])
		ikRpTipJnt = self._joints[-1]
		ikJntsSC = [ikRpTipJnt] + ikJnts
		ikSCHandleList = []

		for i, jnt in enumerate(ikJntsSC[:-1]):
			ikSCHandle = naming.Naming(type = 'ikHandle', side = self._side, sPart = '{}{}Ik'.format(self._part, descriptor[i]), iIndex = self._index).name
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

			dicAttr = {}
			for i in range(7):
				jnt = joints.createOnNode(rvsBpJntList[i], 
										  rvsBpJntList[i],
										  naming.Naming(type = 'reverseJoint',
										  				side = self._side,
										  				part = rvsJntPartList[i],
										  				index = self._index).name)
				dicAttr.update({'_{}'.format(rvsAttrList[i]): jnt})

			self._addAttributeFromDict(dicAttr)

			# orient joints
			txJnt = cmds.getAttr('{}.tx'.format(ikJntsSC[1]))
			if txJnt >= 0:
				aimVec = [1, 0, 0]
			else:
				aimVec = [-1, 0, 0]

			aimList = [[self._ballTwist, self._toeRoll],
					   [self._heelRoll, self._toeRoll],
					   [self._toeRoll, self._heelRoll],
					   [self._sideInn, self._sideOut],
					   [self._sideOut, self._sideInn],
					   [self._toeTap, ikJntsSC[-1]],
					   [self._ballRoll, ikJntsSC[0]]]

			for jntList in aimList:
				cmds.delete(cmds.aimConstraint(jntList[1], jntList[0], aimVector = aimVec, 
												upVector = [0,1,0], worldUpType = 'objectrotation', 
												worldUpObject = ikJntsSC[1]))
				cmds.makeIdentity(jntList[0], apply = True, t = 1, r = 1, s = 1)

			# parent joints
			p = cmds.listRelatives(self._ikHandles[0], p = True)[0]
			rvsJntList = [self._toeTap, self._sideInn, self._sideOut, 
						  self._toeRoll, self._heelRoll, self._ballTwist]
			rvsRoot = hierarchy.connectChain(rvsJntList)
			cmds.parent(self._ballRoll, self._sideInn)
			cmds.parent(rvsRoot, p)

			# parent ik handles
			cmds.parent(ikSCHandleList[0], self._ballRoll)
			cmds.parent(ikSCHandleList[1], self._toeRoll)

			# create controls for rvs
			rvsControls = []
			ControlParent = controls.Control(self._controls[-1])
			for jnt in rvsJntList.reverse():
				NamingJnt = naming.Naming(jnt)
				Control = controls.create(NamingJnt.part, side = NamingJnt.side,
										  index = NamingJnt.index, stacks = self._stacks, 
										  parent = ControlParent.output, posParent = jnt, 
										  lockHide = ['tx', 'ty', 'tz', 'sx', 'sy', 'sz'])
				constraints.matrixConnect(Control.name, matrixLocalAttr, jnt, force = True, 
										  skipTranslate = ['x', 'y', 'z'], skipScale=['x', 'y', 'z'],
										  quatToEuler = False)
				ControlParent = Control
				rvsControls.append(Control.name)

			ControlParent = controls.Control(rvsControls[-2])
			NamingJnt = naming.Naming(self._ballRoll)
			Control = controls.create(NamingJnt.part, side = NamingJnt.side,
									  index = NamingJnt.index, stacks = self._stacks, 
									  parent = ControlParent.output, posParent = jnt, 
									  lockHide = ['tx', 'ty', 'tz', 'sx', 'sy', 'sz'])
			constraints.matrixConnect(Control.name, matrixLocalAttr, self._ballRoll, force = True, 
									  skipTranslate = ['x', 'y', 'z'], skipScale=['x', 'y', 'z'],
									  quatToEuler = False)

			rvsControls.append(Control.name)

			# lock hide attrs
			lockHide = [['rx', 'ry'], ['rx', 'ry'], ['rx', 'rz']]
			for i, ctrl in enumerate([rvsControls[-3], rvsControls[-4], rvsControls[0]]):
				Control = controls.Control(rvsControls)
				Control.lockHideAttrs(lockHide[i])

			# pass info
			self._controls += rvsControls
			self._reverseControls += rvsControls

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
		self._reverseControls = self.getListFromStringAttr('{}.reverseControls'.format(self._rigComponent))




