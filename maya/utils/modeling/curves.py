# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

# import os
import os

# import utils
import utils.common.files as files
import utils.common.attributes as attributes
import utils.common.apiUtils as apiUtils
import utils.common.mathUtils as mathUtils
import utils.common.variables as variables
import utils.common.transforms as transforms
import utils.common.hierarchy as hierarchy
import utils.common.logUtils as logUtils

# CONSTANT
logger = logUtils.logger
CURVE_INFO_FORMAT = '.crvInfo'


#    FUNCTION
def create_curve(name, control_vertices, knots, **kwargs):
    """
    create curve with given information

    Args:
        name(str): curve name
        control_vertices(list): control vertices
        knots(list): knots

    Keyword Args:
        degree(int): curve's degree, default is 1
        form(int): curve's form, default is 1
        parent(str): parent curve to the given node

    Returns:
        transform, shape node
    """
    # vars
    degree = variables.kwargs('degree', 1, kwargs, short_name='d')
    form = variables.kwargs('form', 1, kwargs)
    parent = variables.kwargs('parent', None, kwargs, short_name='p')

    if not cmds.objExists(name):
        cmds.createNode('transform', name=name)

    hierarchy.parent_node(name, parent)

    MObj = apiUtils.get_MObj(name)
    MFnNurbsCurve = OpenMaya.MFnNurbsCurve()
    MObj = MFnNurbsCurve.create(control_vertices, knots, degree, form, False, True, MObj)

    # rename shape
    MDagPath = OpenMaya.MDagPath.getAPathTo(MObj)
    shape = MDagPath.partialPathName()
    shape = cmds.rename(shape, name+'Shape')

    return name, shape


def create_guide_line(name, attrs, reference=True, parent=None):
    """
    create guide line

    Args:
        name(str): guide line's name
        attrs(list): input connections to the cv points
                     example: [['node1.tx', 'node1.ty', 'node1.tz'], ['node2.tx', 'node2.ty', 'node2.tz']]

    Keyword Args:
        reference(bool): if set shape to reference, default is True
        parent(str): parent guide line to the given node

    Returns:
        curve(str): guide line's transform
    """
    # create guide line curve
    crv = cmds.curve(degree=1, point=[[0, 0, 0], [0, 0, 0]], name=name)
    # rename curve's shape node, maya doesn't rename the shape node on creation
    crv_shape = cmds.listRelatives(crv, shapes=True)[0]
    crv_shape = cmds.rename(crv_shape, crv+'Shape')

    if reference:
        cmds.setAttr(crv_shape+'.overrideEnabled', 1)
        cmds.setAttr(crv_shape+'.overrideDisplayType', 2)
    attributes.lock_hide_attrs(crv, attributes.Attr.all)

    hierarchy.parent_node(crv, parent)  # parent curve to the given transform

    # connect curve with given inputs
    attributes.connect_attrs(attrs[0]+attrs[1],
                             [crv_shape+'.controlPoints[0].xValue',
                              crv_shape+'.controlPoints[0].yValue',
                              crv_shape+'.controlPoints[0].zValue',
                              crv_shape+'.controlPoints[1].xValue',
                              crv_shape+'.controlPoints[1].yValue',
                              crv_shape+'.controlPoints[1].zValue'])

    return crv


def create_curve_on_nodes(name, nodes, degree=3, parent=None):
    """
    create curve on given nodes

    Args:
        name(str): curve's name
        nodes(list): given nodes, can be node name or transform values, should have at least two nodes

    Keyword Args:
        degree(int): curve's degree, default is 3
        parent(str): curve's parent node

    Returns:
        curve(str)
    """
    pos_list = []
    for n in nodes:
        if isinstance(n, basestring):
            pos = cmds.xform(n, q=True, t=True, ws=True)  # get transform information
            pos_list.append(pos)
        else:
            pos_list.append(n)

    if len(pos_list) == 2:
        # degree can only be 1
        degree = 1
    elif len(pos_list) == 3 and degree > 2:
        # set degree to 2
        degree = 2

    # create curve and rename shape node
    crv = cmds.curve(p=pos_list, d=degree, name=name)
    crv_shape = cmds.listRelatives(crv, s=True)[0]
    cmds.rename(crv_shape, crv+'Shape')

    # parent curve to given transform node
    hierarchy.parent_node(crv, parent)

    return crv


def get_curve_info(curve):
    """
    get curve shape info

    Args:
        curve: nurbs curve shape node/transform node

    Returns:
        curve_info(dict): curve shape node information
                          include: {name, control_vertices, knots, degree, form}
    """
    if cmds.objectType(curve) == 'nurbsCurve':
        curve = cmds.listRelatives(curve, parent=True)[0]

    MFnCurve = _get_MFnNurbsCurve(curve)

    MPntArray_cvs = MFnCurve.cvPositions(OpenMaya.MSpace.kObject)
    MDoubleArray_knots = MFnCurve.knots()

    degree = MFnCurve.degree

    form = MFnCurve.form

    control_vertices = apiUtils.convert_MPointArray_to_list(MPntArray_cvs)
    knots = apiUtils.convert_MDoubleArray_to_list(MDoubleArray_knots)

    curve_info = {'name': curve,
                  'control_vertices': control_vertices,
                  'knots': knots,
                  'degree': degree,
                  'form': form}

    return curve_info


def set_curve_points(curve, points):
    """
    set curve shape points positions

    Args:
        curve(str): curve shape node or transform node
        points(list): curve cv positions
    """
    MPointArray = OpenMaya.MPointArray(points)

    # get MFnNurbsCurve
    MFnNurbsCurve = _get_MFnNurbsCurve(curve)

    # set pos
    MFnNurbsCurve.setCVPositions(MPointArray)


def export_curves_info(curves, path, name='curvesInfo'):
    """
    export curves information to the given path
    curve information contain curve's name, curve's world matrix and shape info

    Args:
        curves(list/str): curves need to be exported
        path(str): given path
    Keyword Args:
        name(str): export curves info file name, default is curvesInfo
    Returns:
        curves_info_path(str): exported path, return None if nothing to be exported
    """
    if isinstance(curves, basestring):
        curves = [curves]

    curves_info = {}

    for crv in curves:
        if cmds.objExists(crv):
            crv_shape = cmds.listRelatives(crv, shapes=True)
            if crv_shape:
                crv_shape = crv_shape[0]
                # get shape info
                shape_info = get_curve_info(crv_shape)
                matrix_world = cmds.getAttr(crv+'.worldMatrix[0]')
                curves_info.update({crv: {'world_matrix': matrix_world,
                                          'shape': shape_info}})

    # check if has curves info
    if curves_info:
        # compose path
        curves_info_path = os.path.join(path, name + CURVE_INFO_FORMAT)
        files.write_json_file(curves_info_path, curves_info)
        logger.info('export curves info successfully at {}'.format(curves_info_path))
        return curves_info_path
    else:
        logger.warning('nothing to be exported, skipped')
        return None


def build_curves_from_curves_info(curves_info, parent_node=None):
    """
    build curves base on curves info data in the scene

    Args:
        curves_info(dict): curves information
        parent_node(str): parent curves to the given node, default is None
    """
    for crv, crv_info in curves_info.iteritems():
        if not cmds.objExists(crv):
            # decompose matrix
            transform_info = apiUtils.decompose_matrix(crv_info['world_matrix'])
            # create curve
            crv, crv_shape = create_curve(crv_info['shape']['name'], crv_info['shape']['control_vertices'],
                                          crv_info['shape']['knots'], degree=crv_info['shape']['degree'],
                                          form=crv_info['shape']['form'])
            # set pos
            transforms.set_pos(crv, transform_info, set_scale=True)
            # parent node
            hierarchy.parent_node(crv, parent_node)


def load_curves_info(path, name='curvesInfo', parent_node=None):
    """
    load curves information from given path and build the curves in the scene
    Args:
        path(str): given curves info file path
    Keyword Args:
        name(str): curves info file name, default is curvesInfo
        parent_node(str): parent curves to the given node, default is None
    """
    # get path
    curves_info_path = os.path.join(path, name+CURVE_INFO_FORMAT)
    if os.path.exists(curves_info_path):
        curves_info = files.read_json_file(curves_info_path)
        build_curves_from_curves_info(curves_info, parent_node=parent_node)
        # log info
        logger.info('build curves base on given curves info file: {}'.format(curves_info_path))
    else:
        logger.warning('given path: {} does not exist, skipped'.format(curves_info_path))


def get_closest_point_on_curve(curve, pos, space='world'):
    """
    get closest point on the given curve

    Args:
        curve(str): nurbs curve
        pos(str/list): given transform node or position
    Keyword Args:
        space(str): world/object

    Returns:
        pos_on_curve(list): closest point position on curve
        parameter(float): closest point's parameter on curve
    """
    if space == 'world':
        space = OpenMaya.MSpace.kWorld
    else:
        space = OpenMaya.MSpace.kObject
    if isinstance(pos, basestring):
        pos = cmds.xform(pos, query=True, translation=True, worldSpace=True)

    MPoint = OpenMaya.MPoint(pos)
    MFnCurve = _get_MFnNurbsCurve(curve)

    if not MFnCurve.isPointOnCurve(MPoint):
        # given pos is not on curve
        # find closest point
        MPoint, param = MFnCurve.closestPoint(MPoint, space=space)
    else:
        param = MFnCurve.getParamAtPoint(MPoint, space=space)

    pos = [MPoint.x, MPoint.y, MPoint.z]

    return pos, param


def get_tangent_at_param(curve, param):
    """
    get tangent vector at given parameter

    Args:
        curve(str): nurbs curve
        param(float): curve's parameter

    Returns:
        tangent(list)
    """
    MFnCurve = _get_MFnNurbsCurve(curve)
    tangent = MFnCurve.tangent(param)
    return tangent


def get_point_on_parameter(curve, parameter, space='world'):
    """
    get point position on curve's parameter

    Args:
        curve(str)
        parameter(float)
    Keyword Args:
        space(str): object/world

    Returns:
        pos(list)
    """
    # get space
    if space == 'world':
        space = OpenMaya.MSpace.kWorld
    else:
        space = OpenMaya.MSpace.kObject

    # get MFnNurbsCurve object
    MFnCurve = _get_MFnNurbsCurve(curve)
    MPoint = MFnCurve.getPointAtParam(parameter)

    return [MPoint.x, MPoint.y, MPoint.z]


def get_matrices_along_curve(curve, nodes_number, aim_vector=None, up_vector=None, up_curve=None,
                             rotation_up_vector=None, uniform_type='length', aim_type='tangent', flip_check=True):
    """
    get matrices along the given curve uniformly.

    Args:
        curve(str): given curve
        nodes_number(int)
    Keyword Args:
        aim_vector(list)
        up_vector(list)
        up_curve(str): if need nodes to aim along a specific curve
        rotation_up_vector(list): if no up curve specific, it will take this vector as reference for up direction
        uniform_type(str): length/parameter, place transforms uniformly based on distance or parameter,
                           curve's parameter can be stretched in some cases, parameter may not place nodes equally
        aim_type(str): tangent/next/None, aim type of each point, will be based on curve's tangent, or aim to the next
                       point, or keep in world orientation
        flip_check(bool): will automatically fix flipping transform if set to True

    Returns:
        matrices(list): list of output matrices
    """
    # aim vector
    if not aim_vector:
        aim_vector = [1, 0, 0]
    # up vector
    if not up_vector:
        up_vector = [0, 1, 0]

    MFnCurve = _get_MFnNurbsCurve(curve)  # get MFnCurve object
    # get curve length
    crv_length = MFnCurve.length()
    # get curve length per segment
    segment_length = crv_length/(nodes_number-1)
    # get curve min and max value
    min_max_val = MFnCurve.knotDomain
    # get parameter distance
    param_dis = min_max_val[1] - min_max_val[0]
    # get parameter per segment
    param_segment = param_dis/(nodes_number-1)

    # up curve
    if up_curve and cmds.objExists(up_curve):
        # get MFnCurve object for up curve
        MFnCurve_up = _get_MFnNurbsCurve(up_curve)
        crv_length_up = MFnCurve_up.length()
        segment_length_up = crv_length_up/(nodes_number-1)
        min_max_val_up = MFnCurve_up.knotDomain
        param_dis_up = min_max_val_up[1] - min_max_val_up[0]
        param_segment_up = param_dis_up/(nodes_number-1)
    else:
        MFnCurve_up = None
        segment_length_up = None
        param_segment_up = None

    matrix_list = []  # matrix info for each transform
    third_vec_previous = []  # hold previous third vector to check flip
    for i in range(nodes_number):
        if uniform_type == 'length':
            # get parameter at length
            param = MFnCurve.findParamFromLength(i*segment_length)
            param_next = MFnCurve.findParamFromLength((i+1)*segment_length)
        else:
            param = i*param_segment
            param_next = (i+1)*param_segment
        # get pos
        pos = MFnCurve.getPointAtParam(param, space=OpenMaya.MSpace.kWorld)
        pos_node = [pos.x, pos.y, pos.z]
        if not aim_type or aim_type == 'None':
            # no need to calculate rotation
            matrix = apiUtils.compose_matrix(translate=pos_node)
            matrix_list.append(matrix)
        else:
            # calculate rotation
            # check aim vector
            if aim_type == 'tangent':
                aim_vec_param = MFnCurve.tangent(param)
            else:
                if i < nodes_number-1:
                    # not the end node
                    # get next point position
                    pos_next = MFnCurve.getPointAtParam(param_next, space=OpenMaya.MSpace.kWorld)
                    pos_next = [pos_next.x, pos_next.y, pos_next.z]
                    aim_vec_param = mathUtils.get_vector_from_points(pos_next, pos_node, normalize=True)
                else:
                    aim_vec_param = MFnCurve.tangent(param)  # end node doesn't have next point, use tangent

            # check up vector
            if up_curve and cmds.objExists(up_curve):
                # get point on up curve
                if uniform_type == 'length':
                    param_up = MFnCurve_up.findParamFromLength(i*segment_length_up)
                else:
                    param_up = i*param_segment_up
                # get pos
                pos_up = MFnCurve.getPointAtParam(param, space=OpenMaya.MSpace.kWorld)
                pos_node_up = [pos_up.x, pos_up.y, pos_up.z]
                aim_vec_up_dir = mathUtils.get_vector_from_points(pos_node_up, pos_node, normalize=True)
            else:
                aim_vec_up_dir = rotation_up_vector

            aim_vec_param, up_vec, third_vec = mathUtils.build_coordinate_system(aim_vec_param, aim_vec_up_dir,
                                                                                 flip_check_vec=third_vec_previous)
            if flip_check:
                third_vec_previous = third_vec

            # compose matrix
            matrix_orient = mathUtils.four_by_four_matrix(aim_vec_param, up_vec, third_vec, pos_node)

            # get aim vector's matrix
            aim_vec_axis, up_vec_axis, third_vec_axis = mathUtils.build_coordinate_system(aim_vector, up_vector)
            matrix_aim = mathUtils.four_by_four_matrix(aim_vec_axis, up_vec_axis, third_vec_axis, [0, 0, 0])

            # get node matrix by matrix_aim.inverse * matrix_orient
            matrix_aim_inverse = mathUtils.inverse_matrix(matrix_aim)
            matrix_node = mathUtils.mult_matrix([matrix_aim_inverse, matrix_orient])

            matrix_list.append(matrix_node)

    return matrix_list


# SUB FUNCTION
def _get_MFnNurbsCurve(curve):
    """
    get MFnNurbsCurve

    Args:
        curve(str): curve's shape node name

    Returns:
        MFnNurbsCurve
    """
    # get curve shape
    if cmds.objectType(curve) == 'transform':
        curve_shape = cmds.listRelatives(curve, shapes=True)[0]
    else:
        curve_shape = curve
    MDagPath = apiUtils.get_MDagPath(curve_shape)
    MFnCurve = OpenMaya.MFnNurbsCurve(MDagPath)
    return MFnCurve
