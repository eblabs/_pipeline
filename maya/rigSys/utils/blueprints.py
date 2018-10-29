# -- import for debug
import logging
debugLevel = logging.INFO # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import time
import time

# -- import lib
import lib.common.naming.naming as naming
import lib.common.files.files as files
import lib.common.transforms as transforms
import lib.rigging.joints as joints
reload(joints)
import lib.modeling.geometries as geometries
reload(geometries)
# ---- import end ----

# -- import assets lib
import assets.lib.rigs as rigs
# ---- import end ----

# global varibles
grp_blueprint = '_blueprint_'
file_blueprint = 'blueprints'
format_files = files.readJsonFile(files.path_fileFormat)
# export blueprints
def exportBlueprints(asset, project):
	# get export path
	pathBp = rigs.getDataFolderPath('blueprints', 'animationRig', asset, project, mode='wip')
	# export files
	if cmds.objExists(grp_blueprint):
		# get joints info and save
		jnts = cmds.listRelatives(grp_blueprint, ad = True, type = 'joint')
		joints.saveJointsInfo(jnts, pathBp, name = file_blueprint)

		# get geo info and save
		geos = cmds.listRelatives(grp_blueprint, ad = True, type = 'transform')
		geometries.saveGeoInfo(geos, pathBp, name = file_blueprint, separate = False)
	else:
		logger.info('Blueprints Group {} does not exist, skipped'.format(grp_blueprint))

# import blueprints
def importBlueprints(asset, project, mode='publish', version=0):
	bpJntFile = file_blueprint + '.' + format_files['joint']
	bpGeoFile = file_blueprint + '.' + format_files['geometry']
	# get file path
	pathBlueprints = rigs.getDataPath('blueprints', 'animationRig', asset, project, files = [bpJntFile, bpGeoFile], 
									  mode = mode, version = version)

	if pathBlueprints:
		# create blueprint group if not exist
		if not cmds.objExists(grp_blueprint):
			transforms.createTransformNode(grp_blueprint, lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

		for p in pathBlueprints:
			if p.endswith(format_files['joint']):
				joints.loadJointsInfo(p, vis = True)
			elif p.endswith(format_files['geometry']):
				geometries.loadGeoInfo(p, vis = True)


