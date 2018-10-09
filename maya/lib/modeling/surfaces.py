# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

# -- import lib
import lib.common.apiUtils as apiUtils
# ---- import end ----

# sub functions
# get nurbs surface info
def __getSurfaceInfo(surface, type='python'):
	'''
	return surface info:
	- controlVertices: an array of control vertices
	- uKnotSequences: an array of U knot values
	- vKnotSequences: an array of V knot values
	- degreeInU: degree of first set of basis functions
	- degreeInV : degree of second set of basis functions
	- formU : open, closed, periodic in U
	- formV : open, closed, periodic in V
	- uvCount: The uv counts for each patch in the surface
	- uvIds: The uv indices to be mapped to each patch-corner
	- name: surface name
	- type: shape type, nurbsSurface

	paramters:

	type(string): return type, python/MObj, default is python
	'''

	MFnSurface = __setMFnNurbsSurface(surface) # set MFnNurbsSurface to query

	controlVertices = OpenMaya.MPointArray()
	MFnSurface.getCVs(controlVertices, OpenMaya.MSpace.kObject)

	uKnotSequences = OpenMaya.MDoubleArray()
	vKnotSequences = OpenMaya.MDoubleArray()
	MFnSurface.getKnotsInU(uKnotSequences)
	MFnSurface.getKnotsInV(vKnotSequences)

	degreeInU = MFnSurface.degreeU()
	degreeInV = MFnSurface.degreeV()

	formU = MFnSurface.formInU()
	formV = MFnSurface.formInV()

	uvCount = OpenMaya.MIntArray()
	uvIds = OpenMaya.MIntArray()
	MFnSurface.getAssignedUVs(uvCount, uvIds)
	
	if type != 'MObj':
		controlVertices = apiUtils.convertMPointArrayToList(controlVertices)
		uKnotSequences = apiUtils.convertMArrayToList(uKnotSequences)
		vKnotSequences = apiUtils.convertMArrayToList(vKnotSequences)
		uvCount = apiUtils.convertMArrayToList(uvCount)
		uvIds = apiUtils.convertMArrayToList(uvIds)

	surfaceInfo = {'name': surface,
				   'controlVertices': controlVertices,
				   'uKnotSequences': uKnotSequences,
				   'vKnotSequences': vKnotSequences,
				   'degreeInU': degreeInU,
				   'degreeInV': degreeInV,
				   'formU': formU,
				   'formV': formV,
				   'uvCount': uvCount,
				   'uvIds': uvIds,
				   'type': 'nurbsSurface'}

	return surfaceInfo

# load nurbs surface info
def __convertSurfaceInfo(surfaceInfo):
	# convert everything to MObj
	surfaceInfo['controlVertices'] = apiUtils.convertListToMPointArray(surfaceInfo['controlVertices'])
	surfaceInfo['uKnotSequences'] = apiUtils.convertListToMArray(surfaceInfo['uKnotSequences'])
	surfaceInfo['vKnotSequences'] = apiUtils.convertListToMArray(surfaceInfo['vKnotSequences'])
	surfaceInfo['uvCount'] = apiUtils.convertListToMArray(surfaceInfo['uvCount'], type = 'MIntArray')
	surfaceInfo['uvIds'] = apiUtils.convertListToMArray(surfaceInfo['uvIds'], type = 'MIntArray')

	return surfaceInfo

# create nurbs surface
def __createSurface(surfaceInfo, surfaceName):
	# create surface
	MObj = apiUtils.setMObj(surfaceName)
	MFnNurbsSurface = OpenMaya.MFnNurbsSurface()
	MFnNurbsSurface.create(surfaceInfo['controlVertices'], surfaceInfo['uKnotSequences'], 
				   surfaceInfo['vKnotSequences'], surfaceInfo['degreeInU'], 
				   surfaceInfo['degreeInV'], surfaceInfo['formU'], 
				   surfaceInfo['formV'], True, MObj)
	MFnNurbsSurface.assignUVs(surfaceInfo['uvCount'], surfaceInfo['uvIds'])

	return surfaceName

# set MFnNurbsSurface
def __setMFnNurbsSurface(surface):
	MDagPath, MComponents = apiUtils.setMDagPath(surface)
	MFnSurface = OpenMaya.MFnNurbsSurface(MDagPath)
	return MFnSurface