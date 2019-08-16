# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

# import utils
import utils.common.attributes as attributes
import utils.common.apiUtils as apiUtils
import utils.common.variables as variables
import utils.common.hierarchy as hierarchy
import utils.common.logUtils as logUtils

# CONSTANT
logger = logUtils.logger


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

    Returns:
        transform, shape node
    """
    # vars
    degree = variables.kwargs('degree', 1, kwargs, short_name='d')
    form = variables.kwargs('form', 1, kwargs)

    if not cmds.objExists(name):
        cmds.createNode('transform', name=name)

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
    crv = cmds.curve(d=1, p=[[0, 0, 0], [0, 0, 0]], name=name)
    # rename curve's shape node, maya doesn't rename the shape node on creation
    crv_shape = cmds.listRelatives(crv, s=True)[0]
    crv_shape = cmds.rename(crv_shape, crv+'Shape')

    if reference:
        cmds.setAttr(crv_shape+'.overrideEnabled', 1)
        cmds.setAttr(crv_shape+'.overrideDisplayType', 2)
    attributes.lock_hide_attrs(crv, attributes.Attr.all)

    hierarchy.parent_node(crv, parent) # parent curve to the given transform

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
        curve: nurbs curve shape node

    Returns:
        curve_info(dict): curve shape node information
                          include: {name, control_vertices, knots, degree, form}
    """
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
        curve(str): curve shape node
        points(list): curve cv positions
    """
    MPointArray = OpenMaya.MPointArray(points)

    # get MFnNurbsCurve
    MFnNurbsCurve = _get_MFnNurbsCurve(curve)

    # set pos
    MFnNurbsCurve.setCVPositions(MPointArray)


# SUB FUNCTION
def _get_MFnNurbsCurve(curve):
    """
    get MFnNurbsCurve

    Args:
        curve(str): curve's shape node name

    Returns:
        MFnNurbsCurve
    """
    MDagPath = apiUtils.get_MDagPath(curve)
    MFnCurve = OpenMaya.MFnNurbsCurve(MDagPath)
    return MFnCurve
