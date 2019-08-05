# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import attributes
import variables
import logUtils

# CONSTANT
logger = logUtils.get_logger(name='transforms', level='info')


# FUNCTION
def create(name, **kwargs):
    """
    create transform node

    Args:
        name(str): transform node's name

    Keyword Args:
        lockHide(list): lock and hide transform attrs
        parent(str): where to parent the transform node
        rotate_order(int): transform node's rotate order, default is 0
        vis(bool): transform node's visibility, default is True
        pos(str/list): match transform's position to given node/transform value
                       str: match translate and rotate to the given node
                       [str/None, str/None]: match translate/rotate to the given node
                       [[x,y,z], [x,y,z]]: match translate/rotate to given values
        inheritsTransform(bool): set transform node's inheritance attr, default is True
    """
    # get vars
    lock_hide = variables.kwargs('lockHide', [], kwargs, short_name='lh')
    parent = variables.kwargs('parent', None, kwargs, short_name='p')
    rotate_order = variables.kwargs('rotate_order', 0, kwargs, short_name='ro')
    vis = variables.kwargs('vis', True, kwargs, short_name='v')
    pos = variables.kwargs('pos', None, kwargs)
    inherits = variables.kwargs('inheritsTransform', True, kwargs)

    # create transform
    transform = cmds.createNode('transform', name=name)

    # ro
    cmds.setAttr(transform+'.ro', rotate_order)

    # vis
    cmds.setAttr(transform+'.v', vis)

    # inheritance
    cmds.setAttr(transform+'.inheritsTransform', inherits)

    # match pos
    if pos:
        set_pos(transform, pos)

    # parent
    if parent:
        parent_node(transform, parent)

    # lock hide
    attributes.lock_hide_attrs(transform, lock_hide)

    return transform


def parent_node(node, parent):
    """
    parent node

    Args:
        node(str/list): node
        parent(str): parent node
    """

    if isinstance(node, basestring):
        node = [node]

    if not cmds.objExists(parent):
        logger.warning('{} does not exist'.format(parent))
        return

    for n in node:
        if not cmds.objExists(n):
            logger.warning('{} does not exist'.format(n))
        else:
            # check parent
            p = cmds.listRelatives(n, p=True)
            if p and p[0] == parent:
                logger.warning('{} is parented to {} already'.format(n, parent))
            else:
                cmds.parent(n, parent)


def bounding_box_info(nodes):
    """
    get given nodes/pos bounding box info

    Args:
        nodes(list)

    Returns:
        max(list): max X/Y/Z
        min(list): min X/Y/Z
        center(list): pos X/Y/Z
    """
    pos_x = []
    pos_y = []
    pos_z = []

    for n in nodes:
        if isinstance(n, basestring) and cmds.objExists(n):
            pos = cmds.xform(n, q=True, t=True, ws=True)
            pos_x.append(pos[0])
            pos_y.append(pos[1])
            pos_z.append(pos[2])

        elif isinstance(n, list):
            pos_x.append(n[0])
            pos_y.append(n[1])
            pos_z.append(n[2])

    max_pos = [max(pos_x), max(pos_y), max(pos_z)]
    min_pos = [min(pos_x), min(pos_y), min(pos_z)]
    center_pos = [(max_pos[0] + min_pos[0]) * 0.5,
                  (max_pos[1] + min_pos[1]) * 0.5,
                  (max_pos[2] + min_pos[2]) * 0.5]

    return max_pos, min_pos, center_pos


def set_pos(nodes, pos, rotate_order=0):
    """
    set pos for the given transform nodes

    Args:
        nodes(str/list): given transform nodes
        pos(str/list): match transform's position to given node/transform value
                       str: match translate and rotate to the given node
                       [str/None, str/None]: match translate/rotate to the given node
                       [[x,y,z], [x,y,z]]: match translate/rotate to given values

    Keyword Args:
        rotate_order(int): rotate order for the input pos
    """

    ro = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']  # xform rotate order only accept string

    if isinstance(nodes, basestring):
        nodes = [nodes]

    for n in nodes:
        if pos:
            if isinstance(pos, basestring):
                cmds.matchTransform(n, pos, pos=True, rot=True)
            else:
                if isinstance(pos[0], basestring):
                    cmds.matchTransform(n, pos[0], pos=True, rot=False)
                else:
                    cmds.xform(n, t=pos[0], ws=True)
                if isinstance(pos[1], basestring):
                    cmds.matchTransform(n, pos[1], pos=False, rot=True)
                else:
                    # get node's rotate order first
                    ro_node = cmds.getAttr(n+'.rotateOrder')
                    # set rotation with given rotate order
                    cmds.xform(n, rot=pos[1], ws=True, rotateOrder=ro[rotate_order])
                    # set back node's rotate order, and preserve overall rotation
                    cmds.xform(n, rotateOrder=ro[ro_node])
