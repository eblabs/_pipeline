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
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import math

# -- import lib
import common.apiUtils as apiUtils
import common.files.files as files
import meshes
import surfaces
import curves
# ---- import end ----

# save geometries info
def saveGeoInfo(geo, path):
	startTime = time.time()
	# check geo type
	geoShape = cmds.listRelatives(geo, s = True)[0]
	if cmds.objectType(geoShape) == 'mesh':
		geoInfo = meshes.__getMeshInfo(geo)
	elif cmds.objectType(geoShape) == 'nurbsSurface':
		geoInfo = surfaces.__getSurfaceInfo(geo)
	elif cmds.objectType(geoShape) == 'nurbsCurve':
		geoInfo = curves.__getCurveInfo(geo)
	fileFormat = files.readJsonFile(files.path_fileFormat)
	path = os.path.join(path, '{}.{}'.format(geo, fileFormat['geometry']))
	files.writePickleFile(path, geoInfo)
	endTime = time.time()
	logger.info('Save {} geo info at {}, took {} seconds'.format(mesh, path, endTime - startTime))

# load geometries info
def loadGeoInfo(path, name=None, vis=True):
	geoInfo = files.readPickleFile(path)
	if geoInfo['type'] == 'mesh':
		geoInfo = meshes.__convertMeshInfo(geoInfo)
	elif geoInfo['type'] == 'surface':
		geoInfo = surfaces.__convertSurfaceInfo(geoInfo)
	elif geoInfo['type'] == 'curve':
		geoInfo = curves.__convertCurveInfo(geoInfo)
	geo = createGeo(geoInfo, name = name, vis = vis)
	return geo

# create geometry
def createGeo(geoInfo, name=None, vis=True):
	startTime = time.time()
	# create transform node
	if not name:
		name = meshInfo['name']
	if not cmds.objExists(name):
		cmds.createNode('transform', name = name)
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
