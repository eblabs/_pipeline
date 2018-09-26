# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import cPickle
import cPickle

# -- import maya lib

# -- import lib

# ---- import end ----

# ---- global variable
path_fileFormat = 'C:/_pipeline/maya/lib/common/files/fileFormat.json'

# function
# json 
# write json file
def writeJsonFile(path, data):
	with open(path, 'w') as outfile:
		json.dump(data, outfile, indent=4, sort_keys=True)
	file.close(outfile)

# read json file
def readJsonFile(path):
	with open(path, 'r') as infile:
		data = json.load(infile)
	file.close(infile)
	return data

# cPickle
def writePickleFile(path, data):
	outfile = open(path, 'wb')
	cPickle.dump(data, outfile, cPickle.HIGHEST_PROTOCOL)
	outfile.close()

def readPickleFile(path):
	infile = open(path, 'rb')
	data = cPickle.load(infile)
	infile.close()
	return data