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
import common.nodes as nodes
import rigging.control.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# -- import component
import components.base.ikSplineSolverComponent as ikSplineSolverComponent
# -- import end ----

class FkDriveIkSplineSolverComponent(ikSplineSolverComponent.IkSplineSolverComponent):
	"""
	FkDriveIkSplineSolverComponent

	create fk drive ik spline solver component
	mainly used for spine rig

	"""
	_fkControls = []
	_fkReverseControls = []
	def __init__(self, *args,**kwargs):
		super(FkDriveIkSplineSolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.advance.fkDriveIkSplineSolverComponent'

		kwargsDefault = {'blueprintFkControls': {'value': [], 'type': list},
						 'reverseFk': {'value': False, 'type': bool}}
		self._registerAttributes(kwargsDefault)

	def _createComponent(self):
		super(FkDriveIkSplineSolverComponent, self)._createComponent()

		if self._blueprintFkControls:

			ikVisCtrl = self._ikControls[-1]

			blueprintControls = [self._blueprintFkControls]

			if self._reverseFk:
				blueprintControlsRvs = self._blueprintFkControls
				blueprintControlsRvs.reverse()
				blueprintControls.append(blueprintControlsRvs)

			for i, bpCtrlList in enumerate(blueprintControls):
				fkControllist = [self._fkControls, self._fkReverseControls][i]

				visAttr = ['fkControlsVis', 'fkReverseVis'][i]
				attributes.addAttrs(ikVisCtrl, visAttr, attributeType='long', 
					minValue=0, maxValue=1, defaultValue=0, keyable=False, channelBox=True)

				ctrlParent = self._controlsGrp
				partSuffix = ['', 'Rvs'][i]
				ControlIk = controls.Control([self._ikControls[-2], self._ikControls[0]][i])
				for bpCtrl in bpCtrlList:
					NamingNode = naming.Naming(bpCtrl)
					ControlFk = controls.create(NamingNode.part + partSuffix,
												NamingNode.side,
												NamingNode.index,
												stacks = self._stacks, 
												parent = ctrlParent, 
												posParent = bpCtrl,
												lockHide=['sx', 'sy', 'sz'])
					cmds.connectAttr('{}.{}'.format(ikVisCtrl, visAttr), '{}.v'.format(ControlFk.zero))
					ctrlParent = ControlFk.output
					fkControllist.append(ControlFk.name)
				
				controls.addCtrlShape(fkControllist, asCtrl = ikVisCtrl)

				multMatrix = nodes.create(type = 'multMatrix', side = ControlIk.side,
										  part = '{}FkDriver'.format(ControlIk.part),
										  index = ControlIk.index)
				cmds.connectAttr('{}.worldMatrix[0]'.format(ctrlParent), 
								 '{}.matrixIn[0]'.format(multMatrix))
				cmds.connectAttr('{}.worldInverseMatrix[0]'.format(self._controlsGrp), 
								 '{}.matrixIn[1]'.format(multMatrix))

				constraints.matrixConnect(multMatrix, 'matrixSum', ControlIk.passer, offset = True, 
									skipScale = ['x', 'y', 'z'], force = True, quatToEuler = False)

			# pass info
			self._controls += (self._fkControls + self._fkReverseControls)

	def _writeRigComponentInfo(self):
		super(FkDriveIkSplineSolverComponent, self)._writeRigComponentInfo()

		# fk controls
		self._addListAsStringAttr('fkControls', self._fkControls)

		# fk reverse controls
		self._addListAsStringAttr('fkReverseControls', self._fkReverseControls)

	def _getRigComponentInfo(self):
		super(FkDriveIkSplineSolverComponent, self)._getRigComponentInfo()

		# get fk controls
		self._fkControls = self._getStringAttrAsList('fkControls')

		# get fk controls
		self._fkReverseControls = self._getStringAttrAsList('fkReverseControls')

