# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import os
import os

# -- import time
import time

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.files.files as files
import lib.common.nodeUtils as nodeUtils
import lib.common.hierarchy as hierarchy
import meshes
import surfaces
import curves
# ---- import end ----

# save geometries info
def saveGeoInfo(geometry, path, name=None, separate=False):
	if not name:
		name = 'geoInfo'
	if isinstance(geometry, basestring):
		geometry = [geometry]

	fileFormat = files.readJsonFile(files.path_fileFormat)
	
	startTime = time.time()

	geoInfoDict = {}
	for geo in geometry:
		# check geo type
		if cmds.objectType(geo) == 'transform':
			geoShape = cmds.listRelatives(geo, s = True)[0]
		else:
			geoShape = geo
			geo = cmds.listRelatives(geoShape, p = True)[0]
		if cmds.objectType(geoShape) == 'mesh':
			geoInfo = meshes.__getMeshInfo(geoShape)
		elif cmds.objectType(geoShape) == 'nurbsSurface':
			geoInfo = surfaces.__getSurfaceInfo(geoShape)
		elif cmds.objectType(geoShape) == 'nurbsCurve':
			geoInfo = curves.__getCurveInfo(geoShape)
		parent = cmds.listRelatives(geo, p = True)
		if parent:
			parent = parent[0]
		geoInfo.update({'parent': parent})
		geoInfo = {geo: geoInfo}
		if separate:		
			pathOutput = os.path.join(path, '{}.{}'.format(geo, fileFormat['geometry']))
			files.writePickleFile(pathOutput, geoInfo)
			logger.info('Save {} geoInfo at {}'.format(geo, pathOutput))
		else:
			geoInfoDict.update(geoInfo)
	if not separate:
		pathOutput = os.path.join(path, '{}.{}'.format(name, fileFormat['geometry']))
		files.writePickleFile(pathOutput, geoInfoDict)
		logger.info('Save {} geoInfo at {}'.format(geometry, pathOutput))

	endTime = time.time()
	logger.info('Save sucessfully, took {} seconds'.format(endTime - startTime))


# load geometries info
def loadGeoInfo(path, vis=True):
	geoInfoDict = files.readPickleFile(path)
	parentList = []
	jntsList = geoInfoDict.keys()
	for geo, geoInfo in geoInfoDict.iteritems():
		if geoInfo['type'] == 'mesh':
			geoInfo = meshes.__convertMeshInfo(geoInfo)
		elif geoInfo['type'] == 'surface':
			geoInfo = surfaces.__convertSurfaceInfo(geoInfo)
		elif geoInfo['type'] == 'curve':
			geoInfo = curves.__convertCurveInfo(geoInfo)
		createGeo(geoInfo, name = geo, vis = vis)
		parent = geoInfo['parent']
		parentList.append(parent)
	for jnts in zip(jntsList, parentList):
		hierarchy.parent(jnts[0], jnts[1])
	return jntsList

# create geometry
def createGeo(geoInfo, name=None, vis=True):
	startTime = time.time()
	# create transform node
	if not name:
		name = meshInfo['name']
	if not cmds.objExists(name):
		cmds.group(empty = True, name = name)
	else:
		logger.warn('{} already exists, skipped'.format(name))
		return

	# create geo
	if geoInfo['type'] == 'mesh':
		geo = meshes.__createMesh(geoInfo, name)
	elif geoInfo['type'] == 'surface':
		geo = surfaces.__createSurface(geoInfo, name)
	elif geoInfo['type'] == 'curve':
		geo = curves.__createCurve(geoInfo, name)

	# rename shape node
	shape = cmds.listRelatives(geo, s = True)[0]
	shape = cmds.rename(shape, '{}Shape'.format(geo))

	# vis
	if not vis:
		cmds.setAttr('{}.v'.format(geo), 0)

	# assign default shader
	maya.cmds.sets(geo, e=True, fe='initialShadingGroup')

	# log
	endTime = time.time()
	logger.info('create {}, took {} seconds'.format(geo, endTime - startTime))

	return geo
