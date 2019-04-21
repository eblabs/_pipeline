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
import lib.modeling.geometries as geometries
# ---- import end ----

# -- import assets lib
import assets.lib.rigs as rigs
# ---- import end ----

# global varibles
file_skeleton = 'skeleton'
format_files = files.readJsonFile(files.path_fileFormat)
# export skeleton
def exportSkeleton(rig='deformationRig', asset=None, project=None, joints=[]):
	# get export path
	pathSkeleton = rigs.getDataFolderPath('skeleton', rig, asset, project, mode='publish')

	if pathSkeleton:
		if joints:
			joints.saveJointsInfo(jnts, pathSkeleton, name = file_skeleton)
		else:
			logger.info('No joint given, skipped')
	else:
		logger.info('{} does not exist, skipped'.format(pathSkeleton))

# import skeleton
def importSkeleton(rig='deformationRig', asset=None, project=None, mode='publish', version=0):
	skeletonFile = file_skeleton + '.' + format_files['joint']
	# get file path
	pathSkeleton = rigs.getDataPath('skeleton', rig, asset, project, files = [skeletonFile], 
									  mode = mode, version = version)

	if pathSkeleton:
		joints.loadJointsInfo(pathSkeleton[0], vis = True)
	else:
		logger.info('No skeleton file found, skipped')