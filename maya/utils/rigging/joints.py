# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.transforms as transforms
import utils.common.hierarchy as hierarchy
import utils.common.logUtils as logUtils

# CONSTANT
logger = logUtils.logger


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
        jnt = create_on_node(n, search, replace, suffix=suffix,
                             rotate_order=ro, parent=parent, vis=vis)
        jnt_list.append(jnt)

    # connect
    jnt_list = hierarchy.parent_chain(jnt_list, reverse=reverse, parent=parent)

    return jnt_list
