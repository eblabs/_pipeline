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
import maya.OpenMaya as OpenMaya
import math

# -- import lib
import lib.common.apiUtils as apiUtils
import lib.common.files.files as files
# ---- import end ----

# sub function
# get mesh info
def __getMeshInfo(mesh, type='python'):
	'''
	return mesh info:
	- numVertices: mesh vertex number
	- numPolygons: mesh face number
	- vertexArray: vertex array of the mesh
	- polygonCounts: array of vertex counts for each polygon
	- polygonConnects: array of vertex connections for each polygon
	- uArray: The array of u values to be set
	- vArray: The array of v values to be set
	- uvCount: The container for the uv counts for each polygon in the mesh
	- uvIds: The container for the uv indices mapped to each polygon-vertex
	- name: mesh name
	- type: shape type, mesh

	paramters:

	type(string): return type, python/MObj, default is python
	'''

	MFnMesh = __setMFnMesh(mesh) # set MFnMesh to query

	numVertices = MFnMesh.numVertices()
	numPolygons = MFnMesh.numPolygons()
	MVertexArray = OpenMaya.MFloatPointArray()
	MFnMesh.getPoints(MVertexArray, OpenMaya.MSpace.kObject)
	MPolyCountArray = OpenMaya.MIntArray()
	MPolyConnects = OpenMaya.MIntArray()
	MFnMesh.getVertices(MPolyCountArray, MPolyConnects)
	uArray = OpenMaya.MFloatArray()
	vArray = OpenMaya.MFloatArray()
	MFnMesh.getUVs(uArray, vArray)
	uvCount = OpenMaya.MIntArray()
	uvIds = OpenMaya.MIntArray()
	MFnMesh.getAssignedUVs(uvCount, uvIds)

	if type != 'MObj':
		# convert everything to python type
		MVertexArray = apiUtils.convertMPointArrayToList(MVertexArray)
		MPolyCountArray = apiUtils.convertMArrayToList(MPolyCountArray)
		MPolyConnects = apiUtils.convertMArrayToList(MPolyConnects)
		uArray = apiUtils.convertMArrayToList(uArray)
		vArray = apiUtils.convertMArrayToList(vArray)
		uvCount = apiUtils.convertMArrayToList(uvCount)
		uvIds = apiUtils.convertMArrayToList(uvIds)

	meshInfo = {'name': mesh,
				'numVertices': numVertices,
				'numPolygons': numPolygons,
				'vertexArray': MVertexArray,
				'polygonCounts': MPolyCountArray,
				'polygonConnects': MPolyConnects,
				'uArray': uArray,
				'vArray': vArray,
				'uvCount': uvCount,
				'uvIds': uvIds,
				'type': 'mesh'}

	return meshInfo

# load mesh info
def __convertMeshInfo(meshInfo):
	# convert everything to MObj
	# MVertexArray
	meshInfo['vertexArray'] = apiUtils.convertListToMPointArray(meshInfo['vertexArray'], 
													 type = 'MFloatPointArray')
	# polygonCounts
	meshInfo['polygonCounts'] = apiUtils.convertListToMArray(meshInfo['polygonCounts'],
												   type = 'MIntArray')
	# polygonConnects
	meshInfo['polygonConnects'] = apiUtils.convertListToMArray(meshInfo['polygonConnects'],
												 type = 'MIntArray')
	# uArray
	meshInfo['uArray'] = apiUtils.convertListToMArray(meshInfo['uArray'], 
										  			type = 'MFloatArray')
	# vArray
	meshInfo['vArray'] = apiUtils.convertListToMArray(meshInfo['vArray'], 
										  			type = 'MFloatArray')
	# uvCounts
	meshInfo['uvCounts'] = apiUtils.convertListToMArray(meshInfo['uvCounts'],
														type = 'MIntArray')
	# uvIds
	meshInfo['uvIds'] = apiUtils.convertListToMArray(meshInfo['uvIds'], 
										 			type = 'MIntArray')

	return meshInfo

# create mesh
def __createMesh(meshInfo, meshName):
	# create mesh
	MObj = apiUtils.setMObj(meshName)
	MFnMesh = OpenMaya.MFnMesh()
	MFnMesh.create(meshInfo['numVertices'], meshInfo['numPolygons'], 
				   meshInfo['vertexArray'], meshInfo['polygonCounts'], 
				   meshInfo['MPolyConnects'], meshInfo['uArray'], 
				   meshInfo['vArray'], MObj)
	MFnMesh.assignUVs(meshInfo['uvCount'], meshInfo['uvIds'])

	return meshName

# set MFnMesh
def __setMFnMesh(mesh):
	MDagPath, MComponents = apiUtils.setMDagPath(mesh)
	MFnMesh = OpenMaya.MFnMesh(MDagPath)
	return MFnMesh