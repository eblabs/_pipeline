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
import utils.common.variables as variables
import utils.common.transforms as transforms
import utils.common.hierarchy as hierarchy
import utils.common.logUtils as logUtils

# CONSTANT
logger = logUtils.logger
MESH_INFO_FORMAT = '.meshInfo'


#    FUNCTION
def create_mesh(name, points, poly_count, poly_connects, u_values, v_values, **kwargs):
    """
    create mesh with given information
    Args:
        name(str): mesh name
        points(list): vertex array of the mesh
        poly_count(list): array of vertex counts for each polygon
        poly_connects(list): array of vertex connections for each polygon
        u_values(list): the array of u values to be set
        v_values(list): the array of v values to be set
    Keyword Args:
        uv_count(list): the uv counts for each patch in the surface, default is None
        uv_ids(list): the uv indices to be mapped to each patch-corner, default is None
        parent(str): parent surface to the given node

     Returns:
        transform, shape node
    """
    # vars
    uv_count = variables.kwargs('uv_count', None, kwargs)
    uv_ids = variables.kwargs('uv_ids', None, kwargs)
    parent = variables.kwargs('parent', None, kwargs, short_name='p')

    if not cmds.objExists(name):
        cmds.createNode('transform', name=name)

    hierarchy.parent_node(name, parent)

    MObj = apiUtils.get_MObj(name)
    MFnMesh = OpenMaya.MFnMesh()
    MObj = MFnMesh.create(OpenMaya.MPointArray(points), poly_count, poly_connects, uValues=u_values, vValues=v_values,
                          parent=MObj)

    if uv_count and uv_ids:
        MFnMesh.assignUVs(uv_count, uv_ids)

    # assign shader
    cmds.sets(name, edit=True, forceElement='initialShadingGroup')

    # rename shape
    MDagPath = OpenMaya.MDagPath.getAPathTo(MObj)
    shape = MDagPath.partialPathName()
    shape = cmds.rename(shape, name+'Shape')

    return name, shape


def get_mesh_info(mesh):
    """
    get mesh shape info
    Args:
        mesh(str): mesh shape node/transform node

    Returns:
        mesh_info(dict): mesh shape node information
                         include: {name, points, poly_count, poly_connects, u_values,
                                   v_values, uv_count, uv_ids, normals}
    """
    if cmds.objectType(mesh) == 'transform':
        mesh_shape = cmds.listRelatives(mesh, shapes=True)[0]
    else:
        mesh_shape = mesh
        mesh = cmds.listRelatives(mesh, parent=True)[0]

    MFnMesh = _get_MFnMesh(mesh_shape)  # set MFnMesh to query

    MPntArray_points = MFnMesh.getPoints(space=OpenMaya.MSpace.kObject)
    MIntArray_poly_count, MIntArray_poly_connects = MFnMesh.getVertices()
    MFloatArray_u, MFloatArray_v = MFnMesh.getUVs()
    MIntArray_uv_count, MIntArray_uv_ids = MFnMesh.getAssignedUVs()

    points = apiUtils.convert_MPointArray_to_list(MPntArray_points)
    poly_count = apiUtils.convert_MDoubleArray_to_list(MIntArray_poly_count)
    poly_connects = apiUtils.convert_MDoubleArray_to_list(MIntArray_poly_connects)
    u_values = apiUtils.convert_MDoubleArray_to_list(MFloatArray_u)
    v_values = apiUtils.convert_MDoubleArray_to_list(MFloatArray_v)

    uv_count = apiUtils.convert_MDoubleArray_to_list(MIntArray_uv_count)
    uv_ids = apiUtils.convert_MDoubleArray_to_list(MIntArray_uv_ids)

    mesh_info = {'name': mesh,
                 'points': points,
                 'poly_count': poly_count,
                 'poly_connects': poly_connects,
                 'u_values': u_values,
                 'v_values': v_values,
                 'uv_count': uv_count,
                 'uv_ids': uv_ids}

    return mesh_info


def export_meshes_info(meshes, path, name='meshesInfo'):
    """
    export meshes information to the given path
    mesh information contain mesh's name, mesh's world matrix and shape info

    Args:
        meshes(list/str): meshes need to be exported
        path(str): given path
    Keyword Args:
        name(str): export meshes info file name, default is meshesInfo
    Returns:
        meshes_info_path(str): exported path, return None if nothing to be exported
    """
    if isinstance(meshes, basestring):
        meshes = [meshes]

    meshes_info = {}

    for msh in meshes:
        if cmds.objExists(msh):
            msh_shape = cmds.listRelatives(msh, shapes=True)
            if msh_shape:
                msh_shape = msh_shape[0]
                # get shape info
                shape_info = get_mesh_info(msh_shape)
                matrix_world = cmds.getAttr(msh+'.worldMatrix[0]')
                meshes_info.update({msh: {'world_matrix': matrix_world,
                                          'shape': shape_info}})

    # check if has meshes info
    if meshes_info:
        # compose path
        meshes_info_path = os.path.join(path, name+MESH_INFO_FORMAT)
        files.write_json_file(meshes_info_path, meshes_info)
        logger.info('export surfaces info successfully at {}'.format(meshes_info_path))
        return meshes_info_path
    else:
        logger.warning('nothing to be exported, skipped')
        return None


def build_meshes_from_meshes_info(meshes_info, parent_node=None):
    """
    build meshes base on meshes info data in the scene

    Args:
        meshes_info(dict): meshes information
        parent_node(str): parent meshes to the given node, default is None
    """
    for msh, msh_info in meshes_info.iteritems():
        if not cmds.objExists(msh):
            # decompose matrix
            transform_info = apiUtils.decompose_matrix(msh_info['world_matrix'])
            # create curve
            msh, msh_shape = create_mesh(msh_info['shape']['name'], msh_info['shape']['points'],
                                         msh_info['shape']['poly_count'], msh_info['shape']['poly_connects'],
                                         msh_info['shape']['u_values'], msh_info['shape']['v_values'],
                                         uv_count=msh_info['shape']['uv_count'], uv_ids=msh_info['shape']['uv_ids'])
            # set pos
            transforms.set_pos(msh, transform_info, set_scale=True)
            # parent node
            hierarchy.parent_node(msh, parent_node)


def load_meshes_info(path, name='meshesInfo', parent_node=None):
    """
    load meshes information from given path and build the meshes in the scene
    Args:
        path(str): given meshes info file path
    Keyword Args:
        name(str): meshes info file name, default is meshesInfo
        parent_node(str): parent meshes to the given node, default is None
    """
    # get path
    meshes_info_path = os.path.join(path, name+MESH_INFO_FORMAT)
    if os.path.exists(meshes_info_path):
        msh_info = files.read_json_file(meshes_info_path)
        build_meshes_from_meshes_info(msh_info, parent_node=parent_node)
        # log info
        logger.info('build meshes base on given meshes info file: {}'.format(meshes_info_path))
    else:
        logger.warning('given path: {} does not exist, skipped'.format(meshes_info_path))


# SUB FUNCTION
def _get_MFnMesh(mesh):
    """
    get MFnMesh

    Args:
        mesh(str): mesh's shape node name

    Returns:
        MFnMesh
    """
    MDagPath = apiUtils.get_MDagPath(mesh)
    MFnMesh = OpenMaya.MFnMesh(MDagPath)
    return MFnMesh
