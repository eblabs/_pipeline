# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

# import os
import os

# import utils
import utils.common.files as files
import utils.common.apiUtils as apiUtils
import utils.common.variables as variables
import utils.common.transforms as transforms
import utils.common.hierarchy as hierarchy
import utils.common.logUtils as logUtils

# CONSTANT
logger = logUtils.logger
SURF_INFO_FORMAT = '.surfInfo'


# FUNCTION
def create_surface(name, control_vertices, u_knot_sequences, v_knot_sequences, **kwargs):
    """
    create nurbes surface with given information
    Args:
        name(str): surface name
        control_vertices(list): control vertices
        u_knot_sequences(list): u knots
        v_knot_sequences(list): v knots
    Keyword Args:
        degree_u(int): degree of first set of basis functions, default is 1
        degree_v(int): degree of second set of basis functions, default is 1
        form_u(int): surface's form u, default is 1
        form_v(int): surface's form v, default is 1
        parent(str): parent surface to the given node

    Returns:
        transform, shape node
    """
    # vars
    degree_u = variables.kwargs('degree_u', 1, kwargs)
    degree_v = variables.kwargs('degree_v', 1, kwargs)
    form_u = variables.kwargs('form_u', 1, kwargs)
    form_v = variables.kwargs('form_v', 1, kwargs)
    uv_count = variables.kwargs('uv_count', None, kwargs)
    uv_ids = variables.kwargs('uv_ids', None, kwargs)
    parent = variables.kwargs('parent', None, kwargs, short_name='p')

    if not cmds.objExists(name):
        cmds.createNode('transform', name=name)

    hierarchy.parent_node(name, parent)

    MObj = apiUtils.get_MObj(name)
    MFnNurbsSurface = OpenMaya.MFnNurbsSurface()
    MObj = MFnNurbsSurface.create(control_vertices, u_knot_sequences, v_knot_sequences, degree_u, degree_v,
                                  form_u, form_v, True, MObj)

    # assign shader
    cmds.sets(name, edit=True, forceElement='initialShadingGroup')

    # rename shape
    MDagPath = OpenMaya.MDagPath.getAPathTo(MObj)
    shape = MDagPath.partialPathName()
    shape = cmds.rename(shape, name+'Shape')

    return name, shape


def get_surface_info(surface):
    """
    get surface shape info
    Args:
        surface(str): surface shape node/transform node

    Returns:
        surface_info(dict): surface shape node information
                            include: {name, control_vertices, u_knot_sequences, v_knot_sequences, degree_u, degree_v,
                                      form_u, form_v, uv_count, uv_ids}
    """
    if cmds.objectType(surface) == 'transform':
        surface_shape = cmds.listRelatives(surface, shapes=True)[0]
    else:
        surface_shape = surface
        surface = cmds.listRelatives(surface, parent=True)[0]

    MFnSurface = _get_MFnNurbsSurface(surface_shape)  # set MFnNurbsSurface to query

    MPntArray_cvs = MFnSurface.cvPositions(OpenMaya.MSpace.kObject)
    MDoubleArray_knots_u = MFnSurface.knotsInU()
    MDoubleArray_knots_v = MFnSurface.knotsInV()

    degree_u = MFnSurface.degreeInU
    degree_v = MFnSurface.degreeInV

    form_u = MFnSurface.formInU
    form_v = MFnSurface.formInV

    control_vertices = apiUtils.convert_MPointArray_to_list(MPntArray_cvs)
    knots_u = apiUtils.convert_MDoubleArray_to_list(MDoubleArray_knots_u)
    knots_v = apiUtils.convert_MDoubleArray_to_list(MDoubleArray_knots_v)

    # uv_count = apiUtils.convert_MDoubleArray_to_list(MIntArray_uv_count)
    # uv_ids = apiUtils.convert_MDoubleArray_to_list(MIntArray_uv_ids)

    surface_info = {'name': surface,
                    'control_vertices': control_vertices,
                    'u_knot_sequences': knots_u,
                    'v_knot_sequences': knots_v,
                    'degree_u': degree_u,
                    'degree_v': degree_v,
                    'form_u': form_u,
                    'form_v': form_v}

    return surface_info


def export_surfaces_info(surfaces, path, name='surfacesInfo'):
    """
    export surfaces information to the given path
    surface information contain surface's name, surface's world matrix and shape info

    Args:
        surfaces(list/str): surfaces need to be exported
        path(str): given path
    Keyword Args:
        name(str): export surfaces info file name, default is surfacesInfo
    Returns:
        surfaces_info_path(str): exported path, return None if nothing to be exported
    """
    if isinstance(surfaces, basestring):
        surfaces = [surfaces]

    surfaces_info = {}

    for surf in surfaces:
        if cmds.objExists(surf):
            surf_shape = cmds.listRelatives(surf, shapes=True)
            if surf_shape:
                surf_shape = surf_shape[0]
                # get shape info
                shape_info = get_surface_info(surf_shape)
                matrix_world = cmds.getAttr(surf+'.worldMatrix[0]')
                surfaces_info.update({surf: {'world_matrix': matrix_world,
                                             'shape': shape_info}})

    # check if has surfaces info
    if surfaces_info:
        # compose path
        surfaces_info_path = os.path.join(path, name+SURF_INFO_FORMAT)
        files.write_json_file(surfaces_info_path, surfaces_info)
        logger.info('export surfaces info successfully at {}'.format(surfaces_info_path))
        return surfaces_info_path
    else:
        logger.warning('nothing to be exported, skipped')
        return None


def build_surfaces_from_surfaces_info(surfaces_info, parent_node=None):
    """
    build surfaces base on surfaces info data in the scene

    Args:
        surfaces_info(dict): surfaces information
        parent_node(str): parent surfaces to the given node, default is None
    """
    for surf, surf_info in surfaces_info.iteritems():
        if not cmds.objExists(surf):
            # decompose matrix
            transform_info = apiUtils.decompose_matrix(surf_info['world_matrix'])
            # create curve
            surf, surf_shape = create_surface(surf_info['shape']['name'], surf_info['shape']['control_vertices'],
                                              surf_info['shape']['u_knot_sequences'],
                                              surf_info['shape']['v_knot_sequences'],
                                              degree_u=surf_info['shape']['degree_u'],
                                              degree_v=surf_info['shape']['degree_v'],
                                              form_u=surf_info['shape']['form_u'], form_v=surf_info['shape']['form_v'])
            # set pos
            transforms.set_pos(surf, transform_info, set_scale=True)
            # parent node
            hierarchy.parent_node(surf, parent_node)


def load_surfaces_info(path, name='surfacesInfo', parent_node=None):
    """
    load surfaces information from given path and build the surfaces in the scene
    Args:
        path(str): given surfaces info file path
    Keyword Args:
        name(str): surfaces info file name, default is surfacesInfo
        parent_node(str): parent surfaces to the given node, default is None
    """
    # get path
    surfaces_info_path = os.path.join(path, name+SURF_INFO_FORMAT)
    if os.path.exists(surfaces_info_path):
        surf_info = files.read_json_file(surfaces_info_path)
        build_surfaces_from_surfaces_info(surf_info, parent_node=parent_node)
        # log info
        logger.info('build surfaces base on given surfaces info file: {}'.format(surfaces_info_path))
    else:
        logger.warning('given path: {} does not exist, skipped'.format(surfaces_info_path))


# SUB FUNCTION
def _get_MFnNurbsSurface(surface):
    """
    get MFnNurbsSurface

    Args:
        surface(str): surface's shape node name

    Returns:
        MFnNurbsSurface
    """
    MDagPath = apiUtils.get_MDagPath(surface)
    MFnSurface = OpenMaya.MFnNurbsSurface(MDagPath)
    return MFnSurface
