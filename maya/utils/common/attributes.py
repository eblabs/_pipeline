# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import variables
import logUtils

# CONSTANT
ATTR_CONFIG = {'all': ['translateX', 'translateY', 'translateZ',
                       'rotateX', 'rotateY', 'rotateZ',
                       'scaleX', 'scaleY', 'scaleZ', 'visibility'],
               'transform': ['translateX', 'translateY', 'translateZ',
                             'rotateX', 'rotateY', 'rotateZ',
                             'scaleX', 'scaleY', 'scaleZ'],
               'translate': ['translateX', 'translateY', 'translateZ'],
               'rotate': ['rotateX', 'rotateY', 'rotateZ'],
               'scale': ['scaleX', 'scaleY', 'scaleZ'],
               'vis': ['visibility'],
               'scaleVis': ['scaleX', 'scaleY', 'scaleZ', 'visibility'],
               'rotateOrder': ['rotateOrder']}

# logger
logger = logUtils.logger


#  CLASS
class Attr(object):
    """Attr class to access common attribute vars"""
    def __init__(self):
        pass


for key, item in ATTR_CONFIG.iteritems():
    # Add attributes to current module
    setattr(Attr, key, item)


#  FUNCTION
def connect_attrs(driver_attrs, driven_attrs, **kwargs):
    """
    Connect driver attrs to driven attrs

    Args:
        driver_attrs(str/list): source attrs
        driven_attrs(str/list): target attrs

    Keyword Args:
        driver(str): override the node in driver_attrs
        driven(str): override the node in driven_attrs
        force(bool): override the connection/lock status, default is True
    """
    # get vars
    driver = variables.kwargs('driver', None, kwargs)
    driven = variables.kwargs('driven', None, kwargs)
    force = variables.kwargs('force', True, kwargs, short_name='f')

    # check if driver_attrs/driven_attrs is string/list
    if isinstance(driver_attrs, basestring):
        driver_attrs = [driver_attrs]
    if isinstance(driven_attrs, basestring):
        driven_attrs = [driven_attrs]

    # connect each attr
    for attrs in zip(driver_attrs, driven_attrs):
        _connect_single_attr(attrs[0], attrs[1],
                             driver=driver, driven=driven,
                             force=force)

    if len(driver_attrs) == 1:
        if check_attr_exists(driver_attrs[0], node=driver):
            # connect driver attr to the rest driven attrs
            for attr in driven_attrs[1:]:
                _connect_single_attr(driver_attrs[0], attr,
                                     driver=driver, driven=driven,
                                     force=force)
        else:
            pass


def lock_hide_attrs(node, attrs):
    """
    lock and hide attrs

    Args:
        node(str/list): the node to lock hide attrs
        attrs(str/list): lock and hide given attrs
    """
    if isinstance(node, basestring):
        node = [node]
    if isinstance(attrs, basestring):
        attrs = [attrs]

    for n in node:
        for attr in attrs:
            if cmds.attributeQuery(attr, node=n, ex=True):
                cmds.setAttr('{}.{}'.format(n, attr), keyable=False,
                             lock=True, channelBox=False)
            else:
                logger.warn('{} does not have attribute: {}'.format(n, attr))


def unlock_attrs(node, attrs, **kwargs):
    """
    unlock attrs

    Args:
        node(str/list): the node to unlock attrs
        attrs(str/list): unlock and show given attrs

    Keyword Args:
        keyable(bool): set attr keyable, default is True
        channel_box(bool): show attr in channel box (none keyable if False), default is True
    """
    # get vars
    keyable = variables.kwargs('keyable', True, kwargs, short_name='k')
    channel_box = variables.kwargs('channel_box', True, kwargs, short_name='cb')

    if isinstance(node, basestring):
        node = [node]
    if isinstance(attrs, basestring):
        attrs = [attrs]

    for n in node:
        for attr in attrs:
            if cmds.attributeQuery(attr, node=n, ex=True):
                cmds.setAttr('{}.{}'.format(n, attr), lock=False)
                cmds.setAttr('{}.{}'.format(n, attr), channelBox=channel_box)
                if not channel_box:
                    keyable = False
                cmds.setAttr('{}.{}'.format(n, attr), keyable=keyable)
            else:
                logger.warn('{} does not have attribute: {}'.format(n, attr))


def add_attrs(node, attrs, **kwargs):
    """
    add attrs

    Args:
        node(str/list): nodes to assign attrs
        attrs(str/list): add attrs

    Keyword Args:
        attribute_type(str): 'bool', 'long', 'enum', 'float', 'double',
                             'string', 'matrix', 'message', default is 'float'
        range(list):min/max value
        default_value(float/int/list/str): default value
        keyable(bool): set attr keyable, default is True
        channel_box(bool): show attr in channel box, default is True
        enum_name(str): enum attr name
        multi(m): add attr as a multi-attribute, default is False
        lock(bool): lock attr, default is False
    """
    # get vars
    attr_type = variables.kwargs('attribute_type', 'float', kwargs, short_name='at')
    attr_range = variables.kwargs('range', [], kwargs)
    default_val = variables.kwargs('default_value', None, kwargs, short_name='dv')
    keyable = variables.kwargs('keyable', True, kwargs, short_name='k')
    channel_box = variables.kwargs('channel_box', True, kwargs, short_name='cb')
    enum_name = variables.kwargs('enum_name', '', kwargs, short_name='enum')
    multi = variables.kwargs('multi', False, kwargs, short_name='m')
    lock = variables.kwargs('lock', False, kwargs)

    if isinstance(node, basestring):
        node = [node]
    if isinstance(attrs, basestring):
        attrs = [attrs]

    # get default value
    if not isinstance(default_val, list):
        default_val = [default_val]*len(attrs)
    elif not isinstance(default_val[0], list) and attr_type == 'matrix':
        default_val = [default_val]*len(attrs)

    if not channel_box or lock:
        keyable = False
    if attr_type != 'string':
        attr_type_key = 'attributeType'
    else:
        attr_type_key = 'dataType'

    for n in node:
        for attr, val in zip(attrs, default_val):
            attr_dict = {attr_type_key: attr_type,
                         'keyable': keyable,
                         'multi': multi}

            # check if attr exists
            if not cmds.attributeQuery(attr, node=n, ex=True):
                attr_dict.update({'longName': attr})
                if val is not None and not isinstance(val, basestring) and not isinstance(val, list):
                    attr_dict.update({'defaultValue': val})
                if attr_range:
                    if attr_range[0] is not None:
                        attr_dict.update({'minValue': attr_range[0]})
                    if attr_range[1] is not None:
                        attr_dict.update({'maxValue': attr_range[1]})

                if enum_name:
                    attr_dict.update({'enumName': enum_name})

                # add attr
                cmds.addAttr(n, **attr_dict)
                # skip message
                if attr_type != 'message':
                    # set default value for string/matrix
                    if attr_type in ['string', 'matrix'] and val:
                        cmds.setAttr('{}.{}'.format(n, attr), val, type=attr_type)
                    else:
                        pass
                    # lock
                    cmds.setAttr('{}.{}'.format(n, attr), lock=lock)
                    # channelBox
                    if attr_type not in ['string', 'matrix'] and channel_box:
                        cmds.setAttr('{}.{}'.format(n, attr), channelBox=channel_box)
                    else:
                        pass
            else:
                logger.warning('{} already has attribute: {}'.format(n, attr))


def set_attrs(attrs, value, **kwargs):
    """

    Args:
        attrs(str/list): attrs need to be set, can be attribute name or full name like 'node.attr'
        value: attrs values

    Keyword Args:
        node(str): node name to override the attrs
        type(str): if need to be specific, normally for string/matrix
        force(bool): force set value if locked, default is True
    """

    _node = variables.kwargs('node', '', kwargs, short_name='n')
    _type = variables.kwargs('type', '', kwargs, short_name='t')
    _force = variables.kwargs('force', True, kwargs, short_name='f')

    if isinstance(attrs, basestring):
        attrs = [attrs]
    attrs_num = len(attrs)  # get how many attributes need to be set

    if not isinstance(value, list):
        # if it's a single value, multiply the attrs_num to feed in each attr
        value = [value] * attrs_num
    elif _type == 'matrix' and not isinstance(value[0], list):
        # input value is a matrix list
        value = [value] * attrs_num

    for attr, val in zip(attrs, value):
        attr_compose = check_attr_exists(attr, node=_node)  # get attr full name
        if attr_compose:
            # check if connected
            connections = cmds.listConnections(attr_compose, source=True,
                                               destination=False, plugs=True,
                                               skipConversionNodes=True)
            if not connections:
                # set attr if no input connection
                set_attr_kwargs = {}
                if _type in ['matrix', 'string']:
                    set_attr_kwargs.update({'type': _type})  # specific type maya set attr needed

                # check if locked
                lock = cmds.getAttr(attr_compose, lock=True)

                if not lock or _force:
                    # unlock attr, set attr
                    cmds.setAttr(attr_compose, lock=False)
                    cmds.setAttr(attr_compose, val, **set_attr_kwargs)

                    if lock:
                        # lock attr back
                        cmds.setAttr(attr_compose, lock=True)
                else:
                    logger.warning('{} is locked, skipped'.format(attr_compose))
            else:
                logger.warning('{} has input connection: {}, skipped'.format(attr_compose, connections[0]))
        else:
            logger.warning('{} does not exist, skipped'.format(attr_compose))


def attr_in_channel_box(node, attr):
    """
    check if given attr is in channel box

    Args:
        node(str): given maya node
        attr(str): attribute

    Returns:
        check(bool): True/False
    """

    attr = '{}.{}'.format(node, attr)
    keyable = cmds.getAttr(attr, keyable=True)
    channel_box = cmds.getAttr(attr, cb=True)
    check = keyable or channel_box
    return check


def check_attr_exists(attr, node=None):
    """
    check if attr exists

    Args:
        attr(str): given attribute, can be full name like 'node.attr' or only attribute name

    Keyword Args:
        node(str): given node, default is None

    Returns:
        attr(str): attribute full name, return None if doesn't exist
    """
    attr_split = attr.split('.')
    if not node:
        # get node name from attr
        node = attr_split[0]
    if len(attr_split) > 1:
        attr = attr.replace(attr_split[0]+'.', '')  # override node if given

    try:
        cmds.listConnections('{}.{}'.format(node, attr))
        # I found this is the better way to check if attr exist or not
        # attributeQuery doesn't support compound attribute, like worldMatrix[0]
        # listConnections will error out if the attr does not exist
        return '{}.{}'.format(node, attr)
    except ValueError:
        logger.warning('{} does not have attr {}'.format(node, attr))
        return None


# SUB FUNCTION
def _connect_single_attr(driver_attr, driven_attr, driver=None, driven=None, force=True):
    """
    Args:
        driver_attr(str): source attr
        driven_attr(str): target attr

    Keyword Args:
        driver(str): override the node in driver_attr
        driven(str): override the node in driven_attr
        force(bool): override the connection/lock status, default is True
    """

    attr_connect = []
    attr_check = True
    for attr, node in zip([driver_attr, driven_attr],
                          [driver, driven]):
        attr_check = check_attr_exists(attr, node=node)
        if not attr_check:
            break
        else:
            attr_connect.append(attr_check)
    if not attr_check:
        # at least one attribute doesn't exist
        return

    # check if driven attr has connection
    input_plug = cmds.listConnections(attr_connect[1], source=True,
                                      destination=False, plugs=True,
                                      skipConversionNodes=True)
    # check if driven attr is locked
    lock = cmds.getAttr(attr_connect[1], lock=True)

    # connect attr
    if not input_plug and not lock:
        # just connect attr
        cmds.connectAttr(attr_connect[0], attr_connect[1])
    else:
        if force:
            if input_plug == attr_connect[0]:
                # sometimes it gives me an error when using the same input to force connect the attr
                pass
            else:
                cmds.setAttr(attr_connect[1], lock=False)  # unlock the attr anyway
                cmds.connectAttr(attr_connect[0], attr_connect[1], force=True)  # force connection
                if lock:
                    cmds.setAttr(attr_connect[1], lock=True)  # lock back
        else:
            if input_plug == attr_connect[0]:
                logger.warning('{} is already connected with {}, skipped'.format(attr_connect[1], input_plug[0]))
            elif input_plug:
                logger.warning('{} already has connection from {}, skipped'.format(attr_connect[1], input_plug[0]))
            elif lock:
                logger.warning('{} is locked, skipped'.format(attr_connect[1]))
            else:
                pass
