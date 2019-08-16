# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.naming as naming
import utils.common.attributes as attributes
import utils.common.variables as variables
import utils.common.nodeUtils as nodeUtils
import utils.common.mathUtils as mathUtils
import utils.common.logUtils as logUtils

# CONSTANT
logger = logUtils.logger


# FUNCTION
def matrix_connect(input_matrix, nodes, **kwargs):
    """
    connect input matrix to given nodes

    Args:
        input_matrix(str): input matrix attribute
        nodes(str/list): given nodes

    Keyword Args:
        offset(bool): maintain offset, default is False
        skip(list): skip channels
        force(bool): force connection, default is True
    """

    offset = variables.kwargs('offset', '', kwargs)
    skip = variables.kwargs('skip', None, kwargs)
    force = variables.kwargs('force', True, kwargs, short_name='f')

    driver = input_matrix.split('.')[0]
    attr_name = cmds.ls(input_matrix)[0].split('.')[-1]  # use to compose name

    namer_driver = naming.Namer(driver)
    namer_driver.type = naming.Type.decomposeMatrix
    namer_driver.description = namer_driver.description + attr_name[0].upper() + attr_name[1:]

    des_offset = namer_driver.description + 'Offset'

    if isinstance(nodes, basestring):
        nodes = [nodes]

    if skip is None:
        skip = []

    driver_attrs = []
    driven_attrs = []
    for attr in attributes.Attr.transform:
        attr_short = attr[0] + attr[-1].lower()  # get attribute short name
        if attr not in skip and attr_short not in skip:
            # if attribute long and short name are all not in skip
            driver_attrs.append('output{}{}'.format(attr[0].upper(), attr[1:]))
            driven_attrs.append(attr)

    if not offset:
        decompose_matrix = nodeUtils.node(name=namer_driver.name, use_exist=True)
        cmds.connectAttr(input_matrix, decompose_matrix+'.inputMatrix')
        for n in nodes:
            attributes.connect_attrs(driver_attrs, driven_attrs,
                                     driver=decompose_matrix, driven=n, force=force)
    else:
        # get latest suffix
        suffix = 0
        mult_matrix_offset = naming.Namer(type=naming.Type.multMatrix,
                                          side=namer_driver.side,
                                          description=des_offset,
                                          index=namer_driver.index).name
        mult_matrix_offset = cmds.ls(mult_matrix_offset+'_???')  # list all multMatrix nodes with this name

        if mult_matrix_offset:
            mult_matrix_offset.sort()
            namer_offset = naming.Namer(mult_matrix_offset[-1])  # get name wrapper to get suffix
            if namer_offset.suffix:
                suffix = namer_offset.suffix
            elif namer_offset.index:
                suffix = namer_offset.index

        for i, n in enumerate(nodes):
            offset_matrix = cmds.getAttr(n+'.worldMatrix[0]')
            offset_inverse_matrix = mathUtils.inverse_matrix(offset_matrix)

            mult_matrix = nodeUtils.mult_matrix([input_matrix, offset_inverse_matrix],
                                                side=namer_driver.side,
                                                description=des_offset,
                                                index=namer_driver.index,
                                                suffix=suffix+i+1)

            decompose_matrix = nodeUtils.node(type=naming.Type.decomposeMatrix,
                                              side=namer_driver.side,
                                              description=des_offset,
                                              index=namer_driver.index,
                                              suffix=suffix+i+1)

            cmds.connectAttr(mult_matrix+'.matrixSum', decompose_matrix+'.inputMatrix')
            attributes.connect_attrs(driver_attrs, driven_attrs,
                                     driver=decompose_matrix, driven=n, force=force)


def matrix_aim_constraint(input_matrix, driven_nodes, **kwargs):
    """
    aim constraint using matrix connection

    Args:
        input_matrix(str): input matrix attribute
        driven_nodes(str/list): driven nodes

    Keyword Args:
        parent(str): parent constraint node to, None will parent under driven node
        world_up_type(str): aim constraint world up type,
                            'object',
                            'objectrotation'
                            default is 'objectrotation'
        world_up_matrix(str): aim constraint world up matrix
        aim_vector(list): aim constraint's aim vector, default is [1,0,0]
        up_vector(list): aim constraint's up vector, default is [0,1,0]
        local(bool): local will skip parent inverse matrix connection, default is False
        force(bool): force connection, default is True
    """

    # get vars
    parent = variables.kwargs('parent', None, kwargs, short_name='p')
    world_up_type = variables.kwargs('world_up_type', 'objectrotation', kwargs)
    world_up_matrix = variables.kwargs('world_up_matrix', None, kwargs)
    aim_vector = variables.kwargs('aimVector', [1, 0, 0], kwargs, short_name='aim')
    up_vector = variables.kwargs('upVector', [0, 1, 0], kwargs, short_name='up')
    local = variables.kwargs('local', False, kwargs)
    force = variables.kwargs('force', True, kwargs, short_name='f')

    # world up type
    if world_up_type == 'objectrotation':
        world_up_type = 2
    else:
        world_up_type = 1

    if isinstance(driven_nodes, basestring):
        driven_nodes = [driven_nodes]

    # get name
    driver_node = input_matrix.split('.')[0]
    namer_aim = naming.Namer(driver_node)
    namer_aim.type = naming.Type.decomposeMatrix
    namer_aim.description = namer_aim.description+'Aim'

    for d in driven_nodes:
        if cmds.objExists(d):
            namer_driven = naming.Namer(d)
            namer_driven.type = naming.Type.aimConstraint
            aim_constraint = nodeUtils.node(name=namer_driven.name)  # create empty aim constraint

            if not parent or not cmds.objExists(parent):
                parent = d
            cmds.parent(aim_constraint, parent)  # parent aim constraint under parent node

            decompose_matrix = nodeUtils.node(name=namer_aim.name, use_exist=True)
            cmds.connectAttr(input_matrix, decompose_matrix+'.inputMatrix', f=True)

            for i, axis in enumerate('XYZ'):
                # connect aim constraint attributes
                cmds.setAttr('{}.aimVector{}'.format(aim_constraint, axis), aim_vector[i])
                cmds.setAttr('{}.upVector{}'.format(aim_constraint, axis), up_vector[i])
                cmds.connectAttr('{}.translate{}'.format(d, axis),
                                 '{}.constraintTranslate{}'.format(aim_constraint, axis))
                cmds.connectAttr('{}.outputTranslate{}'.format(decompose_matrix, axis),
                                 '{}.target[0].targetTranslate{}'.format(aim_constraint, axis))

            if cmds.objectType(d) == 'joint':
                # connect joint orient if it is joint
                for axis in 'XYZ':
                    cmds.connectAttr('{}.jointOrient{}'.format(d, axis),
                                     '{}.constraintJointOrient{}'.format(aim_constraint, axis))

            if not local:
                # connect parent inverse matrix if not local
                cmds.connectAttr(d+'.parentInverseMatrix[0]',
                                 aim_constraint+'.constraintParentInverseMatrix')

            # aim constraint aim properties
            cmds.connectAttr(world_up_matrix, aim_constraint+'.worldUpMatrix')
            cmds.setAttr(aim_constraint+'.worldUpType', world_up_type)
            cmds.setAttr(aim_constraint+'.target[0].targetParentMatrix',
                         mathUtils.MATRIX_DEFAULT, type='matrix')

            for axis in 'XYZ':
                # connect with driven node
                attributes.connect_attrs('{}.constraintRotate{}'.format(aim_constraint, axis),
                                         '{}.rotate{}'.format(d, axis), force=force)


def matrix_pole_vector_constraint(input_matrix, ik_handle, joint, **kwargs):
    """
    pole vector constraint using matrix connection

    Args:
        input_matrix(str): input matrix attribute
        ik_handle(str): driven ik handle
        joint(str): driven ik chain's root joint

    Keyword Args:
        parent(str): parent constraint node to the given node, None will parent under driven node
        parent_inverse_matrix(str): ikHandle's parent inverse matrix,
                                    None will use ikHandle's parentInverseMatrix attr
        force(bool): force connection, default is True
    """

    # get vars
    parent = variables.kwargs('parent', None, kwargs, short_name='p')
    parent_inverse_matrix = variables.kwargs('parent_inverse_matrix', None, kwargs)
    force = variables.kwargs('force', True, kwargs, short_name='f')

    # get name from ik handle
    namer = naming.Namer(ik_handle)

    decompose_matrix = nodeUtils.node(type=naming.Type.decomposeMatrix,
                                      side=namer.side,
                                      description=namer.description+'Pv',
                                      index=namer.index)

    cmds.connectAttr(input_matrix, decompose_matrix+'.inputMatrix')

    # constraint
    pv_constraint = nodeUtils.node(type=naming.Type.poleVectorConstraint,
                                   side=namer.side,
                                   description=namer.description+'Pv',
                                   index=namer.index)

    if not parent or not cmds.objExists(parent):
        parent = ik_handle
    cmds.parent(pv_constraint, parent)

    # connect constraint attributes
    for output_attr, input_attr in zip([decompose_matrix+'.outputTranslate',
                                        joint+'.translate'],
                                       ['target[0].targetTranslate',
                                        'constraintRotatePivot']):
        for axis in 'XYZ':
            cmds.connectAttr(output_attr + axis, '{}.{}{}'.format(pv_constraint, input_attr, axis))

    # connect parent inverse matrix
    if not parent_inverse_matrix:
        parent_inverse_matrix = ik_handle+'.parentInverseMatrix[0]'
    cmds.connectAttr(parent_inverse_matrix, pv_constraint+'.constraintParentInverseMatrix')

    # output
    for axis in 'XYZ':
        attributes.connect_attrs('{}.constraintTranslate{}'.format(pv_constraint, axis),
                                 '{}.poleVector{}'.format(ik_handle, axis), force=force)


def matrix_blend_constraint(input_matrices, driven, **kwargs):
    """
    blend constraint using matrix connection

    Args:
        input_matrices(list): input matrices attribute, should given at least two matrices
        driven(str): driven node

    Keyword Args:
        parent(str): parent constraint node to the given node, None will parent under driven node
        weights(float/list): weight value for each target
                             can be a list of attribute to connect
        translate(bool): constraint translate, default is True
        rotate(bool): constraint rotate, default is True
        scale(bool): constraint scale, default is True
        force(bool): force connection, default is True
    """

    parent = variables.kwargs('parent', None, kwargs, short_name='p')
    weights = variables.kwargs('weights', 1, kwargs, short_name='w')
    translate = variables.kwargs('translate', True, kwargs, short_name='t')
    rotate = variables.kwargs('rotate', True, kwargs, short_name='r')
    scale = variables.kwargs('scale', True, kwargs, short_name='s')
    force = variables.kwargs('force', True, kwargs, short_name='f')

    namer = naming.Namer(driven)  # get name

    if not parent or not cmds.objExists(parent):
        parent = driven

    if not weights:
        weights = 1
    if not isinstance(weights, list):
        weights = [weights] * len(input_matrices)

    point_constraint = None
    orient_constraint = None
    scale_constraint = None

    if translate:
        # create point constraint
        point_constraint = nodeUtils.node(type=naming.Type.pointConstraint,
                                          side=namer.side,
                                          description=namer.description+'BlendConstraint',
                                          index=namer.index)
        cmds.parent(point_constraint, parent)

    if rotate:
        # create orient constraint
        orient_constraint = nodeUtils.node(type=naming.Type.orientConstraint,
                                           side=namer.side,
                                           description=namer.description+'BlendConstraint',
                                           index=namer.index)
        cmds.setAttr(orient_constraint+'.interpType', 2)
        cmds.parent(orient_constraint, parent)

    if scale:
        # create scale constraint
        scale_constraint = nodeUtils.node(type=naming.Type.scaleConstraint,
                                          side=namer.side,
                                          description=namer.description+'BlendConstraint',
                                          index=namer.index)
        cmds.parent(scale_constraint, parent)

    for i, matrix in enumerate(input_matrices):
        driver = matrix.split('.')[0]
        namer_driver = naming.Namer(driver)  # get driver name

        # create decompose matrix node to drive constraints
        decompose = nodeUtils.node(type=naming.Type.decomposeMatrix,
                                   side=namer_driver.side,
                                   description=namer_driver.description+'BlendConstraint',
                                   index=namer_driver.index)
        cmds.connectAttr(matrix, decompose+'.inputMatrix')

        for attr, con in zip(['translate', 'rotate', 'scale'],
                             [point_constraint, orient_constraint, scale_constraint]):
            if con:
                # connect driver's matrix to constraint node
                for axis in 'XYZ':
                    cmds.connectAttr('{}.output{}{}'.format(decompose, attr.title(), axis),
                                     '{}.target[{}].target{}{}'.format(con, i, attr.title(), axis))

                # connect/set weight value
                if isinstance(weights[i], basestring):
                    cmds.connectAttr(weights[i], '{}.target[{}].targetWeight'.format(con, i))
                else:
                    cmds.setAttr('{}.target[{}].targetWeight'.format(con, i), weights[i])

                # set parent matrix to zero, otherwise the result won't be correct
                cmds.setAttr('{}.target[{}].targetParentMatrix'.format(con, i),
                             mathUtils.MATRIX_DEFAULT, type='matrix')

    for attr, con in zip(['translate', 'rotate', 'scale'],
                         [point_constraint, orient_constraint, scale_constraint]):
        if con:
            # connect constraint node to driven node
            for axis in 'XYZ':
                attributes.connect_attrs('{}.constraint{}{}'.format(con, attr.title(), axis),
                                         '{}.{}{}'.format(driven, attr, axis), force=force)

                # joint orient
                if attr == 'rotate' and cmds.attributeQuery('jointOrient'+axis, n=driven, ex=True):
                    # if driven node has attr 'jointOrient', which means the driven node is a joint
                    # connect joint orient to constraint node
                    cmds.connectAttr('{}.jointOrient{}'.format(driven, axis),
                                     '{}.constraintJointOrient{}'.format(con, axis))
