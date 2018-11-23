# import sys
import sys

# import maya library
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

# import math
import math

# import numpy
import numpy

nodeName = 'rbfDriver'
nodeId = OpenMaya.MTypeId(0x100fff)

class RbfDriver(OpenMayaMPx.MPxNode):
	"""docstring for RbfDriver"""

	inputData = OpenMaya.MObject()
	epsilon = OpenMaya.MObject()
	inputPoint = OpenMaya.MObject()
	interpType = OpenMaya.MObject()

	output = OpenMaya.MObject()

	def __init__(self):
		super(RbfDriver, self).__init__()

	def compute(self, plug, dataBlock):
		# get input values
		MArrayDataHandle_inputData = dataBlock.inputArrayValue(RbfDriver.inputData)

		epsilon = dataBlock.inputValue(RbfDriver.epsilon).asFloat()
		inputPoint = dataBlock.inputValue(RbfDriver.inputPoint).asFloat3()
		interpType = dataBlock.inputValue(RbfDriver.interpType).asInt()

		# get interp function
		self._getInterpFunction(interpType)

		# compute
		array_output = self._computeOutput(MArrayDataHandle_inputData, inputPoint, epsilon = epsilon)
		
		# set output
		MArrayDataHandle_output = dataBlock.outputArrayValue(RbfDriver.output)
		MArrayDataBuilder_output = MArrayDataHandle_output.builder()

		count = len(array_output)
		count_outputOrig = MArrayDataBuilder_output.elementCount()

		for i in xrange(count):			
			MDataHandle_element = MArrayDataBuilder_output.addElement(i)
			MDataHandle_element.setFloat(array_output[i])

		# remove extra output
		if count < count_outputOrig:
			for i in xrange(count_outputOrig - count):
				MArrayDataBuilder_output.removeElement(count + i)

		MArrayDataHandle_output.set(MArrayDataBuilder_output)

		dataBlock.setClean(plug)

	def _getDistance(self, point, target):
		p1 = numpy.array(point)
		p2 = numpy.array(target)
		return numpy.linalg.norm(p1 - p2)

	def _getInterpFunction(self, interpType):
		if interpType == 0:
			self._interpFunction = self._gaussian
		elif interpType == 1:
			self._interpFunction = self._multiquadric
		elif interpType == 2:
			self._interpFunction = self._inverseQuadratic
		elif interpType == 3:
			self._interpFunction = self._inverseMultiquadric
		elif interpType == 4:
			self._interpFunction = self._thinPlateSpline
		elif interpType == 5:
			self._interpFunction = self._shiftedLog
		elif interpType == 6:
			self._interpFunction = self._linear
		elif interpType == 7:
			self._interpFunction = self._cubic
		elif interpType == 8:
			self._interpFunction = self._quintic

	def _gaussian(self, distance, epsilon=10.0):
		# Gaussian f(r) = e^(-(dis/epsilon)^2)
		parameter = -1 * ((distance/epsilon)**2)
		interpolation = math.exp(parameter)
		return interpolation

	def _multiquadric(self, distance, epsilon=10.0):
		# Multiquadric f(r) = sqrt(1 + (dis/epsilon)^2)
		parameter = 1 + ((distance/float(epsilon))**2)
		interpolation = math.sqrt(parameter)
		return interpolation

	def _inverseQuadratic(self, distance, epsilon=10.0):
		# Inverse quadratic f(r) = 1 / (1 + (dis/epsilon)^2)
		parameter = 1 + ((distance/float(epsilon))**2)
		interpolation = 1.0 / float(parameter)
		return interpolation

	def _inverseMultiquadric(self, distance, epsilon=10.0):
		# Inverse multiquadric f(r) = 1 / sqrt(1 + (epsilon * dis)^2)
		parameter = 1 + ((epsilon*distance)**2)
		interpolation = 1.0 / float(math.sqrt(parameter))
		return interpolation

	def _thinPlateSpline(self, distance, epsilon=10.0):
		# Thin plate spline f(r) = r^2 * ln(r)
		parameter = distance**2
		interpolation = parameter * math.log(10e-1+parameter) #can't do log(0), add a small value
		return interpolation

	def _shiftedLog(self, distance, epsilon=10.0):
		# Shifted Log f(r) = sqrt(log(r^2 + epsilon ^2))
		parameter = distance**2 + epsilon**2
		interpolation = math.sqrt(math.log10(10e-1+parameter))
		return interpolation

	def _linear(self, distance, epsilon=10.0):
		return distance

	def _cubic(self, distance, epsilon=10.0):
		return distance**3

	def _quintic(self, distance, epsilon=10.0):
		return distance**5

	def _computeOutput(self, MArrayDataHandle_inputData, inputPoint, epsilon=10.0):
		count = MArrayDataHandle_inputData.elementCount()
		# get matrix
		matrix_interp = []
		matrix_samples = []
		list_data = [] # save a list for further use
		for i in xrange(count):
			# interp matrix
			row_interp = []
			MArrayDataHandle_inputData.jumpToArrayElement(i)
			data_i = MArrayDataHandle_inputData.inputValue().asFloat3()
			list_data.append(data_i)
			for j in xrange(count):
				MArrayDataHandle_inputData.jumpToArrayElement(j)
				data_j = MArrayDataHandle_inputData.inputValue().asFloat3()
				distance = self._getDistance(data_i, data_j)
				interpVal = self._interpFunction(distance, epsilon = epsilon)
				row_interp.append(interpVal)
			matrix_interp.append(row_interp)

			# sample value matrix
			row_samples = [0]*count
			row_samples[i] = 1
			matrix_samples.append(row_samples)

		matrix_interp = numpy.array(matrix_interp)
		matrix_samples = numpy.array(matrix_samples)

		# inverse interp matrix
		try:
			inverseMatrix_interp = numpy.linalg.inv(matrix_interp)
		except:
			return [0] * count

		# get weights
		array_weights = numpy.dot(inverseMatrix_interp, matrix_samples)

		# output values
		array_output = [0]*count
		# sum final output value
		for i in xrange(count):
			distance = self._getDistance(inputPoint, list_data[i])
			interpVal = self._interpFunction(distance, epsilon = epsilon)
			for j in xrange(count):
				array_output[j] += array_weights[i][j] * interpVal

		# normalize output to 0-1
		array_output = numpy.clip(array_output, 0, 1)
		weight_sum = 1/float(sum(array_output) + 10e-1)
		array_output = numpy.dot(array_output, weight_sum)

		return array_output
				
# creator
def creator():
	return OpenMayaMPx.asMPxPtr(RbfDriver()) 

# initialize
def initialize():
	# initialize input plug

	# data point
	MFnNumericAttr_inputData = OpenMaya.MFnNumericAttribute()
	RbfDriver.inputData = MFnNumericAttr_inputData.createPoint('inputData', 'data')
	MFnNumericAttr_inputData.setArray(True)
	MFnNumericAttr_inputData.setStorable(True)
	MFnNumericAttr_inputData.setConnectable(True)
	MFnNumericAttr_inputData.setKeyable(True)
	MFnNumericAttr_inputData.setIndexMatters(False)
	MFnNumericAttr_inputData.setDisconnectBehavior(OpenMaya.MFnNumericAttribute.kNothing)
	
	# input point
	MFnNumericAttr_inputPoint = OpenMaya.MFnNumericAttribute()
	RbfDriver.inputPoint = MFnNumericAttr_inputPoint.createPoint('inputPoint', 'ip')
	MFnNumericAttr_inputPoint.setStorable(True)
	MFnNumericAttr_inputPoint.setConnectable(True)
	MFnNumericAttr_inputPoint.setKeyable(True)
	MFnNumericAttr_inputPoint.setDisconnectBehavior(OpenMaya.MFnNumericAttribute.kNothing)

	# epsilon
	MFnNumericAttr_epsilon = OpenMaya.MFnNumericAttribute()
	RbfDriver.epsilon = MFnNumericAttr_epsilon.create('epsilon', 'r', OpenMaya.MFnNumericData.kFloat, 10.0)
	MFnNumericAttr_inputPoint.setStorable(True)
	MFnNumericAttr_inputPoint.setKeyable(False)

	# interpType
	MFnEnumAttr_interpType = OpenMaya.MFnEnumAttribute()
	RbfDriver.interpType = MFnEnumAttr_interpType.create('interpType', 'interp')
	MFnEnumAttr_interpType.addField('Gaussian', 0)
	MFnEnumAttr_interpType.addField('Multiquadric', 1)
	MFnEnumAttr_interpType.addField('Inverse quadratic', 2)
	MFnEnumAttr_interpType.addField('Inverse multiquadric', 3)
	MFnEnumAttr_interpType.addField('Thin plate spline', 4)
	MFnEnumAttr_interpType.addField('Shifted Log', 5)
	MFnEnumAttr_interpType.addField('Linear', 6)
	MFnEnumAttr_interpType.addField('Cubic', 7)
	MFnEnumAttr_interpType.addField('Quintic', 8)

	# initialize output plug
	# output
	MFnNumericAttr_output = OpenMaya.MFnNumericAttribute()
	RbfDriver.output = MFnNumericAttr_output.create('output', 'o', OpenMaya.MFnNumericData.kFloat, 0.0)
	MFnNumericAttr_output.setArray(True)
	MFnNumericAttr_output.setStorable(True)
	MFnNumericAttr_output.setUsesArrayDataBuilder(True)

	# add attrs
	RbfDriver.addAttribute(RbfDriver.inputData)
	RbfDriver.addAttribute(RbfDriver.inputPoint)
	RbfDriver.addAttribute(RbfDriver.epsilon)
	RbfDriver.addAttribute(RbfDriver.interpType)
	RbfDriver.addAttribute(RbfDriver.output)

	# attr affects
	RbfDriver.attributeAffects(RbfDriver.inputData, RbfDriver.output)
	RbfDriver.attributeAffects(RbfDriver.inputPoint, RbfDriver.output)
	RbfDriver.attributeAffects(RbfDriver.epsilon, RbfDriver.output)
	RbfDriver.attributeAffects(RbfDriver.interpType, RbfDriver.output)

# initializePlugin
def initializePlugin(MObject):
	MPlugin = OpenMayaMPx.MFnPlugin(MObject)
	try:
		MPlugin.registerNode(nodeName, nodeId, creator, initialize)
	except:
		raise RuntimeError('Failed to register command {}'.format(nodeName))

# uninitialize
def uninitializePlugin(MObject):
	MPlugin = OpenMayaMPx.MFnPlugin(MObject)
	try:
		MPlugin.deregisterNode(nodeId)
	except:
		raise RuntimeError('Failed to unregister command {}'.format(nodeName))


