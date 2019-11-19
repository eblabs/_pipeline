# IMPORT PACKAGES

# import system packages
import os

# import string
import string

# import ast
import ast

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
import constraints

# CONSTANT
import config
CONFIG_PATH = os.path.dirname(config.__file__)
SHAPE_CONFIG = files.read_json_file(os.path.join(CONFIG_PATH, 'CONTROL_SHAPE.cfg'))
COLOR_CONFIG = files.read_json_file(os.path.join(CONFIG_PATH, 'CONTROL_COLOR.cfg'))
SIDE_CONFIG = files.read_json_file(os.path.join(CONFIG_PATH, 'CONTROL_SIDE_COLOR.cfg'))
SPACE_CONFIG = files.read_json_file(os.path.join(CONFIG_PATH, 'SPACE.cfg'))

ASCII = string.ascii_uppercase

logger = logUtils.logger

CTRL_SHAPE_INFO_FORMAT = '.ctrlShapeInfo'
CTRL_SHAPE_INFO_DEFAULT_NAME = 'ctrlShapes'
CTRL_SPACE_INFO_FORMAT = '.spaceInfo'
CTRL_SPACE_INFO_DEFAULT_NAME = 'spaces'

CUSTOM_SPACE_INDEX = 50


# CLASS
class Control(object):
    """class to get control information"""
    def __init__(self, ctrl):
        super(Control, self).__init__()
        self._name = None
        self._side = None
        self._des = None
        self._index = None
        self._suffix = None

        self._space_info = {}

        self._get_control_info(ctrl)

    @ property
    def name(self):
        return self._name

    @ property
    def n(self):
        return self._name

    @ property
    def side(self):
        return self._side

    @ property
    def s(self):
        return self._side

    @ property
    def description(self):
        return self._des

    @ property
    def des(self):
        return self._des

    @ property
    def index(self):
        return self._index

    @ property
    def i(self):
        return self._index

    @ property
    def zero(self):
        return self._zero

    @ property
    def drive(self):
        return self._drive

    @ property
    def space(self):
        return self._space

    @ property
    def offsets(self):
        return self._offsets

    @ property
    def output(self):
        return self._output

    @ property
    def control_shape(self):
        return self._ctrl_shape

    @ property
    def sub(self):
        return self._sub

    @ property
    def sub_control_shape(self):
        return self._sub_shape

    @ property
    def local_matrix(self):
        matrix = cmds.getAttr(self._local_matrix_attr)
        return matrix

    @ property
    def local_matrix_attr(self):
        return self._local_matrix_attr

    @ property
    def world_matrix(self):
        matrix = cmds.getAttr(self._world_matrix_attr)
        return matrix

    @ property
    def world_matrix_attr(self):
        return self._world_matrix_attr

    @ property
    def space_info(self):
        return get_space_info(self._name)

    @ side.setter
    def side(self, key):
        self._side = key
        self._update_control_name()

    @ s.setter
    def s(self, key):
        self._side = key
        self._update_control_name()

    @ description.setter
    def description(self, key):
        self._des = key
        self._update_control_name()

    @ des.setter
    def des(self, key):
        self._des = key
        self._update_control_name()

    @ index.setter
    def index(self, num):
        self._index = num
        self._update_control_name()

    @ i.setter
    def i(self, num):
        self._index = num
        self._update_control_name()

    @ offsets.setter
    def offsets(self, num):
        if isinstance(num, int) and num > 0:
            self._update_offsets(num)
        else:
            logger.warning('Given number: {} is invalid, must be an integer'.format(num))

    @ sub.setter
    def sub(self, key):
        self._update_sub(key)

    def _get_control_info(self, ctrl):
        """
        get control's information

        Args:
            ctrl(str): control's name
        """

        self._name = ctrl
        self._ctrls = [self._name]

        namer_ctrl = naming.Namer(ctrl)

        self._side = namer_ctrl.side
        self._des = namer_ctrl.description
        self._index = namer_ctrl.index

        # zero
        namer_ctrl.type = naming.Type.zero
        self._zero = namer_ctrl.name

        # drive
        namer_ctrl.type = naming.Type.drive
        self._drive = namer_ctrl.name

        # space
        namer_ctrl.type = naming.Type.space
        self._space = namer_ctrl.name

        # controlShape
        namer_ctrl.type = naming.Type.controlShape
        self._ctrl_shape = namer_ctrl.name

        # output
        namer_ctrl.type = naming.Type.output
        self._output = namer_ctrl.name

        # offsets
        namer_ctrl.type = naming.Type.offset
        namer_ctrl.description += '?'  # remove the last letter to search all
        self._offsets = cmds.ls(namer_ctrl.name, type='transform')  # get all offset controls

        # sub
        namer_ctrl.type = naming.Type.control
        namer_ctrl.description = namer_ctrl.description[:-1] + 'Sub'  # remove the ? we added on offset
        if cmds.objExists(namer_ctrl.name):
            self._sub = namer_ctrl.name
            self._ctrls.append(self._sub)
            namer_ctrl.type = naming.Type.controlShape
            self._sub_shape = namer_ctrl.name
        else:
            self._sub = None
            self._sub_shape = None

        self._local_matrix_attr = self._name+'.matrixLocal'
        self._world_matrix_attr = self._name+'.matrixWorld'
        self._mult_matrix = cmds.listConnections(self._local_matrix_attr, s=True, d=False, p=False)[0]

    def _update_control_name(self):
        """
        update control nodes' names
        """
        namer_ctrl = naming.Namer(type=naming.Type.zero, side=self._side, description=self._des, index=self._index)
        # zero
        self._zero = cmds.rename(self._zero, namer_ctrl.name)

        # drive
        namer_ctrl.type = naming.Type.drive
        self._drive = cmds.rename(self._drive, namer_ctrl.name)

        # space
        namer_ctrl.type = naming.Type.space
        self._space = cmds.rename(self._space, namer_ctrl.name)

        # offsets
        namer_ctrl.type = naming.Type.offset
        for i, offset in enumerate(self._offsets):
            namer_ctrl.description += ASCII[i]  # add ASCII letter for different offset
            self._offsets[i] = cmds.rename(self._offsets[i], namer_ctrl.name)
            namer_ctrl.description = namer_ctrl.description[:-1]  # remove the letter

        # control
        namer_ctrl.type = naming.Type.control
        namer_ctrl.suffix = None
        namer_ctrl.index = self._index
        self._name = cmds.rename(self._name, namer_ctrl.name)
        self._ctrls[0] = self._name

        # control shape
        namer_ctrl.type = naming.Type.controlShape
        self._ctrl_shape = cmds.rename(self._ctrl_shape, namer_ctrl.name)

        # output
        namer_ctrl.type = naming.Type.output
        self._output = cmds.rename(self._output, namer_ctrl.name)

        # sub
        if self._sub:
            namer_ctrl.type = naming.Type.control
            namer_ctrl.part = namer_ctrl.part + 'Sub'
            self._sub = cmds.rename(self._sub, namer_ctrl.name)
            self._ctrls[1] = self._sub
            namer_ctrl.type = naming.Type.controlShape
            self._sub_shape = cmds.rename(self._sub_shape, namer_ctrl.name)

        # mult matrix node
        namer_ctrl.type = naming.Type.multMatrix
        namer_ctrl.part = namer_ctrl.part.replace('Sub', 'LocalMatrix')
        self._mult_matrix = cmds.rename(self._mult_matrix, namer_ctrl.name)

    def _update_offsets(self, num):
        """
        update control's offset groups

        Args:
            num(int): offset groups num, minimum is 1
        """

        offset_num = len(self._offsets)
        children = cmds.listRelatives(self._offsets[-1], c=True, type='transform')  # get nodes under the last offset

        offset_mult_matrix = naming.Namer(type=naming.Type.multMatrix, side=self._side,
                                          description=self._des+'OffsetMatrix', index=self._index).name

        # disconnect mult matrix
        for i in range(offset_num):
            cmds.disconnectAttr(self._offsets[offset_num-1-i]+'.matrix',
                                '{}.matrixIn[{}]'.format(offset_mult_matrix, i))

        if num < offset_num:
            # delete extra offsets
            cmds.parent(children, self._offsets[num-1])  # parent to the last offset group we want to keep
            cmds.delete(self._offsets[num])  # delete the rest
            self._offsets = self._offsets[:num]  # update in-class variable

        elif num > offset_num:
            # add more offsets
            namer = naming.Namer(self._offsets[-1])
            parent = self._offsets[-1]

            for i in range(num-offset_num):
                # remove the previous ASCII letter, add new one
                namer.description = namer.description[:-1] + ASCII[offset_num+i]
                offset = transforms.create(namer.name, parent=parent, pos=parent)
                self._offsets.append(offset)
                parent = offset

            # re-parent children
            cmds.parent(children, self._offsets[-1])

        # reconnect mult matrix node
        for i in range(num):
            cmds.connectAttr(self._offsets[num-1-i]+'.matrix', '{}.matrixIn[{}]'.format(offset_mult_matrix, i))

    def _update_sub(self, key):
        """
        update control's sub control

        Args:
            key(bool)
        """

        if not key and self._sub:
            # delete sub
            cmds.delete(self._sub)
            # delete vis attr
            cmds.deleteAttr(self._name+'.subControlVis')
            self._sub = None
            self._sub_shape = None
            self._ctrls = self._ctrls[:-1]  # remove sub control from control list

        elif key and not self._sub:
            # add sub
            namer = naming.Namer(type=naming.Type.control, side=self._side,
                                 description=self._des+'Sub', index=self._index)

            # get lock hide attrs from control
            lock_hide = []
            for attr in attributes.Attr.all:
                if not attributes.attr_in_channel_box(self._name, attr):
                    # check if the attr in control's channel box, lock and hide if not
                    lock_hide.append(attr)

            self._sub = transforms.create(namer.name, parent=self._name,
                                           pos=self._name, lock_hide=lock_hide)  # create sub control transform node
            self._ctrls.append(self._sub)  # add sub control to control list

            # connect output
            attributes.connect_attrs(attributes.Attr.all+attributes.Attr.rotateOrder,
                                     attributes.Attr.all+attributes.Attr.rotateOrder,
                                     driver=self._sub, driven=self._output)

            # sub vis
            attributes.add_attrs(self._name, 'subControlVis', attribute_type='long',
                                 range=[0, 1], default_value=0, keyable=False,
                                 channel_box=True)
            cmds.connectAttr(self._name+'.subControlVis', self._sub+'.v', force=True)

            # unlock rotate order
            attributes.unlock_attrs(self._sub, 'rotateOrder', channel_box=True)

            # shape
            self.match_sub_ctrl_shape()
            namer.type = naming.Type.controlShape
            self._sub_shape = namer.name

    def match_sub_ctrl_shape(self):
        """
        match sub control's control shape to the controller
        """
        if self._sub:
            ctrl_shape_info = curves.get_curve_shape_info(self._ctrl_shape)  # get curve info
            color = cmds.getAttr(self._ctrl_shape+'.overrideColor')  # get color
            _add_ctrl_shape(self._sub, shapeInfo=ctrl_shape_info, size=0.9, color=color)

    def lock_hide_attrs(self, attrs):
        """
        lock hide control's attrs

        Args:
            attrs(str/list): attributes to be locked and hidden
        """

        attributes.lock_hide_attrs(self._ctrls, attrs)

    def unlock_attrs(self, attrs, **kwargs):
        """
        unlock control's attrs

        Args:
            attrs(str/list): attributes

        Keyword Args:
            keyable(bool)
            channel_box(bool)
        """

        attributes.unlock_attrs(self._ctrls, attrs, **kwargs)

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

        attributes.add_attrs(self._ctrls[0], attrs, **kwargs)

    def add_space(self, **kwargs):
        """
        add spaces for controller's space node,
        it will either create the blend set up for spaces if no spaces, or add spaces to the existing setup
        it will also add space info to the given control for further query

        Keyword Args:
            parent(dict): add spaces behaves like parent constraint, template is space: matrix attribute,
                          it will be skipped if the control already had point/orient spaces
            point(dict): add spaces only for translation, it will be skipped if the control already had parent spaces
            orient(dict): add spaces only for rotation, it will be skipped if the control already had parent spaces
            scale(dict): add spaces only for scale
            parent_default(list): set default values for parent spaces, None will use either the first two from dict, or
                                  keep the previous value if already had any spaces
            point_default(list): set default values for point spaces
            orient_default(list): set default values for orient spaces
            scale_default(list): set default values for scale spaces
        """
        add_space(self._name, **kwargs)


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
    color_sub = variables.kwargs('color_sub', None, kwargs, short_name='col_sub')
    lock_hide = variables.kwargs('lock_hide', attributes.Attr.scaleVis, kwargs, short_name='lh')

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
    offset_matrix_attrs = []
    for i in range(offsets):
        namer.description = namer.description + ASCII[i]
        offset = transforms.create(namer.name, parent=parent)

        parent = offset
        offset_matrix_attrs.append(offset+'.matrix')
        namer.description = namer.description[:-1]  # remove ASCII letter

    offset_matrix_attrs.reverse()  # mult matrix starts from the child to parent

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
        attributes.connect_attrs(attributes.Attr.transform+attributes.Attr.rotateOrder,
                                 attributes.Attr.transform+attributes.Attr.rotateOrder,
                                 driver=sub, driven=transform_nodes[4])

        # sub vis
        attributes.add_attrs(ctrl, 'subControlVis', attributeType='long', range=[0, 1], defaultValue=0, keyable=False,
                             channel_box=True)
        attributes.connect_attrs(ctrl+'.subControlVis', sub+'.v', force=True)

    # unlock rotate order
    attributes.unlock_attrs(ctrl_list, 'rotateOrder', channel_box=True)

    # set rotate order for control and sub control
    for ctrl in ctrl_list:
        cmds.setAttr(ctrl+'.rotateOrder', rotate_order)

    # lock hide
    attributes.lock_hide_attrs(ctrl_list, lock_hide)

    ctrl = ctrl_list[0]
    # add output attrs
    attributes.add_attrs(ctrl, ['matrixLocal', 'matrixWorld'], attribute_type='matrix')

    # offset mult matrix
    offset_mult_matrix_attr = nodeUtils.mult_matrix(offset_matrix_attrs, side=side,
                                                    description=description+'OffsetsMatrix', index=index)

    # local matrix
    local_mult_matrix_attr = nodeUtils.mult_matrix([transform_nodes[4]+'.matrix', transform_nodes[3]+'.matrix',
                                                    offset_mult_matrix_attr, transform_nodes[2]+'.matrix',
                                                    transform_nodes[1]+'.matrix'],
                                                   attrs=ctrl+'.matrixLocal', side=side,
                                                   description=description+'LocalMatrix', index=index)

    # world matrix
    nodeUtils.mult_matrix([local_mult_matrix_attr, transform_nodes[0]+'.matrix'],
                          attrs=ctrl+'.matrixWorld', side=side, description=description+'WorldMatrix', index=index)

    # set pos
    if pos:
        transforms.set_pos(transform_nodes[0], pos)

    # add shape
    for c, col, scale in zip(ctrl_list, [color, color_sub], [size, size*0.9]):
        _add_ctrl_shape(c, shape=shape, size=scale, color=col)

    # return control object
    return Control(ctrl)


def add_space(ctrl, **kwargs):
    """
    add spaces for given controller's space node,
    it will either create the blend set up for spaces if no spaces, or add spaces to the existing setup
    it will also add space info to the given control for further query

    Args:
        ctrl(str): control name
    Keyword Args:
        parent(dict): add spaces behaves like parent constraint, template is space: matrix attribute,
                      it will be skipped if the control already had point/orient spaces
        point(dict): add spaces only for translation, it will be skipped if the control already had parent spaces
        orient(dict): add spaces only for rotation, it will be skipped if the control already had parent spaces
        scale(dict): add spaces only for scale
        parent_default(list): set default values for parent spaces, None will use either the first two from dict, or
                              keep the previous value if already had any spaces
        point_default(list): set default values for point spaces
        orient_default(list): set default values for orient spaces
        scale_default(list): set default values for scale spaces
    """
    # get kwargs
    parent = variables.kwargs('parent', None, kwargs)
    point = variables.kwargs('point', None, kwargs)
    orient = variables.kwargs('orient', None, kwargs)
    scale = variables.kwargs('scale', None, kwargs)
    parent_default = variables.kwargs('parent_default', None, kwargs)
    point_default = variables.kwargs('point_default', None, kwargs)
    orient_default = variables.kwargs('orient_default', None, kwargs)
    scale_default = variables.kwargs('scale_default', None, kwargs)

    # add each space to ctrl
    for space_add, space_default, space_type in zip([parent, point, orient, scale],
                                                    [parent_default, point_default, orient_default, scale_default],
                                                    ['parent', 'point', 'orient', 'scale']):
        if space_add:
            for space, info in space_add.iteritems():
                _add_single_space_to_ctrl(ctrl, {space: info}, default=space_default, space_type=space_type)


def get_space_info(ctrl):
    """
    get given control's space info

    Args:
        ctrl(str): control name

    Returns:
        space_info(dict)
    """
    space_info = {}
    for space_attr, space_type in zip({'parentSpaces', 'pointSpaces', 'orientSpaces', 'scaleSpaces'},
                                      {'parent', 'point', 'orient', 'scale'}):
        space_attr_str = attributes.get_attr(space_attr, node=ctrl, warn=False)
        if space_attr_str:
            # convert to dict
            space_attr_val = ast.literal_eval([space_attr_str])
            if len(space_attr_val) > 1:
                # it has blend set up, get current space as default value
                space_a = cmds.getAttr('{}.{}SpaceA'.format(ctrl, space_type))
                space_b = cmds.getAttr('{}.{}SpaceB'.format(ctrl, space_type))
                default_info = [space_a, space_b]
            else:
                default_info = []
            space_info.update({space_type: {'space': space_attr_val,
                                            'default': default_info}})
    return space_info


def export_space_info(ctrls, path, name=CTRL_SPACE_INFO_DEFAULT_NAME):
    """
    export controls space info to the given path, space info contains each spaces information, and default values

    Args:
        ctrls(list/str): controls need to be exported
        path(str): given path
    Keyword Args:
        name(str): export space info file name, default is 'spaces'
    Returns:
        space_info_path(str): exported path, return None if nothing to be exported
    """
    if isinstance(ctrls, basestring):
        ctrls = [ctrls]

    space_info_export = {}
    for c in ctrls:
        # check if it's exist
        if cmds.objExists(c):
            # get space info
            space_info = get_space_info(c)
            if space_info:
                space_info_export.update({c: space_info})
        else:
            logger.warning("{} doesn't exist in the scene, skipped".format(c))

    # check if has ctrl shape info
    if space_info_export:
        # compose path
        space_info_path = os.path.join(path, name + CTRL_SPACE_INFO_FORMAT)
        files.write_json_file(space_info_path, space_info_export)
        logger.info('export space info successfully at {}'.format(space_info_path))
        return space_info_path
    else:
        logger.warning('nothing to be exported, skipped')
        return None


def build_spaces_from_info(space_info, control_list=None, exception_list=None):
    """
    build space base on given space information

    Args:
        space info(dict): space info
    Keyword Args:
        control_list(list): only load space info to those controls in the list, None will load all, default is None
        exception_list(list): skip loading space info to those controls in the list, default is None
    """
    for ctrl, space_info in space_info.iteritems():
        if cmds.objExists(ctrl):
            if control_list and ctrl not in control_list:
                pass
            elif exception_list and ctrl in exception_list:
                pass
            else:
                ctrl_space_info = {}
                for key, item in space_info.iteritems():
                    ctrl_space_info.update({key: item['space'],
                                            key+'_default': item['default']})
                add_space(ctrl, **ctrl_space_info)
                # log info
                logger.info("build spaces for {} base on the given information".format(ctrl))
        else:
            logger.warning("{} doesn't exist, skipped".format(ctrl))


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
            ctrl_shape_info = curves.get_curve_shape_info(shape)
            cv_points = ctrl_shape_info['control_vertices']

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


def get_ctrl_shape_info(ctrl):
    """
    get ctrl shape information
    Args:
        ctrl(str): control's transform or shape node

    Returns:
        ctrl_shape_info(dict): control's shape information
    """
    # check if control it's transform
    if cmds.objectType(ctrl) == 'transform':
        # get namer
        namer = naming.check_name_convention(ctrl)
        if namer and namer.type == naming.Type.Key.ctrl:
            # change namer type to control shape
            namer.type = naming.Type.controlShape
            ctrl_shape = namer.name
        else:
            logger.warning("{} is not a control, skipped".format(ctrl))
            ctrl_shape = None
    else:
        # most likely it's a nurbs curve shape node, check if it follow the naming convention
        # in case it's a shape control (like ik/fk blend), we won't save the info in that case
        namer = naming.check_name_convention(ctrl)
        if namer and namer.type == naming.Type.Key.ctsp:
            ctrl_shape = ctrl
        else:
            logger.warning("{} doesn't have a control shape node, skipped".format(ctrl))
            ctrl_shape = None

    # get ctrl shape info
    if ctrl_shape:
        curve_info = curves.get_curve_shape_info(ctrl_shape)
        ctrl_name = curve_info['name']
        color = cmds.getAttr(ctrl_shape+'.overrideColor')

        ctrl_shape_info = {ctrl_name: {'color': color,
                                       'shape_info': curve_info}}
    else:
        ctrl_shape_info = None

    return ctrl_shape_info


def export_ctrl_shape(ctrl, path, name=CTRL_SHAPE_INFO_DEFAULT_NAME):
    """
    export control shapes information to the given path
    control shape information contain shape info and color

    Args:
        ctrl(list/str): controls need to be exported
        path(str): given path
    Keyword Args:
        name(str): export control shape info file name, default is ctrlShapes
    Returns:
        ctrl_shape_info_path(str): exported path, return None if nothing to be exported
    """
    if isinstance(ctrl, basestring):
        ctrl = [ctrl]

    ctrl_shape_info_export = {}
    for c in ctrl:
        # check if it's exist
        if cmds.objExists(c):
            # get ctrl shape info
            ctrl_shape_info = get_ctrl_shape_info(c)
            if ctrl_shape_info:
                ctrl_shape_info_export.update(ctrl_shape_info)
        else:
            logger.warning("{} doesn't exist in the scene, skipped".format(c))

    # check if has ctrl shape info
    if ctrl_shape_info_export:
        # compose path
        ctrl_shape_info_path = os.path.join(path, name + CTRL_SHAPE_INFO_FORMAT)
        files.write_json_file(ctrl_shape_info_path, ctrl_shape_info_export)
        logger.info('export control shapes info successfully at {}'.format(ctrl_shape_info_path))
        return ctrl_shape_info_path
    else:
        logger.warning('nothing to be exported, skipped')
        return None


def build_ctrl_shape_from_info(ctrl_shape_info, control_list=None, exception_list=None, size=1):
    """
    add shapes to controllers base on the given control shapes info

    Args:
        ctrl_shape_info(dict): ctrl shape info
    Keyword Args:
        control_list(list): only load ctrl shape info to those controls in the list, None will load all, default is None
        exception_list(list): skip loading ctrl shape info to those controls in the list, default is None
        size(float): scale controls shapes uniformly, default is 1
    """

    for ctrl, shape_info in ctrl_shape_info.iteritems():
        if cmds.objExists(ctrl):
            if control_list and ctrl not in control_list:
                pass
            elif exception_list and ctrl in exception_list:
                pass
            else:
                shape_info.update({'size': size})
                _add_ctrl_shape(ctrl, **shape_info)
                # log info
                logger.info("added control shape for {} base on the given control shape info".format(ctrl))
        else:
            logger.warning("{} doesn't exist, skipped".format(ctrl))


# SUB FUNCTION
def _add_single_space_to_ctrl(ctrl, space_info, space_type='parent', default=None):
    """
    add single space to the given control
    it will directly connect with offset if this is the first space,
    will create blend set up if this is the second
    and will add to the existing set up if it's already had the blend setup

    it will also create the space info attribute and add on for further query

    Args:
        ctrl(str): control's name
        space_info(dict): {space: matrix_attr}
    Keyword Args:
        space_type(str): parent/point/orient/scale,
                        if it had parent space already, will skip point and orient,
                        and if it had point/orient, will skip parent
        default(list): default value for space, default is None

    Returns:
        True/False
    """
    parent_space_attr = 'parentSpaces'
    point_space_attr = 'pointSpaces'
    orient_space_attr = 'orientSpaces'
    scale_space_attr = 'scaleSpaces'

    # check if space has any exist space
    parent_info_str = attributes.get_attr(parent_space_attr, node=ctrl, warn=False)
    point_info_str = attributes.get_attr(point_space_attr, node=ctrl, warn=False)
    orient_info_str = attributes.get_attr(orient_space_attr, node=ctrl, warn=False)
    scale_info_str = attributes.get_attr(scale_space_attr, node=ctrl, warn=False)

    # convert space info string to dict
    spaces_all_info = {}
    # we need to store input matrix attr and offset matrix node because some spaces may share the same input,
    # in this way, we can avoid to create lots of matrix node doing the same thing
    input_attr_info = {}
    # we need to store all spaces, because we may add some custom space for different type,
    # and they should share the same index to keep consistent
    spaces_indexes = {}

    if parent_info_str:
        # ctrl has parent spaces, which means it doesn't have point/orient spaces
        parent_info = ast.literal_eval(parent_info_str)
        spaces_all_info.update({'parent': parent_info})
        # loop in each space to get input attr
        for key, info in parent_info.iteritems():
            input_attr_info.update({info['attr']: info['offset']})
            spaces_indexes.update({key: info['index']})
    else:
        if point_info_str:
            # add point spaces info
            point_info = ast.literal_eval(point_info_str)
            spaces_all_info.update({'point': point_info})
            # loop in each space to get input attr
            for key, info in point_info.iteritems():
                input_attr_info.update({info['attr']: info['offset']})
                spaces_indexes.update({key: info['index']})
        if orient_info_str:
            # add orient spaces info
            orient_info = ast.literal_eval(orient_info_str)
            spaces_all_info.update({'orient': orient_info})
            # loop in each space to get input attr
            for key, info in orient_info.iteritems():
                input_attr_info.update({info['attr']: info['offset']})
                spaces_indexes.update({key: info['index']})

    if scale_info_str:
        # add scale spaces info
        scale_info = ast.literal_eval(scale_info_str)
        spaces_all_info.update({'scale': scale_info})
        # loop in each space to get input attr
        for key, info in scale_info.iteritems():
            input_attr_info.update({info['attr']: info['offset']})
            spaces_indexes.update({key: info['index']})

    # check if it has parent vs point/orient clash
    if 'parent' in spaces_all_info and (space_type == 'point' or space_type == 'orient'):
        # ctrl already had parent spaces, can't add point/orient space, skipped
        return False
    elif ('point' in spaces_all_info or 'orient' in spaces_all_info) and space_type == 'parent':
        # ctrl already had point/orient spaces, can't add parent space, skipped
        return False

    # get control object
    ctrl_obj = Control(ctrl)
    space_node = ctrl_obj.space

    # check if has existing offset matrix node, create new one if not
    matrix_attr = space_info.values()[0]
    if matrix_attr in input_attr_info:
        offset_matrix_node = input_attr_info[matrix_attr]
    else:
        # create offset matrix node
        offset_matrix_node = nodeUtils.node(type=naming.Type.multMatrix, side=ctrl_obj.side,
                                            description=ctrl_obj.description+'Space', index=ctrl_obj.index,
                                            auto_suffix=True)
        # get offset matrix value
        # get control's world matrix
        ctrl_world_matrix = cmds.getAttr(ctrl+'.worldMatrix[0]')
        # get input inverse matrix
        input_matrix = cmds.getAttr(matrix_attr)
        input_inverse_matrix = mathUtils.inverse_matrix(input_matrix)
        # get offset matrix
        offset_matrix = mathUtils.mult_matrix([ctrl_world_matrix, input_inverse_matrix])
        # set attr for offset matrix node
        cmds.setAttr(offset_matrix_node+'.matrixIn[0]', offset_matrix, type='matrix')
        # connect input
        cmds.connectAttr(matrix_attr, offset_matrix_node+'.matrixIn[1]')

    # get space index
    space_name = space_info.keys()[0]
    if space_name in spaces_indexes:
        space_index = spaces_indexes[space_name]
    else:
        # get from config
        if space_name in SPACE_CONFIG:
            space_index = SPACE_CONFIG[space_name]
        else:
            # assign a custom index
            # get the max index from previous spaces
            indexes = spaces_indexes.values()
            if indexes and max(indexes) >= CUSTOM_SPACE_INDEX:
                space_index = max(indexes) + 1
            else:
                space_index = CUSTOM_SPACE_INDEX

    # get previous space info
    space_info_pre = spaces_all_info.get(space_type, None)

    # get constraint info
    if space_type == 'parent':
        skip_attrs = attributes.Attr.scale
        attr_save = parent_space_attr
        translate = True
        rotate = True
        scale = False
        attr_query = '.translateX'
    elif space_type == 'point':
        skip_attrs = attributes.Attr.rotateScale
        attr_save = point_space_attr
        translate = True
        rotate = False
        scale = False
        attr_query = '.translateX'
    elif space_type == 'orient':
        skip_attrs = attributes.Attr.translate + attributes.Attr.scale
        attr_save = orient_space_attr
        translate = False
        rotate = True
        scale = False
        attr_query = '.rotateX'
    else:
        skip_attrs = attributes.Attr.translate + attributes.Attr.rotate
        attr_save = scale_space_attr
        translate = False
        rotate = False
        scale = True
        attr_query = '.scaleX'

    # check if has previous space info
    if not space_info_pre:
        # this is the first space, directly connect to space node
        # generate space info
        space_info_save = {space_name: {'attr': matrix_attr,
                                        'offset': offset_matrix_node,
                                        'index': space_index}}

        # create mult matrix node to plug parent inverse matrix
        parent_inverse_matrix_attr = nodeUtils.mult_matrix([offset_matrix_node+'.matrixSum',
                                                            space_node+'.parentInverseMatrix[0]'], side=ctrl_obj.side,
                                                           description='{}{}OffsetSpaceA'.format(ctrl_obj.description,
                                                                                                 space_type.title()),
                                                           index=ctrl_obj.index)

        decompose_matrix = nodeUtils.node(type=naming.Type.decomposeMatrix, side=ctrl_obj.side,
                                          description='{}{}SpaceA'.format(ctrl_obj.description, space_type.title()),
                                          index=ctrl_obj.index)

        cmds.connectAttr(parent_inverse_matrix_attr, decompose_matrix+'.inputMatrix')

        # get all attributes
        attrs = attributes.Attr.transform[:]
        for skip in skip_attrs:
            attrs.remove(skip)

        for attr in attrs:
            cmds.connectAttr('{}.output{}{}'.format(decompose_matrix, attr[0].upper(), attr[1:]),
                             '{}.{}'.format(space_node, attr))

        # save space info to ctrl node
        # we can't lock the attribute, because we may want to add more spaces in animation scene,
        # the rig will be referenced into the scene, and we can't unlock attr in that case, so keep it unlock
        attributes.add_attrs(ctrl, attr_save, attribute_type='string', default_value=str(space_info_save), lock=False)
        return True

    elif len(space_info_pre.keys()) == 1:
        # this is the second space, need to create the blend space set up
        # check if it's the same space as the first one, switch the input in that case
        if space_name in space_info_pre:
            # check if input attr is the same, skip if the same
            if matrix_attr == space_info_pre[space_name]['attr']:
                return False
            else:
                # get offset matrix node, because we plug space node's parent inverse matrix node for another offset
                decompose_node = cmds.listConnections(space_node + attr_query, source=True, destination=False,
                                                      plugs=False, skipConversionNodes=True)[0]
                offset_node = cmds.listConnections(decompose_node + '.inputMatrix', source=True, destination=False,
                                                   plugs=False, skipConversionNodes=True)[0]

                # override input
                # the previous offset matrix node may be useless after this, but generally we don't care,
                # because we will save out the space data and it won't be created when we rebuild the rig
                # and we can also clean it up by using maya delete unused nodes function after all
                # it will give us less trouble than trying to delete the node on this stage
                cmds.connectAttr(offset_matrix_node+'.matrixSum', offset_node+'.inputMatrix', force=True)

                # generate space info
                space_info_save = {space_name: {'attr': matrix_attr,
                                                'offset': offset_matrix_node,
                                                'index': space_index}}
                # override space info to ctrl node
                attributes.set_attrs(attr_save, str(space_info_save), node=ctrl, type='string')
                return True
        else:
            # it's the second space, create the blend space set up
            choice_a = nodeUtils.node(type=naming.Type.choice, side=ctrl_obj.side,
                                      description='{}{}SpaceA'.format(ctrl_obj.description, space_type.title()),
                                      index=ctrl_obj.index)
            choice_b = nodeUtils.node(type=naming.Type.choice, side=ctrl_obj.side,
                                      description='{}{}SpaceB'.format(ctrl_obj.description, space_type.title()),
                                      index=ctrl_obj.index)
            # connect input matrix attr to choice node
            index_pre = space_info_pre.values()[0]['index']
            offset_pre = space_info_pre.values()[0]['offset']

            attributes.connect_attrs([offset_pre+'.matrixSum', offset_pre+'.matrixSum',
                                      offset_matrix_node+'.matrixSum', offset_matrix_node+'.matrixSum'],
                                     ['{}.input[{}]'.format(choice_a, index_pre),
                                      '{}.input[{}]'.format(choice_b, index_pre),
                                      '{}.input[{}]'.format(choice_a, space_index),
                                      '{}.input[{}]'.format(choice_b, space_index)], force=True)

            # get decompose matrix node A
            decompose_node = cmds.listConnections(space_node + attr_query, source=True, destination=False,
                                                  plugs=False, skipConversionNodes=True)[0]

            # remove decompose node a
            cmds.delete(decompose_node)

            # add attributes
            # get enum name
            space_pre = space_info_pre.keys()[0]
            enum_name = '{}={}:{}={}'.format(space_pre, index_pre, space_name, space_index)
            # get save info
            space_info_save = {space_name: {'attr': matrix_attr,
                                            'offset': offset_matrix_node,
                                            'index': space_index},
                               space_pre: space_info_pre[space_pre]}
            # get default
            default_val = []
            if default:
                for space in default:
                    if space in [space_pre, space_name]:
                        default_index = space_info_save[space]['index']
                        default_val.append(default_index)

            if not default_val:
                default_val = [index_pre, space_index]

            attributes.separator(ctrl, space_type+'Space')
            attributes.add_attrs(ctrl, [space_type+'SpaceA', space_type+'SpaceB'], attribute_type='enum',
                                 enum_name=enum_name, default_value=[default_val[0], default_val[-1]], keyable=True,
                                 channel_box=True)
            cmds.addAttr(ctrl, longName=space_type+'SpaceBlend', attributeType='float', min=0, max=1, keyable=True)
            # reverse blend attr
            rvs_blend_attr = nodeUtils.equation('~{}.{}SpaceBlend'.format(ctrl, space_type), side=ctrl_obj.side,
                                                description='{}{}SpaceBlend'.format(ctrl_obj.description,
                                                                                    space_type.title()), index=ctrl_obj)

            # connect attr
            attributes.connect_attrs(['{}.{}SpaceA'.format(ctrl, space_type), '{}.{}SpaceB'.format(ctrl, space_type)],
                                     [choice_a+'.selector', choice_b+'.selector'], force=True)

            # constraint blend setup
            constraints.matrix_blend_constraint([choice_a + '.output', choice_b + '.output'], space_node,
                                                translate=translate, rotate=rotate, scale=scale,
                                                weights=[rvs_blend_attr, '{}.{}SpaceBlend'.format(ctrl, space_type)],
                                                addition_constraint_description=space_type.title() + 'SpaceBlend',
                                                addition_decompose_description='Blend')

            # override space info to ctrl node
            attributes.set_attrs(attr_save, str(space_info_save), node=ctrl, type='string')
            return True
    else:
        # ctrl already had blend set up, add more
        # get choice nodes
        choice_a = naming.Namer(type=naming.Type.choice, side=ctrl_obj.side,
                                description='{}{}SpaceA'.format(ctrl_obj.description, space_type.title()),
                                index=ctrl_obj.index).name
        choice_b = naming.Namer(type=naming.Type.choice, side=ctrl_obj.side,
                                description='{}{}SpaceB'.format(ctrl_obj.description, space_type.title()),
                                index=ctrl_obj.index).name
        # check if it's the same space as the first one, switch the input in that case
        if space_name in space_info_pre and matrix_attr == space_info_pre[space_name]['attr']:
            # input attr and space is the same with the existing one, skip if the same
            return False
        else:
            # either new space or override the existing one
            attributes.connect_attrs([offset_matrix_node+'.matrixSum', offset_matrix_node+'.matrixSum'],
                                     ['{}.input[{}]'.format(choice_a, space_index),
                                      '{}.input[{}]'.format(choice_b, space_index)], force=True)
            # check if space already exist or not, if not, add to enum
            if space_name not in space_info_pre:
                # get enum name
                enum_name = cmds.attributeQuery(space_type+'SpaceA', node=ctrl, listEnum=True)[0]
                enum_name += ':{}={}'.format(space_name, space_index)
                cmds.addAttr('{}.{}SpaceA'.format(ctrl, space_type), edit=True, enumName=enum_name)
                cmds.addAttr('{}.{}SpaceB'.format(ctrl, space_type), edit=True, enumName=enum_name)

            # update save info
            space_info_pre.update({space_name: {'attr': matrix_attr,
                                                'offset': offset_matrix_node,
                                                'index': space_index}})

            # check if need to change default value
            if default:
                for default_val, space in zip([default[0], default[-1]], ['A', 'B']):
                    if default_val in space_info_pre:
                        index = space_info_pre[default_val]['index']
                        # set default value and also the current value
                        cmds.addAttr('{}.{}Space{}'.format(ctrl, space_type, space), edit=True, defaultValue=index)
                        cmds.setAttr('{}.{}Space{}'.format(ctrl, space_type, space), index)

            # override space info to ctrl node
            attributes.set_attrs(attr_save, str(space_info_pre), node=ctrl, type='string')
            return True


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
        shape_info(dict): if has custom shape node (like copy/paste), or load from file
    """
    shape = kwargs.get('shape', 'cube')
    size = kwargs.get('size', 1)
    color = kwargs.get('color', None)
    transform = kwargs.get('transform', None)
    shape_info = kwargs.get('shape_info', None)

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
    crv_transform, crv_shape = curves.create_curve('TEMP_CRV', shape_info['control_vertices'], shape_info['knots'],
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
