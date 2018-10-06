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
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.common.apiUtils as apiUtils
import lib.rigging.joints as joints
# ---- import end ----

# -- import component
import jointComponent as jointComponent
# ---- import end ----

class IkSolverComponent(jointComponent.JointComponent):
	"""ikSolverComponent template"""
	def __init__(self, *args,**kwargs):
		super(IkSolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.core.ikSolverComponent'
		self._ikControls = []
		self._ikHandles = []

	def _writeRigComponentInfo(self):
		super(IkSolverComponent, self)._writeRigComponentInfo()

		# ik controls
		self._addListAsStringAttr('ikControls', self._ikControls)
		# ik Handles
		self._addListAsStringAttr('ikHandles', self._ikHandles)

	def _getRigComponentInfo(self):
		super(IkSolverComponent, self)._getRigComponentInfo()

		# get ik controls
		self._ikControls = self._getStringAttrAsList('ikControls')

		# get ik handles
		self._ikHandles = self._getStringAttrAsList('ikHandles')
		

