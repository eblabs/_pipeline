# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.packages as packages
# ---- import end ----

def createComponent(componentType, data):
	componentFunc = componentType.split('.')[-1]
	componentFunc = componentFunc[0].upper() + componentFunc[1:]
	componentImport = packages.importModule(componentType)
	Limb = getattr(componentImport, componentFunc)(**data)
	Limb.create()
	return Limb

def getComponentAttr(Component, attr):
	if isinstance(attr, basestring):
		attr = attr.split('.')
	attrValue = Component
	for a in attr:
		attrValue = getattr(attrValue, a)
	return attrValue