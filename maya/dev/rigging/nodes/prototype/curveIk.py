# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

# import math
import math

# import numpy
import numpy

nodeName = 'spline'
nodeId = OpenMaya.MTypeId(0x101000)


class CurveIk(OpenMayaMPx.MPxNode):
	"""docstring for RbfDriver"""

	# curves
	input_curve = OpenMaya.MObject()  # main ik curve, used to drive nodes
	up_curve = OpenMaya.MObject()  # curve to define up vector in ribbon mode

	# aim vector
	aim_vector = OpenMaya.MObject()
	up_vector = OpenMaya.MObject()
	aim_mode = OpenMaya.MObject()  # tangent/next point

	# chain parameter
	node_number = OpenMaya.MObject()  # output nodes number
	stretch = OpenMaya.MObject()
	stretch_clamp = OpenMaya.MObject()  # clamp stretch if True
	stretch_limit = OpenMaya.MObject()  # multiplier of the original curve length
	slide = OpenMaya.MObject()
	curve_world_matrix = OpenMaya.MObject()

	# ik type
	ik_type = OpenMaya.MObject()  # spline/ribbon

	# spline
	start_matrix = OpenMaya.MObject()
	end_matrix = OpenMaya.MObject()
	sections = OpenMaya.MObject()  # twist sections number
	twist_ramp = OpenMaya.MObject()  # define the twist ramp from start to the end
	twist_section_ramp = OpenMaya.MObject()  # define sections twist ramp

	# output
	output = OpenMaya.MObject()

	def __init__(self):
		super(CurveIk, self).__init__()

	def compute(self, plug, data_block):
		pass


# creator
def creator():
	return OpenMayaMPx.asMPxPtr(CurveIk())


# initialize
def initialize():
	# initialize input plug

	curve_attribute = OpenMaya.MFnTypedAttribute()
	number_attribute = OpenMaya.MFnNumericAttribute()
	enum_attribute = OpenMaya.MFnEnumAttribute()
	matrix_attribute = OpenMaya.MFnMatrixAttribute()
	ramp_attribute = OpenMaya.MRampAttribute()

	# curves
	# main ik curve, used to drive nodes
	CurveIk.input_curve = curve_attribute.create('inputCurve', 'ic', OpenMaya.MFnData.kNurbsCurve)
	# curve to define up vector in ribbon mode
	CurveIk.up_curve = curve_attribute.create('upCurve', 'uc', OpenMaya.MFnData.kNurbsCurve)

	# aim vector
	CurveIk.aim_vector = number_attribute.createPoint('aimVector', 'aim')
	number_attribute.setArray(False)
	number_attribute.setStorable(True)
	number_attribute.setConnectable(False)
	number_attribute.setKeyable(False)
	# up_vector
	CurveIk.up_vector = number_attribute.createPoint('upVector', 'up')
	number_attribute.setArray(False)
	number_attribute.setStorable(True)
	number_attribute.setConnectable(False)
	number_attribute.setKeyable(False)

	# aim_mode tangent/next point
	CurveIk.aim_mode = enum_attribute.create('aimMode', 'mode')
	enum_attribute.addField('tangent', 0)
	enum_attribute.addField('next point', 1)

	# chain parameter
	CurveIk.node_number = number_attribute.create('nodeNumber', 'num', OpenMaya.MFnNumericData.kInt, 5)
	number_attribute.setArray(False)
	number_attribute.setStorable(True)
	number_attribute.setConnectable(False)
	number_attribute.setKeyable(False)

	# stretch
	CurveIk.stretch = number_attribute.create('stretch', 'stretch', OpenMaya.MFnNumericData.kFloat, 1)
	number_attribute.setMax(1)
	number_attribute.setMin(0)
	number_attribute.setArray(False)
	number_attribute.setStorable(True)
	number_attribute.setConnectable(True)
	number_attribute.setKeyable(True)
	number_attribute.setDisconnectBehavior(OpenMaya.MFnNumericAttribute.kNothing)

	# stretch clamp
	CurveIk.stretch_clamp = number_attribute.create('stretchClamp', 'clamp', OpenMaya.MFnNumericData.kBoolean, 0)
	number_attribute.setArray(False)
	number_attribute.setStorable(True)
	number_attribute.setConnectable(False)
	number_attribute.setKeyable(False)

	# stretch limit
	CurveIk.stretch_limit = number_attribute.create('stretchClamp', 'stretchClamp', OpenMaya.MFnNumericData.kFloat, 2)
	number_attribute.setMin(1)
	number_attribute.setArray(False)
	number_attribute.setStorable(True)
	number_attribute.setConnectable(True)
	number_attribute.setKeyable(True)
	number_attribute.setDisconnectBehavior(OpenMaya.MFnNumericAttribute.kNothing)

	# slide
	CurveIk.slide = number_attribute.create('slide', 'slide', OpenMaya.MFnNumericData.kFloat, 1)
	number_attribute.setMax(1)
	number_attribute.setMin(0)
	number_attribute.setArray(False)
	number_attribute.setStorable(True)
	number_attribute.setConnectable(True)
	number_attribute.setKeyable(True)

	# curve world matrix
	CurveIk.curve_world_matrix = matrix_attribute.create('curveWorldMatrix', 'cwm', OpenMaya.MFnMatrixAttribute.kFloat)

	# ik type spline/ribbon
	CurveIk.ik_type = enum_attribute.create('ikType', 'ik')
	enum_attribute.addField('spline', 0)
	enum_attribute.addField('ribbon', 1)

	# spline
	CurveIk.start_matrix = matrix_attribute.create('startMatrix', 'start', OpenMaya.MFnMatrixAttribute.kFloat)
	CurveIk.end_matrix = matrix_attribute.create('endMatrix', 'end', OpenMaya.MFnMatrixAttribute.kFloat)

	CurveIk.sections = number_attribute.create('sections', 'sections', OpenMaya.MFnNumericData.kInt, 3)
	number_attribute.setMin(1)
	number_attribute.setArray(False)
	number_attribute.setStorable(True)
	number_attribute.setConnectable(False)
	number_attribute.setKeyable(False)

	CurveIk.twist_ramp = ramp_attribute.createCurveRamp('twistRamp', 'tr')
	CurveIk.twist_section_ramp = ramp_attribute.createCurveRamp('twistSectionRamp', 'tsr')

	# output
	CurveIk.output = matrix_attribute.create('output', 'o', OpenMaya.MFnMatrixAttribute.kFloat)
	matrix_attribute.setArray(True)
	matrix_attribute.setStorable(True)
	matrix_attribute.setUsesArrayDataBuilder(True)

	# add attributes
	CurveIk.addAttribute(CurveIk.input_curve)
	CurveIk.addAttribute(CurveIk.up_curve)
	CurveIk.addAttribute(CurveIk.side_curve)
	CurveIk.addAttribute(CurveIk.aim_vector)
	CurveIk.addAttribute(CurveIk.up_vector)
	CurveIk.addAttribute(CurveIk.aim_mode)
	CurveIk.addAttribute(CurveIk.node_number)
	CurveIk.addAttribute(CurveIk.stretch)
	CurveIk.addAttribute(CurveIk.stretch_clamp)
	CurveIk.addAttribute(CurveIk.stretch_limit)
	CurveIk.addAttribute(CurveIk.slide)
	CurveIk.addAttribute(CurveIk.curve_world_matrix)
	CurveIk.addAttribute(CurveIk.ik_type)
	CurveIk.addAttribute(CurveIk.start_matrix)
	CurveIk.addAttribute(CurveIk.end_matrix)
	CurveIk.addAttribute(CurveIk.sections)
	CurveIk.addAttribute(CurveIk.twist_ramp)
	CurveIk.addAttribute(CurveIk.twist_section_ramp)
	CurveIk.addAttribute(CurveIk.output)

	# attr affects


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


