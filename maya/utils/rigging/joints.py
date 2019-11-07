# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import os
import os

# import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.files as files
import utils.common.apiUtils as apiUtils
import utils.common.transforms as transforms
import utils.common.hierarchy as hierarchy
import utils.common.logUtils as logUtils
import utils.modeling.curves as curves

# CONSTANT
logger = logUtils.logger
JOINT_INFO_FORMAT = '.jntInfo'


# FUNCTION
def create(name, **kwargs):
    """
    create single joint

    Args:
        name(str): joint's name

    Keyword Args:
        rotate_order(int): joint's rotate order, default is 0
        parent(str): parent joint
        pos(str/list): match joint's position to given node/transform value
                       str: match translate and rotate to the given node
                       [str/None, str/None]: match translate/rotate to the given node
                       [[x,y,z], [x,y,z]]: match translate/rotate to given values
        vis(bool): visibility, default is True

    Returns:
        joint(str)
    """

    # get vars
    ro = variables.kwargs('rotate_order', 0, kwargs, short_name='ro')
    parent = variables.kwargs('parent', None, kwargs, short_name='p')
    pos = variables.kwargs('pos', None, kwargs)
    vis = variables.kwargs('vis', True, kwargs, short_name='v')

    # create joint
    if cmds.objExists(name):
        logger.error('{} already exists in the scene'.format(name))
        return

    jnt = cmds.createNode('joint', name=name)
    cmds.setAttr(jnt+'.rotateOrder', ro)
    cmds.setAttr(jnt+'.visibility', vis)

    # pos
    # match pos
    if pos:
        transforms.set_pos(jnt, pos)
        cmds.makeIdentity(jnt, apply=True, t=True, r=True, s=True)  # freeze transformation

    # parent
    hierarchy.parent_node(jnt, parent)

    return jnt


def create_on_node(node, search, replace, **kwargs):
    """
    create joint base on given transform node

    Args:
        node(str): given transform node
        search(str/list): search name
        replace(str/list): replace name

    Keyword Args:
        suffix(str): add suffix description
        rotate_order(int): joint's rotate order,
                           None will copy transform's rotate order
        parent(str): parent joint
        vis(bool): joint's visibility, default is True

    Returns:
        joint(str)
    """

    # get vars
    if isinstance(search, basestring):
        search = [search]
    if isinstance(replace, basestring):
        replace = [replace]

    suffix = variables.kwargs('suffix', '', kwargs, short_name='sfx')
    ro = variables.kwargs('rotate_order', None, kwargs, short_name='ro')
    parent = variables.kwargs('parent', None, kwargs, short_name='p')
    vis = variables.kwargs('vis', True, kwargs, short_name='v')

    # get joint name
    jnt = node
    if search and replace:
        for s, r in zip(search, replace):
            jnt = jnt.replace(s, r)
    namer = naming.Namer(jnt)
    namer.description = namer.description + suffix
    jnt = namer.name

    # check node exist
    if not cmds.objExists(node):
        logger.error('{} does not exist'.format(node))
        return

    # create joint
    # get rotate order
    if ro is None:
        ro = cmds.getAttr(node+'.rotateOrder')

    # create
    jnt = create(jnt, rotate_order=ro, parent=parent, pos=node, vis=vis)

    return jnt


def create_on_pos(pos_list, **kwargs):
    """
    create joints base on given pos list
    Args:
        pos_list(list): pos can be translate/[translate, rotation]/matrix
    Keyword Args:
        joint_type(str): joint/blueprint joint
        side(str)
        description(str)
        rotate_order(int): joint's rotate order, default is 0
        hierarchy(bool): parent as chain, default is False
        parent(str): parent to the given node, default is None

    Returns:
        joints(list): list of created joints

    """
    jnt_type = variables.kwargs('joint_type', 'joint', kwargs)
    side = variables.kwargs('side', None, kwargs, short_name='s')
    des = variables.kwargs('description', None, kwargs, short_name='des')
    ro = variables.kwargs('rotate_order', 0, kwargs, short_name='ro')
    hie = variables.kwargs('hierarchy', False, kwargs)
    parent = variables.kwargs('parent', None, kwargs)

    jnt_list = []
    for i, pos in enumerate(pos_list):
        if len(pos) == 16:
            # matrix
            translate, rotate, scale = apiUtils.decompose_matrix(pos, rotate_order=ro)
        elif len(pos) == 2:
            # translate and rotate
            translate = pos[0]
            rotate = pos[1]
        else:
            translate = pos
            rotate = [0, 0, 0]
        jnt_name = naming.Namer(type=jnt_type, side=side, description=des, index=i+1).name
        jnt = create(jnt_name, rotate_order=ro, pos=[translate, rotate], parent=parent)
        jnt_list.append(jnt)

    if hie:
        jnt_list = hierarchy.parent_chain(jnt_list, reverse=True, parent=parent)
    return jnt_list


def create_on_hierarchy(nodes, search, replace, **kwargs):
    """
    create joints base on given hierarchy

    Args:
        nodes(list): given nodes
        search(str/list): search
        replace(str/list): replace

    Keyword Args:
        suffix(str): add suffix description
        rotate_order(int)[None]: joint's rotate order,
                                 None will copy transform's rotate order
        parent(str): parent joint
        vis(bool): joint's visibility, default is True
        reverse(bool): reverse parent order, default is False
                       originally is from root to end,
                       like node[0]
                            -- node[1]
                               -- node[2]
                                   .....

    Returns:
        joints(list): list of created joints
    """

    # get vars
    suffix = variables.kwargs('suffix', '', kwargs, short_name='sfx')
    ro = variables.kwargs('rotate_order', None, kwargs, short_name='ro')
    parent = variables.kwargs('parent', None, kwargs, short_name='p')
    vis = variables.kwargs('vis', True, kwargs, short_name='v')
    reverse = variables.kwargs('reverse', False, kwargs)

    # parent chain function has opposite reverse direction
    reverse = not reverse

    # create joints
    jnt_list = []

    for n in nodes:
        jnt = create_on_node(n, search, replace, suffix=suffix, rotate_order=ro, parent=parent, vis=vis)
        jnt_list.append(jnt)

    # connect
    jnt_list = hierarchy.parent_chain(jnt_list, reverse=reverse, parent=parent)

    return jnt_list


def create_joints_along_curve(curve, joints_number, **kwargs):
    """
    create joints along the given curve

    Args:
        curve(str)
        joints_number(int)
    Keyword Args:
        joint_type(str): joint/blueprint joint
        search(str/list): search
        replace(str/list): replace
        suffix(str): add suffix description
        rotate_order(int): joint's rotate order, default is 0
        aim_vector(list)
        up_vector(list)
        up_curve(str): if need nodes to aim along a specific curve
        rotation_up_vector(list): if no up curve specific, it will take this vector as reference for up direction
        uniform_type(str): length/parameter, place transforms uniformly based on distance or parameter,
                           curve's parameter can be stretched in some cases, parameter may not place nodes equally
        aim_type(str): tangent/next/None, aim type of each point, will be based on curve's tangent, or aim to the next
                       point, or keep in world orientation
        flip_check(bool): will automatically fix flipping transform if set to True
        hierarchy(bool): parent as chain, default is False
        parent(str): parent joints to the given node, default is None

    Returns:
        joints(list): list of created joints
    """
    jnt_type = variables.kwargs('joint_type', 'joint', kwargs)
    search = variables.kwargs('search', None, kwargs)
    replace = variables.kwargs('replace', None, kwargs)
    suffix = variables.kwargs('suffix', '', kwargs, short_name='sfx')
    ro = variables.kwargs('rotate_order', 0, kwargs, short_name='ro')
    aim_vector = variables.kwargs('aim_vector', [1, 0, 0], kwargs, short_name='aim')
    up_vector = variables.kwargs('up_vector', [0, 1, 0], kwargs, short_name='up')
    up_curve = variables.kwargs('up_curve', None, kwargs)
    rotation_up_vector = variables.kwargs('rotation_up_vector', [0, 1, 0], kwargs)
    uniform_type = variables.kwargs('uniform_type', 'length', kwargs)
    aim_type = variables.kwargs('aim_type', 'tangent', kwargs)
    flip_check = variables.kwargs('flip_check', True, kwargs)
    hie = variables.kwargs('hierarchy', False, kwargs)
    parent = variables.kwargs('parent', None, kwargs)

    if isinstance(search, basestring):
        search = [search]
    if isinstance(replace, basestring):
        replace = [replace]

    # get matrices
    matrix_list = curves.get_matrices_along_curve(curve, joints_number, aim_vector=aim_vector, up_vector=up_vector,
                                                  up_curve=up_curve, rotation_up_vector=rotation_up_vector,
                                                  uniform_type=uniform_type, aim_type=aim_type, flip_check=flip_check)

    namer = naming.Namer(curve)
    if search and replace:
        for s, r in zip(search, replace):
            namer.description = namer.description.replace(s, r)
    namer.description = namer.description + suffix

    # create joints
    jnt_list = create_on_pos(matrix_list, joint_type=jnt_type, side=namer.side, description=namer.description,
                             rotate_order=ro, hierarchy=hie, parent=parent)

    return jnt_list


def export_joints_info(joints, path, name='jointsInfo'):
    """
    export joints information to the given path
    joints information contain joint's name, joint's world matrix, joint's rotate order and hierarchy

    Args:
        joints(list/str): joints need to be exported
        path(str): given path
    Keyword Args:
        name(str): export joints info file name, default is jointsInfo
    Returns:
        joints_info_path(str): exported path, return None if nothing to be exported
    """
    if isinstance(joints, basestring):
        joints = [joints]

    joints_info = {}

    # get joints position info
    for jnt in joints:
        # check if jnt exist and if it is a joint
        if cmds.objExists(jnt) and cmds.objectType(jnt) == 'joint':
            # get jnt world matrix
            matrix_world = cmds.getAttr(jnt+'.worldMatrix[0]')
            # get jnt rotate order
            rotate_order = cmds.getAttr(jnt+'.rotateOrder')
            # add information to dictionary
            joints_info.update({jnt: {'world_matrix': matrix_world,
                                      'rotate_order': rotate_order}})
        else:
            logger.warning('given joint {} does not exist, skipped'.format(jnt))

    # check joints parent node
    for jnt in joints_info.keys():
        # check parent node
        parent = cmds.listRelatives(jnt, p=True)
        # check if has parent and parent in the dictionary
        if parent and parent[0] in joints_info:
            parent = parent[0]
        else:
            parent = ''
        # add parent information
        joints_info[jnt].update({'parent': parent})

    # check if has joints info
    if joints_info:
        # compose path
        joints_info_path = os.path.join(path, name+JOINT_INFO_FORMAT)
        files.write_json_file(joints_info_path, joints_info)
        logger.info('export joints info successfully at {}'.format(joints_info_path))
        return joints_info_path
    else:
        logger.warning('nothing to be exported, skipped')
        return None


def build_joints_from_joints_info(joints_info, parent_node=None):
    """
    build joints base on joints info data in the scene

    Args:
        joints_info(dict): joints information
        parent_node(str): parent root joints to the given node, default is None
    """
    # create joints
    jnts_create = []
    for jnt, jnt_info in joints_info.iteritems():
        matrix_world = jnt_info['world_matrix']
        rotate_order = jnt_info['rotate_order']
        # decompose matrix
        transform_info = apiUtils.decompose_matrix(matrix_world, rotate_order=rotate_order)

        # create jnt
        jnt = create(jnt, rotate_order=rotate_order, pos=transform_info, parent=parent_node)
        if jnt:
            # in case the joint is in the scene before creation
            jnts_create.append(jnt)

    # parent joints
    for jnt in jnts_create:
        parent = joints_info[jnt]['parent']
        hierarchy.parent_node(jnt, parent)


def load_joints_info(path, name='jointsInfo', parent_node=None):
    """
    load joints information from given path and build the joints in the scene
    Args:
        path(str): given joints info file path
    Keyword Args:
        name(str): joints info file name, default is jointsInfo
        parent_node(str): parent root joints to the given node, default is None
    """
    # get path
    joints_info_path = os.path.join(path, name+JOINT_INFO_FORMAT)
    if os.path.exists(joints_info_path):
        joints_info = files.read_json_file(joints_info_path)
        build_joints_from_joints_info(joints_info, parent_node=parent_node)
        # log info
        logger.info('build joints base on given joints info file: {}'.format(joints_info_path))
    else:
        logger.warning('given path: {} does not exist, skipped'.format(joints_info_path))
