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
file_misc = 'misc'
format_files = 'mb'
format_import = ['mb', 'ma', 'obj']
format_mb = 'mayaBinary'

# export nodes as misc file
def exportNodesAsMisc(rig=None, asset=None, project=None, nodes=[], name=None):
	# get export path
	pathMisc = rigs.getDataFolderPath('miscs', rig, asset, project, mode='wip')
	# export nodes
	if nodes:
		startTime = time.time()
		if not name:
			name = file_misc
		miscFile = name + '.' + format_files
		pathMiscFile = os.path.join(pathMisc, miscFile)
		cmds.select(nodes)
		cmds.file(pathMiscFile, force = True, type = format_mb, exportSelected = True)
		endTime = time.time()
		logger.info('Misc file exported at {}, took {} seconds'.format(pathMiscFile, endTime - startTime))
	else:
		logger.info('No node given, skipped')

# import misc file
def importMisc(rig=None, asset=None, project=None, mode='publish', version=0, files=[], fileType=format_import):
	# get misc path
	pathMisc = rigs.getDataPath('miscs', rig, asset, project, files = files, fileType = fileType, 
								mode = mode, version = version)
	if pathMisc:
		for p in pathMisc:
			startTime = time.time()
			cmds.file(p, i = True)
			endTime = time.time()
			logger.info('Import misc file {} successfully, took {} seconds'.format(p, endTime - startTime))
	else:
		logger.info('No misc file found, skipped')


	

	