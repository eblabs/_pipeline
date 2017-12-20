## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import riggingAPI.rigLimbs.baseLimbs.singleJointRig as singleJointRig
reload(singleJointRig)
import riggingAPI.controls as controls
import namingAPI.naming as naming
## function
class cogRig(singleJointRig.singleJointRig):
	"""docstring for cogRig"""
	def __init__(self):
		super(cogRig, self).__init__()
		
		self._sBpJnt = naming.oName(sType = 'blueprint', sSide = 'm', sPart = 'cog').sName
		oCtrlLocal = controls.oControl(naming.oName(sType = 'ctrl', sSide = 'm', sPart = 'local').sName)
		self._sConnectInCtrl = oCtrlLocal.sOutput
		self._sConnectInJnt = 'rigJoints'
		self._bSub = True