# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import ast
import ast

# import utils
import naming
import attributes
import variables
import logUtils

# CONSTANT
logger = logUtils.logger


# FUNCTION
def node(**kwargs):
    """
    Create maya node

    Keyword Args:
        name(str): node's name, will create node base on type
        type(str): node's type (if name given, will follow name)
        side(str): node's side (if name given, will follow name)
        description(str): node's description (if name given, will follow name)
        index(int): node's index (if name given, will follow name)
        suffix(int): node's suffix (if name given, will follow name)

        use_exist(bool): if node already exists, using exist node
                        will Error out if node exists and set this to False
                        default is False
        auto_suffix(bool): automatically suffix node from 1, default is False

        set_attrs(dict): set attrs when creating the node

    Returns:
        name(str): node's name
    """

    # get vars
    _name = variables.kwargs('name', None, kwargs, short_name='n')
    _type = variables.kwargs('type', None, kwargs, short_name='t')
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')

    _use_exist = variables.kwargs('use_exist', False, kwargs)
    _auto_suffix = variables.kwargs('auto_suffix', False, kwargs)

    _set_attrs = variables.kwargs('set_attrs', {}, kwargs)

    node_name = None

    if _name:
        namer = naming.Namer(_name)
    else:
        if not _des or not _side:
            raise ValueError('name must contain side and description')

        namer = naming.Namer(type=_type, side=_side,
                             description=_des, index=_index,
                             suffix=_suffix)

    # check if node exist
    if cmds.objExists(namer.name):
        if not _use_exist:
            logger.error('{} node: {} already exists in the scene'.format(namer.type, namer.name))
            raise ValueError('{} node: {} already exists in the scene'.format(namer.type, namer.name))
        else:
            node_name = namer.name
    else:
        # check if auto suffix
        if _auto_suffix:
            node_exists = cmds.ls(namer.name+'_???')
            namer.suffix = len(node_exists) + 1

        node_name = cmds.createNode(namer.type, name=namer.name)

    for attr, val in _set_attrs.iteritems():
        cmds.setAttr('{}.{}'.format(node_name, attr), val)

    return node_name


def equation(expression, **kwargs):
    """
    Create node connection network base on the expression, only works for 1D input

    Symbols:
        +:  add
        -:  sub
        *:  multiply
        /:  divide
       **:  power
        ~:  reverse

    Example:
        equation('(pCube1.tx + pCube2.tx)/2')

    Args:
        expression(str): given equation to make the connection

    Keyword Args:
        side(str): nodes' side
        description(str): nodes' description
        index(int): nodes' index
        attrs(str/list): connect the equation to given attrs
        force(bool): force the connection, default is True

    Return:
        output_attr(str): output attribute from the equation node network
    """

    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')

    # node equation
    output_attr = NodeEquation.equation(expression, side=_side,
                                        description=_des, index=_index)

    # connect attrs
    if _attrs:
        attributes.connect_attrs(output_attr, _attrs, force=_force)

    return output_attr


def plus_minus_average(input_attrs, **kwargs):
    """
    connect attrs with plusMinusAverage node

    Args:
        input_attrs(list): given attrs, will connect in order
                           can be 1D/2D/3D inputs
                           2D/3D attrs must be in list
                          ('node.t' will not work,
                            have to be ['node.tx', 'node.ty', 'node.tz'])
    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        operation(int): plusMinusAverage node's operation
                        1. add
                        2. sub
                        3. average
                        default is 1
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False

    Returns:
        output_attr(list): output attribute from the node
            or
        node(str): node name
    """

    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _op = variables.kwargs('operation', 1, kwargs, short_name='op')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    # create node
    pmav = node(type=naming.Type.plusMinusAvarge, side=_side,
                description=_des, index=_index, suffix=_suffix,
                set_attrs={'operation': _op})

    # check input attr type(1D/2D/3D)
    if not isinstance(input_attrs[0], list) and not isinstance(input_attrs[0], tuple):
        # 1D
        for i, input_attr in enumerate(input_attrs):
            if isinstance(input_attr, basestring):
                cmds.connectAttr(input_attr, '{}.input1D[{}]'.format(pmav, i))
            else:
                cmds.setAttr('{}.input1D[{}]'.format(pmav, i), input_attr)

        output_attr = [pmav+'.output1D']

    else:
        # 2D/3D
        num = len(input_attrs[0])

        for i, input_attr in enumerate(input_attrs):
            for input_attr_info in zip(input_attr, ['x', 'y', 'z']):
                if isinstance(input_attr_info[0], basestring):
                    cmds.connectAttr(input_attr_info[0],
                                     '{}.input{}D[{}].input{}D{}'.format(pmav, num, i,
                                                                         num, input_attr_info[1]))
                else:
                    cmds.setAttr('{}.input{}D[{}].input{}D{}'.format(pmav, num, i,
                                                                     num, input_attr_info[1]), input_attr_info[0])
        if num == 2:
            output_attr = [pmav+'.output2Dx', pmav+'.output2Dy']
        else:
            output_attr = [pmav+'.output3Dx', pmav+'.output3Dy', pmav+'.output3Dz']

    # connect attr
    if _attrs:
        if isinstance(_attrs, basestring):
            _attrs = [_attrs]
        elif isinstance(_attrs[0], basestring):
            _attrs = [_attrs]
        for attr in _attrs:
            for attrInfo in zip(output_attr, attr):
                attributes.connect_attrs(attrInfo[0], attrInfo[1], force=_force)

    # return output attr/node name
    if not _node_only:
        return output_attr
    else:
        return pmav


def multiply_divide(input_attr1, input_attr2, **kwargs):
    """
    connect attrs with multiplyDivide node

    Args:
        input_attr1(str/list): input attr 1
                               maximum 3 attrs (['tx', 'ty', 'tz'])
        input_attr2(str/list): input attr 2
                               maximum 3 attrs (['tx', 'ty', 'tz'])
    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        operation(int): multiplyDivide node's operation
                        1. multiply
                        2. divide
                        3. power
                        default is 1
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False

    Returns:
        output_attr(str/list): output attribute from the node
            or
        node(str): node name
    """
    # get vars

    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _op = variables.kwargs('operation', 1, kwargs, short_name='op')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    output_attr, _node = _create_node_multi_attrs([], [input_attr1, input_attr2],
                                                  [], ['input1', 'input2'],
                                                  ['X', 'Y', 'Z'], 'output',
                                                  type=naming.Type.multiplyDivide,
                                                  side=_side, description=_des,
                                                  set_attrs={'operation': _op},
                                                  attrs=_attrs, force=_force)
    # return output attr/node name
    if not _node_only:
        return output_attr
    else:
        return _node


def condition(first_term, second_term, if_true, if_false, **kwargs):
    """
    connect attrs with condition node

    Args:
        first_term(str/float): first term
        second_term(str/float): secondTerm
        if_true(str/float/list): color if True
        if_false(str/float/list): color if False

    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        operation(int/str): condition node's operation
                            0['=='] equal
                            1['!='] not equal
                            2['>']  greater than
                            3['>='] greater or equal
                            4['<']  less than
                            5['<='] less or equal
                            default is 0
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False

    Returns:
        output_attr(str/list): output attribute from the node
            or
        node(str): node name
    """

    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _op = variables.kwargs('operation', 0, kwargs, short_name='op')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    # get operation
    if isinstance(_op, basestring):
        _op_list = ['==', '!=', '>', '>=', '<', '<=']
        _op = _op_list.index(_op)

    output_attr, _node = _create_node_multi_attrs([first_term, second_term],
                                                  [if_true, if_false],
                                                  ['firstTerm', 'secondTerm'],
                                                  ['colorIfTrue', 'colorIfFalse'],
                                                  ['R', 'G', 'B'], 'outColor',
                                                  type=naming.Type.condition,
                                                  side=_side, description=_des,
                                                  set_attrs={'operation': _op},
                                                  attrs=_attrs, force=_force)

    # return output attr/node name
    if not _node_only:
        return output_attr
    else:
        return _node


def clamp(input_attr, max_attr, min_attr, **kwargs):
    """
    connect attrs with clamp node

    Args:
        input_attr(str/float/list): clamp's input
        max_attr(str/float/list): clamp's max
        min_attr(str/float/list): clamp's min

    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False
    Returns:
        outputAttr(list): output attribute from the node
            or
        node(str): node name
    """

    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    output_attr, _node = _create_node_multi_attrs([], [input_attr, max_attr, min_attr],
                                                  [], ['input', 'max', 'min'],
                                                  ['R', 'G', 'B'], 'output',
                                                  type=naming.Type.clamp,
                                                  side=_side, description=_des,
                                                  attrs=_attrs, force=_force)

    # return output attr/node name
    if not _node_only:
        return output_attr
    else:
        return _node


def blend(blender, input_attr1, input_attr2, **kwargs):
    """
    connect attrs with blendColor node

    Args:
        blender(str/float): blendColor's blender
        input_attr1(str/float/list): blendColor's color1
        input_attr2(str/float/list): blendColor's color2

    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False

    Returns:
        output_attr(list): output attribute from the node
            or
        node(str): node name
    """

    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    output_attr, _node = _create_node_multi_attrs([blender], [input_attr1, input_attr2],
                                                  ['blender'], ['color1', 'color2'],
                                                  ['R', 'G', 'B'], 'output',
                                                  type=naming.Type.blendColor,
                                                  side=_side, description=_des,
                                                  attrs=_attrs, force=_force)

    # return output attr/node name
    if not _node_only:
        return output_attr
    else:
        return _node


def remap(input_value, input_range, output_range, **kwargs):
    """
    connect attrs with remapValue node

    Args:
        input_value(str/float): remapValue's input
        input_range(list): remapValue's input min/max
        output_range(list): remapValue's output min/max

    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        set_attrs(dict): set node's attrs
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False

    Returns:
        output_attr(str): output attribute from the node
            or
        node(str): node name
    """

    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _set_attrs = variables.kwargs('set_attrs', {}, kwargs)
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    # create node
    remap_node = node(type=naming.Type.remapValue, side=_side, description=_des,
                      index=_index, suffix=_suffix, set_attrs=_set_attrs)

    # input connection
    if isinstance(input_value, basestring):
        cmds.connectAttr(input_value, remap_node+'.inputValue')

    for range_value in zip([input_range, output_range], ['input', 'output']):
        for val in zip(range_value[0], ['Min', 'Max']):
            if isinstance(val[0], basestring):
                cmds.connectAttr(val[0], '{}.{}{}'.format(remap_node, range_value[1], val[1]))
            else:
                cmds.setAttr('{}.{}{}'.format(remap_node, range_value[1], val[1]), val[0])

    output_attr = remap_node+'.outValue'

    if _attrs:
        attributes.connect_attrs(output_attr, _attrs, force=_force)

    if not _node_only:
        return output_attr
    else:
        return  remap_node


def add_matrix(input_matrix, **kwargs):
    """
    connect attrs with add matrix node

    Args:
        input_matrix(list): list of input matrix
                            each can be attribute/list

    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False
    Returns:
        outputAttr(str): output attribute from the node
            or
        node(str): node name
    """

    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    # create node
    add_matrix_node = node(type=naming.Type.addMatrix, side=_side,
                           description=_des, index=_index, suffix=_suffix)

    # input attrs
    for i, matrix in enumerate(input_matrix):
        if isinstance(matrix, basestring):
            cmds.connectAttr(matrix, '{}.matrixIn[{}]'.format(add_matrix, i))
        else:
            cmds.setAttr('{}.matrixIn[{}]'.format(add_matrix, i), matrix, type='matrix')

    output_attr = add_matrix_node+'.matrixSum'

    if _attrs:
        attributes.connect_attrs(output_attr, _attrs, force=_force)

    # return output attr/node name
    if not _node_only:
        return output_attr
    else:
        return add_matrix_node


def mult_matrix(input_matrix, **kwargs):
    """
    connect attrs with mult matrix node

    Args:
        input_matrix(list): list of input matrix
                           each can be attribute/list

    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False

    Returns:
        outputAttr(str): output attribute from the node
            or
        node(str): node name
    """

    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    # create node
    mult_matrix_node = node(type=naming.Type.multMatrix, side=_side,
                            description=_des, index=_index, suffix=_suffix)

    # input attrs
    for i, matrix in enumerate(input_matrix):
        if isinstance(matrix, basestring):
            cmds.connectAttr(matrix, '{}.matrixIn[{}]'.format(mult_matrix_node, i))
        else:
            cmds.setAttr('{}.matrixIn[{}]'.format(mult_matrix_node, i), matrix, type='matrix')

    output_attr = mult_matrix_node+'.matrixSum'

    if _attrs:
        attributes.connect_attrs(output_attr, _attrs, force=_force)

    # return output attr/node name
    if not _node_only:
        return output_attr
    else:
        return mult_matrix_node


def inverse_matrix(input_matrix, **kwargs):
    """
    connect attrs with inverse matrix node

    Args:
        input_matrix(str): input matrix attr

    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False

    Returns:
        output_attr(str): output attribute from the node
            or
        node(str): node name
    """

    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    # create node
    inverse_matrix_node = node(type=naming.Type.inverseMatrix, side=_side,
                               description=_des, index=_index, suffix=_suffix)

    # input attrs
    cmds.connectAttr(input_matrix, inverse_matrix_node+'.inputMatrix')

    output_attr = inverse_matrix_node+'.outputMatrix'

    if _attrs:
        attributes.connect_attrs(output_attr, _attrs, force=_force)

    # return output attr/node name
    if not _node_only:
        return output_attr
    else:
        return inverse_matrix_node


def compose_matrix(translate, rotate, scale=None, **kwargs):
    """
    connect attrs with compose matrix node

    Args:
        translate(list): input translate
                         each can be attribute/float
        rotate(list): input rotate
                      each can be attribute/float

    Keyword Args:
        scale(list): input scale
                     each can be attribute/float
                     default is [1,1,1]
        rotateOrder(int): input rotate order, default is 0
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        attrs(str/list): connect the node to given attrs
        force(bool): force the connection, default is True
        node_only(bool): return node name instead of output attributes if True, default is False

    Returns:
        output_attr(str): output attribute from the node
        node(str): node name
    """
    # get vars
    rotate_order = variables.kwargs('rotateOrder', 0, kwargs, short_name='ro')
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _attrs = variables.kwargs('attrs', [], kwargs)
    _force = variables.kwargs('force', True, kwargs, short_name='f')
    _node_only = variables.kwargs('node_only', False, kwargs)

    if scale is None:
        scale = [1, 1, 1]

    # node
    compose = node(type=naming.Type.composeMatrix, side=_side,
                   description=_des, index=_index, suffix=_suffix)
    for input_attr_info in zip([translate, rotate, scale], ['translate', 'rotate', 'scale']):
        for input_val in zip(input_attr_info[0], ['X', 'Y', 'Z']):
            if isinstance(input_val[0], basestring):
                cmds.connectAttr(input_val[0],
                                 '{}.input{}{}'.format(compose, input_attr_info[1].title(), input_val[1]))
            else:
                cmds.setAttr('{}.input{}{}'.format(compose, input_attr_info[1].title(), input_val[1]),
                             input_val[0])

    if isinstance(rotate_order, basestring):
        cmds.connectAttr(rotate_order, compose+'.inputRotateOrder')
    else:
        cmds.setAttr(compose+'.inputRotateOrder', rotate_order)

    output_attr = compose+'.outputMatrix'

    if _attrs:
        attributes.connect_attrs(output_attr, _attrs, force=_force)

    # return output_attr/node name
    if not _node_only:
        return output_attr
    else:
        return compose


def twist_extraction(input_matrix, **kwargs):
    """
    extract twist value from input matrix

    Args:
        input_matrix(str)

    Keyword Args:
        attrs(str/list): connect twist value to attrs
        force(bool): force the connection, default is True

    Returns:
        output_attr(str): output attr
    """
    attrs = variables.kwargs('attrs', [], kwargs)
    force = variables.kwargs('force', True, kwargs, short_name='f')

    driver = input_matrix.split('.')[0]

    namer = naming.Namer(driver)

    namer.type = naming.Type.decomposeMatrix
    namer.description = namer.description+'TwistExtract'

    decompose_matrix = node(name=namer.name)
    cmds.connectAttr(input_matrix, decompose_matrix+'.inputMatrix')

    namer.type = naming.Type.quatToEuler
    quat_to_euler = node(name=namer.name)

    cmds.connectAttr(decompose_matrix+'.outputQuatX',
                     quat_to_euler+'.inputQuatX')
    cmds.connectAttr(decompose_matrix+'.outputQuatW',
                     quat_to_euler+'.inputQuatW')

    if attrs:
        attributes.connect_attrs(quat_to_euler+'.outputRotateX',
                                 attrs, force=force)

    return quat_to_euler+'.outputRotateX'


def mash_distribute(input_attr, nodes_number, affect_attr, **kwargs):
    """
    create mash distribute node and mash breakout node to achieve remap array
    Args:
        input_attr(str): input drive attribute
        nodes_number(int): output nodes number
        affect_attr(str): which attribute input_attr should connect to,
                                ['distanceX', 'distanceY', 'distanceZ',
                                 'rotateX', 'rotateY', 'rotateZ',
                                 'scaleX', 'scaleY', 'scaleZ']
    Keyword Args:
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        ramp_position(list): ramp points positions
        ramp_values(list): ramp_points values
        ramp_interpolation(int/str): ramp interpolation

    Returns:
        mash_distribute(str): mash distribute node
        mash_breakout(str): mash breakout node
    """
    # get vars
    _side = variables.kwargs('side', None, kwargs, short_name='s')
    _des = variables.kwargs('description', None, kwargs, short_name='des')
    _index = variables.kwargs('index', None, kwargs, short_name='i')
    _suffix = variables.kwargs('suffix', None, kwargs, short_name='sfx')
    _ramp_pos = variables.kwargs('ramp_position', None, kwargs)
    _ramp_val = variables.kwargs('ramp_values', None, kwargs)
    _ramp_interp = variables.kwargs('ramp_interpolation', 1, kwargs)

    # create mash_distribute node
    mash_distribute_node = node(type=naming.Type.MASH_Distribute, side=_side, description=_des, index=_index,
                                suffix=_suffix, set_attrs={'pointCount': nodes_number})
    cmds.connectAttr(input_attr, '{}.{}'.format(mash_distribute_node, affect_attr))

    # get ramp
    if affect_attr.startswith('t'):
        ramp_attr = 'biasRamp'
    elif affect_attr.startswith('r'):
        ramp_attr = 'rotationRamp'
    else:
        ramp_attr = 'scaleRamp'

    # remove extra ramp point
    cmds.removeMultiInstance('{}.{}[2]'.format(mash_distribute_node, ramp_attr), b=True)

    # set ramp value
    # interpolation
    if isinstance(_ramp_interp, basestring):
        if _ramp_interp.lower() in ['linear', 'smooth', 'spline']:
            _ramp_interp = ['linear', 'smooth', 'spline'].index(_ramp_interp.lower())
        else:
            _ramp_interp = 1
    i = 0
    for pos, val in zip(_ramp_pos, _ramp_val):
        cmds.setAttr('{}.rotationRamp[{}].rotationRamp_Position'.format(mash_distribute_node, i), pos)
        cmds.setAttr('{}.rotationRamp[{}].rotationRamp_FloatValue'.format(mash_distribute_node, i), val)
        cmds.setAttr('{}.rotationRamp[{}].rotationRamp_Interp'.format(mash_distribute_node, i), _ramp_interp)
        i += 1

    # mash breakout
    mash_breakout_node = node(type=naming.Type.MASH_Breakout, side=_side, description=_des, index=_index,
                              suffix=_suffix)
    cmds.connectAttr(mash_distribute_node+'.outputPoints', mash_breakout_node+'.inputPoints')

    return mash_distribute_node, mash_breakout_node


#  SUB FUNCTION
def _create_node_multi_attrs(input_attr_single, input_attr_multi, node_attr_single,
                             node_attr_multi, node_sub_attrs, output_attr, **kwargs):
    """
    create node with multi attrs (like RGB/XYZ), connect with attrs

    Args:
        input_attr_single(list): input single channel attr, use [] to skip
        input_attr_multi(list): input multi channel attr
        node_attr_single(list): connect input single channel attr to the node's given attr, use [] to skip
        node_attr_multi(list): connect input multi channel attr to the node's given attr
                              it should only be the parent attribute, like 'translate', not 'translateX', 'translateY'
        node_sub_attrs(list): multi channel attr's sub name,
                             'translate' would be ['X', 'Y, 'Z']
                             'outColor' would be ['R', 'G', 'B']
        output_attr(str): node output attr, like 'outColor' or 'output'

    Keyword Args:
        type(str): node's type
        side(str): node's side
        description(str): node's description
        index(int): node's index
        suffix(int): node's suffix
        set_attrs(dict): node's parameters
        attrs(list): connect node's output to the given attrs
        force(bool): force the connection, default is True

    Returns:
        output_attrs(list): node's output attrs
        node(str): node's name

    """

    # get vars
    _type = kwargs.get('type', None)
    _side = kwargs.get('side', None)
    _des = kwargs.get('description', None)
    _index = kwargs.get('index', None)
    _suffix = kwargs.get('suffix', None)
    _set_attrs = kwargs.get('set_attrs', {})
    _attrs = kwargs.get('attrs', [])
    _force = kwargs.get('force', True)

    # create node
    _node = node(type=_type, side=_side, description=_des,
                 index=_index, suffix=_suffix, set_attrs=_set_attrs)

    # connect input
    for input_attr_info in zip(input_attr_single, node_attr_single):
        if isinstance(input_attr_info[0], basestring):
            cmds.connectAttr(input_attr_info[0], '{}.{}'.format(_node, input_attr_info[1]))
        else:
            cmds.setAttr('{}.{}'.format(_node, input_attr_info[1]), input_attr_info[0])

    input_attr_list = []
    input_attr_num = []
    for input_val in input_attr_multi:
        if not isinstance(input_val, list) and not isinstance(input_val, tuple):
            input_val = [input_val]
        input_attr_list.append(input_val)
        input_attr_num.append(len(input_val))

    for input_attr_info in zip(input_attr_list, node_attr_multi):
        for input_val in zip(input_attr_info[0], node_sub_attrs):
            if isinstance(input_val[0], basestring):
                cmds.connectAttr(input_val[0],
                                 '{}.{}{}'.format(_node, input_attr_info[1], input_val[1]))
            else:
                cmds.setAttr('{}.{}{}'.format(_node, input_attr_info[1], input_val[1]),
                             input_val[0])

    output_num = min(input_attr_num)

    output_attr_list = []
    for attr_info in zip(range(output_num), node_sub_attrs):
        output_attr_list.append('{}.{}{}'.format(_node, output_attr, attr_info[1]))

    # connect output
    if _attrs:
        if isinstance(_attrs, basestring):
            _attrs = [_attrs]
        elif isinstance(_attrs[0], basestring):
            _attrs = [_attrs]
        for attr_info in zip(output_attr_list, _attrs):
            attributes.connect_attrs(attr_info[0], attr_info[1], force=_force)

    # return output attr
    return output_attr_list, _node


# operation functions
def _add(left, right, **kwargs):
    """
    connect left and right attr with addDoubleLinear node
    """
    side = kwargs.get('side', None)
    des = kwargs.get('description', None)
    index = kwargs.get('index', None)

    is_str_left = isinstance(left, basestring)
    is_str_right = isinstance(right, basestring)

    if is_str_left or is_str_right:
        add_node = node(type=naming.Type.addDoubleLinear,
                        side=side, description=des, index=index,
                        auto_suffix=True)

        for attr_info in zip([left, right],
                             [is_str_left, is_str_right],
                             ['input1', 'input2']):
            if attr_info[1]:
                cmds.connectAttr(attr_info[0], '{}.{}'.format(add_node, attr_info[2]))
            else:
                cmds.setAttr('{}.{}'.format(add_node, attr_info[2]), attr_info[0])

        return add_node+'.output'
    else:
        return left+right


def _mult(left, right, **kwargs):
    """
    connect left and right attr with multDoubleLinear node
    """
    side = kwargs.get('side', None)
    des = kwargs.get('description', None)
    index = kwargs.get('index', None)

    is_str_left = isinstance(left, basestring)
    is_str_right = isinstance(right, basestring)

    if is_str_left or is_str_right:
        mult_node = node(type=naming.Type.multDoubleLinear,
                         side=side, description=des, index=index,
                         auto_suffix=True)

        for attr_info in zip([left, right],
                             [is_str_left, is_str_right],
                             ['input1', 'input2']):
            if attr_info[1]:
                cmds.connectAttr(attr_info[0], '{}.{}'.format(mult_node, attr_info[2]))
            else:
                cmds.setAttr('{}.{}'.format(mult_node, attr_info[2]), attr_info[0])

        return mult_node+'.output'
    else:
        return left+right


def _sub(left, right, **kwargs):
    """
    connect left and right attr doing left-right equation node
    """
    side = kwargs.get('side', None)
    des = kwargs.get('description', None)
    index = kwargs.get('index', None)

    is_str_left = isinstance(left, basestring)
    is_str_right = isinstance(right, basestring)

    if is_str_left or is_str_right:
        add_node = node(type=naming.Type.addDoubleLinear,
                        side=side, description=des, index=index,
                        auto_suffix=True)

        if is_str_right:
            mult_node = node(type=naming.Type.multDoubleLinear,
                             side=side, des=des, index=index,
                             auto_suffix=True, set_attrs={'input2': -1})
            cmds.connectAttr(right, mult_node+'.input1')
            cmds.connectAttr(mult_node+'.output', add_node+'.input2')
        else:
            cmds.setAttr(add_node+'.input2', right)

        if is_str_left:
            cmds.connectAttr(left, add_node+'.input1')
        else:
            cmds.setAttr(add_node+'.input1', left)

        return add_node+'.output'
    else:
        return left-right


def _divide(left, right, **kwargs):
    """
    connect left and right attr with multiplyDivide node
    set operation to divide
    """
    side = kwargs.get('side', None)
    des = kwargs.get('description', None)
    index = kwargs.get('index', None)

    is_str_left = isinstance(left, basestring)
    is_str_right = isinstance(right, basestring)

    if is_str_left or is_str_right:
        divide_node = node(type=naming.Type.multiplyDivide,
                           side=side, description=des, index=index,
                           auto_suffix=True, set_attrs={'operation': 2})

        for attr_info in zip([left, right],
                             [is_str_left, is_str_right],
                             ['input1X', 'input2X']):
            if attr_info[1]:
                cmds.connectAttr(attr_info[0], '{}.{}'.format(divide_node, attr_info[2]))
            else:
                cmds.setAttr('{}.{}'.format(divide_node, attr_info[2]), attr_info[0])

        return divide_node+'.outputX'
    else:
        return left/float(right)


def _pow(left, right, **kwargs):
    """
    connect left and right attr with multiplyDivide node
    set operation to power
    """
    side = kwargs.get('side', None)
    des = kwargs.get('description', None)
    index = kwargs.get('index', None)

    is_str_left = isinstance(left, basestring)
    is_str_right = isinstance(right, basestring)

    if is_str_left or is_str_right:
        pow_node = node(type=naming.Type.multiplyDivide,
                        side=side, description=des, index=index,
                        auto_suffix=True, set_attrs={'operation': 3})

        for attr_info in zip([left, right],
                             [is_str_left, is_str_right],
                             ['input1X', 'input2X']):

            if attr_info[1]:
                cmds.connectAttr(attr_info[0], '{}.{}'.format(pow_node, attr_info[2]))
            else:
                cmds.setAttr('{}.{}'.format(pow_node, attr_info[2]), attr_info[0])

        return pow_node+'.outputX'
    else:
        return left**right


def _reverse(operand, **kwargs):
    """
    connect operand attr with reverse node
    """
    side = kwargs.get('side', None)
    des = kwargs.get('description', None)
    index = kwargs.get('index', None)

    rvs_node = node(type=naming.Type.reverse,
                    side=side, description=des, index=index,
                    auto_suffix=True)
    cmds.connectAttr(operand, rvs_node+'.inputX')

    return rvs_node+'.outputX'


def _uSub(operand, **kwargs):
    """
    connect operand attr with multDoubleLinear node
    set input2 to -1
    """
    side = kwargs.get('side', None)
    des = kwargs.get('description', None)
    index = kwargs.get('index', None)

    is_str = isinstance(operand, basestring)
    if is_str:
        mult_node = node(type=naming.Type.multDoubleLinear,
                         side=side, description=des, index=index,
                         auto_suffix=True, set_attrs={'input2': -1})

        cmds.connectAttr(operand, mult_node+'.input1')

        return mult_node+'.output'
    else:
        return -operand


#  SUB CLASS

# operation
_BINOP_MAP = {
                ast.Add: _add,
                ast.Sub: _sub,
                ast.Mult: _mult,
                ast.Div: _divide,
                ast.Pow: _pow}

_UNARYOP_MAP = {
                ast.USub: _uSub,
                ast.Invert: _reverse}


class NodeEquation(ast.NodeVisitor):

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return _BINOP_MAP[type(node.op)](left, right,
                                         side=self.side,
                                         description=self.des,
                                         index=self.index)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        return _UNARYOP_MAP[type(node.op)](operand,
                                           side=self.side,
                                           description=self.des,
                                           index=self.index)

    def visit_Num(self, node):
        return node.n

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Attribute(self, node):
        return '{}.{}'.format(node.value.id, node.attr)

    @classmethod
    def equation(cls, expression, **kwargs):
        cls.side = kwargs.get('side', None)
        cls.des = kwargs.get('description', None)
        cls.index = kwargs.get('index', None)

        tree = ast.parse(expression)
        calc = cls()
        return calc.visit(tree.body[0])
