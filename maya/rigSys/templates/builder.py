# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

class Builder(object):
	"""docstring for Builder"""
	def __init__(self, arg):
		super(Builder, self).__init__()
		
		# preBuild, build, postBuild
		self._preBuild = {'order': {},
						  'info': {}}
		self._build = {'order': {},
					   'info': {}}
		self._postBuild = {'order': {},
						   'info': {}}

	def registerTask(self, taskInfo):
		'''
		taskInfo template

		'name'
		'task'
		'after'
		'section'
		'''
		# get section
		section = taskInfo['section']
		if section == 'preBuild':
			taskDict = self._preBuild
		elif section == 'build':
			taskDict = 'build'
		else:
			taskDict = 'postBuild'

		# get index
		index = None
		if 'after' in taskInfo:
			after = taskInfo['after']
			if isinstance(after, int):
				index = after + 1
				if index > len(taskDict['order']):
					index = None
			elif isinstance(after, basestring):
				if after in taskDict['order']:
					index = taskDict['order'].index(after) + 1

		# add to section
		if index == None:
			taskDict['order'].append(taskInfo['name'])
			taskDict['info'].append({'task': taskInfo['task']})
		else:
			taskDict['order'].insert(index, taskInfo['name'])
			taskDict['info'].insert(index, {'task': taskInfo['task']})

	def registertion(self):
		pass
