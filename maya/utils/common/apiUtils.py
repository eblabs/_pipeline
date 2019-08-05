# IMPORT PACKAGES

# import maya packages
import maya.api.OpenMaya as OpenMaya

# import math
import math

# import utils
import variables


# FUNCTION
def get_MObj(node):
    """
    Args:
        node (str): maya node name

    Returns:
        MObject
    """

    selection = OpenMaya.MSelectionList()
    selection.add(node)
    MObj = selection.getDependNode(0)
    return MObj


def get_MDagPath(node):
    """
    Args:
        node (str): maya node name

    Returns:
        MDagPath
    """

    selection = OpenMaya.MSelectionList()
    selection.add(node)
    MDagPath = selection.getDagPath(0)
    return MDagPath


def convert_MPointArray_to_list(MPointArray):
    """
    Args:
        MPointArray (MPointArray): input MPointArray

    Returns:
        point_list(list)
    """

    point_list = []
    for i in range(len(MPointArray)):
        point_list.append([MPointArray[i].x,
                           MPointArray[i].y,
                           MPointArray[i].z])
    return point_list


def convert_MDoubleArray_to_list(MDoubleArray):
    """
    Args:
        MDoubleArray (MDoubleArray): input MDoubleArray

    Returns:
        array_list(list)
    """

    array_list = []
    for i in range(len(MDoubleArray)):
        array_list.append(MDoubleArray[i])
    return array_list


def compose_matrix(**kwargs):
    """
    compose matrix with transform information

    Keyword Args:
        translate(list): input translate, default is [0, 0, 0]
        rotate(list): input rotate, default is [0, 0, 0]
        scale(list): input scale, default is [1, 1, 1]
        rotate_order(int): input rotate order, default is 0

    Returns:
        matrix(list)
    """

    # vars
    translate = variables.kwargs('translate', [0, 0, 0], kwargs, short_name='t')
    rotate = variables.kwargs('rotate', [0, 0, 0], kwargs, short_name='r')
    scale = variables.kwargs('scale', [1, 1, 1], kwargs, short_name='s')
    rotate_order = variables.kwargs('rotate_order', 0, kwargs, short_name='ro')

    # create MMatrix object
    MTransformationMatrix = OpenMaya.MTransformationMatrix()

    # create MVector for translation
    MVector = OpenMaya.MVector(translate[0], translate[1], translate[2])

    # create MDoubleArray for rotation
    MRotate = OpenMaya.MEulerRotation(math.radians(rotate[0]),
                                      math.radians(rotate[1]),
                                      math.radians(rotate[2]),
                                      rotate_order)

    # set MMatrix
    MTransformationMatrix.setTranslation(MVector, OpenMaya.MSpace.kWorld)
    MTransformationMatrix.setRotation(MRotate)
    MTransformationMatrix.setScale(scale, OpenMaya.MSpace.kWorld)

    # get MMatrix
    MMatrix = MTransformationMatrix.asMatrix()

    matrix = convert_MMatrix_to_list(MMatrix)

    return matrix


def decompose_matrix(matrix, **kwargs):
    """
    decompose input matrix to transform information

    Args:
        matrix(list): input matrix

    Keyword Args:
        rotate_order(int): input rotate order, default is 0

    Returns:
        [translate, rotate, scale](list)
    """

    # vars
    rotate_order = variables.kwargs('rotate_order', 0, kwargs, short_name='ro')

    # convert input matrix to MMatrix
    MMatrix = OpenMaya.MMatrix(matrix)

    # get MTransformationMatrix from MMatrix
    MTransformationMatrix = OpenMaya.MTransformationMatrix(MMatrix)

    # get MTranslate, MRotate, scale
    MTranslate = MTransformationMatrix.translation(OpenMaya.MSpace.kWorld)
    MRotate = MTransformationMatrix.rotation(asQuaternion=False)
    MRotate.reorderIt(rotate_order)
    scale = MTransformationMatrix.scale(OpenMaya.MSpace.kWorld)

    # get transform information
    translate = [MTranslate.x, MTranslate.y, MTranslate.z]
    rotate = [math.degrees(MRotate.x), math.degrees(MRotate.y), math.degrees(MRotate.z)]

    return [translate, rotate, scale]


def convert_MMatrix_to_list(MMatrix):
    """
    Args:
        MMatrix (MMatrix): input MMatrix

    Returns:
        matrix(list)
    """

    matrix = []
    for i in range(4):
        for j in range(4):
            matrix.append(MMatrix.getElement(i, j))
    return matrix
