# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import logUtils
import attributes

# CONSTANT
logger = logUtils.logger


# FUNCTION
def parent_node(nodes, parent):
    """
    parent nodes under given parent node

    Args:
        nodes(str/list): given nodes
        parent(str): given parent node
    """

    if isinstance(nodes, basestring):
        nodes = [nodes]

    if parent and cmds.objExists(parent):
        # given parent node is available
        for n in nodes:
            p = cmds.listRelatives(n, p=True)
            if not p or p[0] != parent:
                # parent if given node has no parent or not the same has given parent
                cmds.parent(n, parent)


def parent_chain(nodes, reverse=False, parent=None):

    """
    chain parent given nodes

    Args:
        nodes(list): given nodes

    Keyword Args:
        reverse(bool): reverse parent order to parent node[1] to node[0], node[2] to node[1]...etc, default is False
        parent(str): parent chain's root to the given node, skip if None, default is None

    Returns:
        nodes(list): chain nodes, same order with the given nodes
    """

    chain_nodes = nodes[:]  # copy nodes list so the original list won't get changed

    if reverse:
        chain_nodes.reverse()

    chain_nodes.append(parent)  # add parent node to the end

    for i, n in enumerate(chain_nodes[:-1]):
        parent_node(n, chain_nodes[i+1])  # parent node to the next in the list

    nodes_return = chain_nodes[:-1]  # skip the parent node, don't need to return it

    if reverse:
        nodes_return.reverse()  # reverse back to keep the order same as nodes

    return nodes_return
