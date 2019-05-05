#=================#
# IMPORT PACKAGES #
#=================#

## import maya packages
import maya.cmds as cmds

## import utils

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#

#=================#
#    FUNCTION     #
#=================#
def connect_attrs(driverAttrs, drivenAttrs, driver=None, driven=None, force=True):
	'''
	Connect driver attrs to driven attrs

	Args:
		driverAttrs(str/list): source attrs
		drivenAttrs(str/list): target attrs
	Kwargs:
		driver(str): override the node in driverAttrs
		driven(str): override the drivenAttrs
		force(bool): override the connection/lock status
	'''

	# check if driverAttrs/drivenAttrs is string/list
	if isinstance(driverAttrs, basestring):
		driverAttrs = [driverAttrs]
	if isinstance(drivenAttrs, basestring):
		drivenAttrs = [drivenAttrs]

	# connect each attr
	for attrs in zip(driverAttrs, drivenAttrs):
		_connect_single_attr(attrs[0], attrs[1], 
							 driver=driver, driven=driven,
							 force=force)
	if len(driverAttrs) == 1:
		if not _check_attr_exists(driverAttrs[0]):
			return
		for attr in drivenAttrs[1:]:
			_connect_single_attr(drivenAttrs[0], attr, 
								 driver=driver, driven=driven,
								 force=force)

#=================#
#  SUB FUNCTION   #
#=================#
def _check_attr_exists(attr, node=None):
	'''
	Check if attr exists
	'''
	if not node:
		node = attr.split('.')[0]
		attr = attr.replace(node+'.', '')
	try:
		cmds.getAttr('{}.{}'.format(node, attr))
		return '{}.{}'.format(node, attr)
	except:
		Logger.warn('{} does not have attr {}'.format(node, attr))
		return None

def _connect_single_attr(driverAttr, drivenAttr, driver=None, driven=None, force=True):
	'''
	Connect single attr
	'''
	attrConnect=[]
	for attr, node in zip([driverAttr, drivenAttr],
						  [driver, driven]):
		attrCheck = _check_attr_exists(attr, node=node)
		if not attrCheck:
			break
		else:
			attrConnect.append(attrCheck)
	if not attrCheck:
		return

	# check if driven attr has connection
	inputPlug = cmds.listConnections(attrConnect[1], source=True,
									 destination=False, plugs=True,
									 skipConversionNodes=True)
	# check if driven attr is locked
	lock = cmds.getAttr(attrConnect[1], lock=True)

	# connect attr
	if not inputPlug and not lock:
		cmds.connectAttr(attrConnect[0], attrConnect[1])
	else:
		if force:
			cmds.setAttr(attrConnect[1], lock=False)
			cmds.connectAttr(attrConnect[0], attrConnect[1], force=True)
			if lock:
				cmds.setAttr(attrConnect[1], lock=True)
		else:
			if inputPlug:
				Logger.warn('{} already has connection from {}, skipped'.format(attrConnect[1], inputPlug[0]))
			elif lock:
				logger.warn('{} is locked, skipped'.format(attrConnect[1]))
