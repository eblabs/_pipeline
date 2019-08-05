# IMPORT PACKAGES

# import system packages
import os

# import string
import string

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.variables as variables
import utils.common.files as files
import utils.common.naming as naming
import utils.common.logUtils as logUtils
import utils.common.attributes as attributes
import utils.common.transforms as transforms
import utils.common.nodeUtils as nodeUtils
import utils.common.apiUtils as apiUtils
import utils.common.mathUtils as mathUtils
import utils.modeling.curves as curves

# CONSTANT
import config
CONFIG_PATH = os.path.dirname(config.__file__)
SHAPE_CONFIG = files.read_json_file(os.path.join(CONFIG_PATH, 'CONTROL_SHAPE.cfg'))
COLOR_CONFIG = files.read_json_file(os.path.join(CONFIG_PATH, 'CONTROL_COLOR.cfg'))
SIDE_CONFIG = files.read_json_file(os.path.join(CONFIG_PATH, 'CONTROL_SIDE_COLOR.cfg'))

ASCII = string.ascii_uppercase

logger = logUtils.get_logger(name='controls', level='info')


# CLASS
class Control(object):
    """class to get control information"""
    def __init__(self, ctrl):
        super(Control, self).__init__()
        self.__name = None
        self.__side = None
        self.__des = None
        self.__index = None
        self.__suffix = None
        self.__get_control_info(ctrl)

    @property
    def name(self):
        return self.__name

    @property
    def n(self):
        return self.__name

    @property
    def side(self):
        return self.__side

    @property
    def s(self):
        return self.__side

    @property
    def description(self):
        return self.__des

    @property
    def des(self):
        return self.__des

    @property
    def index(self):
        return self.__index

    @property
    def i(self):
        return self.__index

    @property
    def zero(self):
        return self.__zero

    @property
    def drive(self):
        return self.__drive

    @property
    def space(self):
        return self.__space

    @property
    def offsets(self):
        return self.__offsets

    @property
    def output(self):
        return self.__output

    @property
    def sub(self):
        return self.__sub

    @property
    def local_matrix(self):
        matrix = cmds.getAttr(self.__local_matrix_attr)
        return matrix

    @property
    def local_matrix_attr(self):
        return self.__local_matrix_attr

    @property
    def world_matrix(self):
        matrix = cmds.getAttr(self.__world_matrix_attr)
        return matrix

    @property
    def world_matrix_attr(self):
        return self.__world_matrix_attr

    @side.setter
    def side(self, key):
        self.__side = key
        self.__update_control_name()

    @s.setter
    def s(self, key):
        self.__side = key
        self.__update_control_name()

    @description.setter
    def description(self, key):
        self.__des = key
        self.__update_control_name()

    @des.setter
    def des(self, key):
        self.__des = key
        self.__update_control_name()

    @index.setter
    def index(self, num):
        self.__index = num
        self.__update_control_name()

    @i.setter
    def i(self, num):
        self.__index = num
        self.__update_control_name()

    @offsets.setter
    def offsets(self, num):
        if isinstance(num, int) and num > 0:
            self.__update_offsets(num)
        else:
            logger.warning('Given number: {} is invalid, must be an integer'.format(num))

    @sub.setter
    def sub(self, key):
        self.__update_sub(key)

    def __get_control_info(self, ctrl):
        """
        get control's information

        Args:
            ctrl(str): control's name
        """

        self.__name = ctrl
        self.__ctrls = [self.__name]

        namer_ctrl = naming.Namer(ctrl)

        self.__side = namer_ctrl.side
        self.__des = namer_ctrl.description
        self.__index = namer_ctrl.index

        # zero
        namer_ctrl.type = naming.Type.zero
        self.__zero = namer_ctrl.name

        # drive
        namer_ctrl.type = naming.Type.drive
        self.__drive = namer_ctrl.name

        # space
        namer_ctrl.type = naming.Type.space
        self.__space = namer_ctrl.name

        # controlShape
        namer_ctrl.type = naming.Type.controlShape
        self.__ctrl_shape = namer_ctrl.name

        # output
        namer_ctrl.type = naming.Type.output
        self.__output = namer_ctrl.name

        # offsets
        namer_ctrl.type = naming.Type.offset
        namer_ctrl.description += '?'  # remove the last letter to search all
        self.__offsets = cmds.ls(namer_ctrl.name, type='transform')  # get all offset controls

        # sub
        namer_ctrl.type = naming.Type.control
        namer_ctrl.description = namer_ctrl.description[:-1] + 'Sub'  # remove the ? we added on offset
        if cmds.objExists(namer_ctrl.name):
            self.__sub = namer_ctrl.name
            self.__ctrls.append(self.__sub)
            namer_ctrl.type = naming.Type.controlShape
            self.__subShape = namer_ctrl.name
        else:
            self.__sub = None
            self.__subShape = None

        self.__local_matrix_attr = self.__name+'.matrixLocal'
        self.__world_matrix_attr = self.__name+'.matrixWorld'
        self.__mult_matrix = cmds.listConnections(self.__local_matrix_attr,
                                                  s=True, d=False, p=False)[0]

    def __update_control_name(self):
        """
        update control nodes' names
        """
        namer_ctrl = naming.Namer(type=naming.Type.zero, side=self.__side,
                                  description=self.__des, index=self.__index)
        # zero
        self.__zero = cmds.rename(self.__zero, namer_ctrl.name)

        # drive
        namer_ctrl.type = naming.Type.drive
        self.__drive = cmds.rename(self.__drive, namer_ctrl.name)

        # space
        namer_ctrl.type = naming.Type.space
        self.__space = cmds.rename(self.__space, namer_ctrl.name)

        # offsets
        namer_ctrl.type = naming.Type.offset
        for i, offset in enumerate(self.__offsets):
            namer_ctrl.description += ASCII[i]  # add ASCII letter for different offset
            self.__offsets[i] = cmds.rename(self.__offsets[i], namer_ctrl.name)
            namer_ctrl.description = namer_ctrl.description[:-1]  # remove the letter

        # control
        namer_ctrl.type = naming.Type.control
        namer_ctrl.suffix = None
        namer_ctrl.index = self.__index
        self.__name = cmds.rename(self.__name, namer_ctrl.name)
        self.__ctrls[0] = self.__name

        # control shape
        namer_ctrl.type = naming.Type.controlShape
        self.__ctrl_shape = cmds.rename(self.__ctrl_shape, namer_ctrl.name)

        # output
        namer_ctrl.type = naming.Type.output
        self.__output = cmds.rename(self.__output, namer_ctrl.name)

        # sub
        if self.__sub:
            namer_ctrl.type = naming.Type.control
            namer_ctrl.part = namer_ctrl.part + 'Sub'
            self.__sub = cmds.rename(self.__sub, namer_ctrl.name)
            self.__ctrls[1] = self.__sub
            namer_ctrl.type = naming.Type.controlShape
            self.__subShape = cmds.rename(self.__subShape, namer_ctrl.name)

        # mult matrix node
        namer_ctrl.type = naming.Type.multMatrix
        namer_ctrl.part = namer_ctrl.part.replace('Sub', 'LocalMatrix')
        self.__mult_matrix = cmds.rename(self.__mult_matrix, namer_ctrl.name)

    def __update_offsets(self, num):
        """
        update control's offset groups

        Args:
            num(int): offset groups num, minimum is 1
        """

        offset_num = len(self.__offsets)
        children = cmds.listRelatives(self.__offsets[-1], c=True, type='transform')  # get nodes under the last offset

        if num < offset_num:
            # delete extra offsets
            cmds.parent(children, self.__offsets[num-1])  # parent to the last offset group we want to keep
            cmds.delete(self.__offsets[num])  # delete the rest
            self.__offsets = self.__offsets[:num]  # update in-class variable

        elif num > offset_num:
            # add more offsets
            namer = naming.Namer(self.__offsets[-1])
            parent = self.__offsets[-1]

            for i in range(num-offset_num):
                # remove the previous ASCII letter, add new one
                namer.description = namer.description[:-1] + ASCII[offset_num+i]
                offset = transforms.create(namer.name, parent=parent, pos=parent)
                self.__offsets.append(offset)
                parent = offset

            # re-parent children
            cmds.parent(children, self.__offsets[-1])

    def __update_sub(self, key):
        """
        update control's sub control

        Args:
            key(bool)
        """

        if not key and self.__sub:
            # delete sub
            cmds.delete(self.__sub)
            # delete vis attr
            cmds.deleteAttr(self.__name+'.subControlVis')
            self.__sub = None
            self.__subShape = None
            self.__ctrls = self.__ctrls[:-1]  # remove sub control from control list

        elif key and not self.__sub:
            # add sub
            namer = naming.Namer(type=naming.Type.control, side=self.__side,
                                 description=self.__des+'Sub', index=self.__index)

            # get lock hide attrs from control
            lock_hide = []
            for attr in attributes.Attr.all:
                if not attributes.attr_in_channel_box(self.__name, attr):
                    # check if the attr in control's channel box, lock and hide if not
                    lock_hide.append(attr)

            self.__sub = transforms.create(namer.name, parent=self.__name,
                                           pos=self.__name, lock_hide=lock_hide)  # create sub control transform node
            self.__ctrls.append(self.__sub)  # add sub control to control list

            # connect output
            attributes.connect_attrs(attributes.Attr.all+['rotateOrder'],
                                     attributes.Attr.all+['rotateOrder'],
                                     driver=self.__sub, driven=self.__output)

            # sub vis
            attributes.add_attrs(self.__name, 'subControlVis', attribute_type='long',
                                 range=[0, 1], default_value=0, keyable=False,
                                 channel_box=True)
            cmds.connectAttr(self.__name+'.subControlVis', self.__sub+'.v', force=True)

            # unlock rotate order
            attributes.unlock_attrs(self.__sub, 'rotateOrder', channel_box=True)

            # shape
            self.match_sub_ctrl_shape()
            namer.type = naming.Type.controlShape
            self.__subShape = namer.name

    def match_sub_ctrl_shape(self):
        """
        match sub control's control shape to the controller
        """
        if self.__sub:
            ctrl_shape_info = curves.get_curve_info(self.__ctrl_shape)  # get curve info
            color = cmds.getAttr(self.__ctrl_shape+'.overrideColor')  # get color
            _add_ctrl_shape(self.__sub, shapeInfo=ctrl_shape_info, size=0.9, color=color)

    def lock_hide_attrs(self, attrs):
        """
        lock hide control's attrs

        Args:
            attrs(str/list): attributes to be locked and hidden
        """

        attributes.lock_hide_attrs(self.__ctrls, attrs)

    def unlock_attrs(self, attrs, **kwargs):
        """
        unlock control's attrs

        Args:
            attrs(str/list): attributes

        Keyword Args:
            keyable(bool)
            channel_box(bool)
        """

        attributes.unlock_attrs(self.__ctrls, attrs, **kwargs)

    def add_attrs(self, attrs, **kwargs):
        """
        add attrs, only for main control

        Args:
            attrs(str/list): add attrs

        Keyword Args:
            attributeType(str): 'bool', 'long', 'enum', 'float', 'double',
                                'string', 'matrix', 'message',
                                default is 'float'
            range(list): min/max value
            default_value(float/int/list): default value
            keyable(bool): set attr keyable
            channel_box(bool): show attr in channel box
            enum_name(str): enum attr name
            multi(m): add attr as a multi-attribute
            lock(bool): lock attr
        """

        attributes.add_attrs(self.__ctrls[0], attrs, **kwargs)


# FUNCTION
def create(description, **kwargs):
    """
    create control

    hierarchy:
    -zero
    --drive
    ---space
    ----offset_001
    -----offset_002
    ------offset_...
    -------control
    --------sub control
    --------output

    Args:
        description(str): control's name's description

    Keyword Args:
        side(str): control's side, default is middle
        index(int): control's index
        sub(bool): if control has sub control, default is True
        offsets(int): control's offset groups number, default is 1, minimum is 1
        parent(str): where to parent the control
        pos(str/list): match control's position to given node/transform value
                       str: match translate and rotate to the given node
                       [str/None, str/None]: match translate/rotate to the given node
                       [[x,y,z], [x,y,z]]: match translate/rotate to given values
        rotate_order(int): control's initial rotate order, default is 0
        shape(str): control's shape, default is 'cube'
        size(float/list): control shape's size, default is 1
        color(string/int): control shape's color, follow side preset if None
        color_sub(string/int): sub control shape's color, follow control's color if None
        lock_hide(list): lock and hide control's attributes

    Returns:
        control(obj): control object
    """

    # get vars
    side = variables.kwargs('side', naming.Side.middle, kwargs, short_name='s')
    index = variables.kwargs('index', None, kwargs, short_name='i')
    sub = variables.kwargs('sub', True, kwargs)
    offsets = variables.kwargs('offsets', 1, kwargs, short_name='ofst')
    parent = variables.kwargs('parent', None, kwargs, short_name='p')
    pos = variables.kwargs('pos', None, kwargs)
    rotate_order = variables.kwargs('rotate_order', 0, kwargs, short_name='ro')
    shape = variables.kwargs('shape', 'cube', kwargs)
    size = variables.kwargs('size', 1, kwargs)
    color = variables.kwargs('color', None, kwargs, short_name='col')
    color_sub = variables.kwargs('colorSub', None, kwargs, short_name='col_sub')
    lock_hide = variables.kwargs('lockHide', attributes.Attr.scaleVis, kwargs, short_name='lh')

    namer = naming.Namer(type=naming.Type.control, side=side,
                         description=description, index=index)  # get naming object

    if attributes.Attr.vis[0] not in lock_hide:
        lock_hide.append(attributes.Attr.vis[0])  # make sure to add visibility to lock hide list

    # build hierarchy
    transform_nodes = []
    for trans in ['zero', 'drive', 'space', 'control', 'output']:
        namer.type = getattr(naming.Type, trans)  # get node type's name from naming
        transform = transforms.create(namer.name, parent=parent)  # create transform node
        transform_nodes.append(transform)
        parent = transform

    ctrl = transform_nodes[3]  # get control transform node
    ctrl_list = [ctrl]  # create a control list to set attr for both control and sub control (sub is optional)

    # offset
    namer.type = naming.Type.offset
    parent = transform_nodes[2]
    for i in range(offsets):
        namer.description = namer.description + ASCII[i]
        offset = transforms.create(namer.name, parent=parent)

        parent = offset
        namer.description = namer.description[:-1]  # remove ASCII letter

    # parent control to parent
    cmds.parent(ctrl, parent)

    # sub control
    if sub:
        namer.type = naming.Type.control
        namer.description += 'Sub'
        namer.index = index

        sub = transforms.create(namer.name, parent=ctrl)
        ctrl_list.append(sub)

        # connect sub control with output
        attributes.connect_attrs(attributes.Attr.transform+['rotateOrder'], attributes.Attr.transform+['rotateOrder'],
                                 driver=sub, driven=transform_nodes[4])

        # sub vis
        attributes.add_attrs(ctrl, 'subControlVis', attributeType='long', range=[0, 1], defaultValue=0, keyable=False,
                             channel_box=True)
        attributes.connect_attrs(ctrl+'.subControlVis', sub+'.v', force=True)

    # unlock rotate order
    attributes.unlock_attrs(ctrl_list, 'rotateOrder', channel_box=True)

    # lock hide
    attributes.lock_hide_attrs(ctrl_list, lock_hide)

    # set rotate order for control and sub control
    for ctrl in ctrl_list:
        cmds.setAttr(ctrl+'.rotateOrder', rotate_order)

    # add output attrs
    attributes.add_attrs(ctrl, ['matrixLocal', 'matrixWorld'], attributeType='matrix')

    nodeUtils.mult_matrix([transform_nodes[-1]+'.worldMatrix[0]', transform_nodes[0]+'.parentInverseMatrix[0]'],
                          attrs=ctrl+'.matrixWorld', side=side, description=description+'WorldMatrix', index=index)

    nodeUtils.mult_matrix([transform_nodes[-1]+'.worldMatrix[0]', transform_nodes[0]+'.worldInverseMatrix[0]'],
                          attrs=ctrl+'.matrixLocal', side=side, description=description+'LocalMatrix', index=index)

    # set pos
    if pos:
        transforms.set_pos(transform_nodes[0], pos)

    # add shape
    for c, col, scale in zip(ctrl_list, [color, color_sub], [size, size*0.9]):
        _add_ctrl_shape(c, shape=shape, size=scale, color=col)

    # return control object
    return Control(ctrl)


def transform_ctrl_shape(ctrl_shapes, **kwargs):
    """
    offset controls shape nodes

    Args:
        ctrl_shapes(str/list): controls shape nodes
    Keyword Args:
        translate(float/list): translate
        rotate(float/list): rotate
        scale(float/list): scale
        pivot(str): transform/shape, define the offset pivot, default is 'transform'
    """
    # vars
    translate = variables.kwargs('translate', None, kwargs, short_name='t')
    rotate = variables.kwargs('rotate', None, kwargs, short_name='r')
    scale = variables.kwargs('scale', None, kwargs, short_name='s')
    pivot = variables.kwargs('pivot', 'transform', kwargs)

    if translate is None:
        translate = [0, 0, 0]
    if rotate is None:
        rotate = [0, 0, 0]
    if scale is None:
        scale = [1, 1, 1]

    if isinstance(ctrl_shapes, basestring):
        ctrl_shapes = [ctrl_shapes]
    if not isinstance(scale, list):
        scale = [scale, scale, scale]

    for shape in ctrl_shapes:
        if cmds.objExists(shape):
            ctrl_shape_info = curves.get_curve_info(shape)
            cv_points = ctrl_shape_info['controlVertices']

            matrix_offset = apiUtils.compose_matrix(translate=translate, rotate=rotate, scale=scale)

            # get pivot matrix
            if pivot == 'shape':
                pos_max, pos_min, pos_center = transforms.bounding_box_info(cv_points)
                matrix_pivot = apiUtils.compose_matrix(translate=pos_center)
            else:
                matrix_pivot = mathUtils.MATRIX_DEFAULT

            # get pivot inverse matrix
            inverse_matrix_pivot = mathUtils.inverse_matrix(matrix_pivot)

            # move each point
            for i, pnt in enumerate(cv_points):
                # get point's matrix
                matrix_point = apiUtils.compose_matrix(translate=pnt)

                # mult matrix
                matrix_pos = mathUtils.mult_matrix([matrix_point, inverse_matrix_pivot,
                                                   matrix_offset, matrix_pivot])

                # get pos
                pos = apiUtils.decompose_matrix(matrix_pos)[0]

                cv_points[i] = pos

            # set pos
            curves.set_curve_points(shape, cv_points)

        else:
            logger.warning('{} does not exist'.format(shape))


def add_ctrls_shape(ctrls, **kwargs):
    """
    add shape node to controller

    Args:
        ctrls(str/list): control's name

    Keyword Args:
        shape(str): control's shape, default is 'cube'
        size(float): control shape's size, default is size
        color(str/int): control's color, None will follow the side preset
        transform(str/list): if add shape node as control, the shape node would parented to the given transforms
        shape_info(dict): if has custom shape node (like copy/paste)
    """

    if isinstance(ctrls, basestring):
        ctrls = [ctrls]

    for c in ctrls:
        _add_ctrl_shape(c, **kwargs)


# SUB FUNCTION
def _add_ctrl_shape(ctrl, **kwargs):
    """
    add shape node to controller

    Args:
        ctrl(str): control's name

    Keyword Args:
        shape(str): control's shape, default is 'cube'
        size(float): control shape's size, default is size
        color(str/int): control's color, None will follow the side preset
        transform(str/list): if add shape node as control, the shape node would parented to the given transforms
        shape_info(dict): if has custom shape node (like copy/paste)
    """
    shape = kwargs.get('shape', 'cube')
    size = kwargs.get('size', 1)
    color = kwargs.get('color', None)
    transform = kwargs.get('transform', None)
    shape_info = kwargs.get('shapeInfo', None)

    if transform and isinstance(transform, basestring):
        transform = [transform]

    if not shape_info:
        shape_info = SHAPE_CONFIG[shape]  # get shape info from config

    if transform and cmds.objExists(ctrl):
        for trans in transform:
            s = cmds.listRelatives(trans, s=True)  # get shapes
            if ctrl not in s:
                cmds.parent(ctrl, trans, shape=True, addObject=True)  # add shape node to transforms
        return

    # create temp curve
    crv_transform, crv_shape = curves.create_curve('TEMP_CRV', shape_info['controlVertices'], shape_info['knots'],
                                                   degree=shape_info['degree'], form=shape_info['form'])

    if not transform:
        # normal control
        namer = naming.Namer(ctrl)
        namer.type = naming.Type.controlShape
        if cmds.objExists(namer.name):
            # if shape node exists, delete it
            cmds.delete(namer.name)
        # rename the shape node created to the control shape node name
        crv_shape = cmds.rename(crv_shape, namer.name)
        transform = [ctrl]

        # set color
        if not color:
            # use preset if not given
            side_col = SIDE_CONFIG[namer.side]  # get color's key
            color = COLOR_CONFIG[side_col]  # get color information
        else:
            if isinstance(color, basestring):
                color = COLOR_CONFIG[color]  # get color information from config

        cmds.setAttr(crv_shape+'.overrideEnabled', 1)
        cmds.setAttr(crv_shape+'.overrideColor', color)

        # size
        transform_ctrl_shape(crv_shape, scale=size)  # scale control shape

    else:
        # curve shape as control
        crv_shape = cmds.rename(crv_shape, ctrl)  # rename shape node as control
        attributes.set_attrs(crv_shape+'.v', 0, force=True)  # hide shape node

    # assign shape
    for trans in transform:
        cmds.parent(crv_shape, trans, shape=True, addObject=True)  # parent shape node under transform

    cmds.delete('TEMP_CRV')  # delete the temp transform node

    # return shape node
    return crv_shape
