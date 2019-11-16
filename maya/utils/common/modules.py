# IMPORT PACKAGES

# import imp
import imp

# import utils
import variables


#  FUNCTION
def import_module(path, **kwargs):
    """
    import module from given path

    Args:
        path(str): import module path, path should be sth like 'dev.rigging.function'

    Keyword Args:
        function(str): function name, if None will use the file name
                       like dev.rigging.task.Task()

    Returns:
        module, function
    """

    path = str(path)  # __import__ module doesn't support unicode

    func = variables.kwargs('function', '', kwargs, short_name='func')

    modules = path.split('.')  # split into parts to get the last section

    if not func:
        # get function name is not given, use the module name with first letter in cap
        func = modules[-1][0].upper() + modules[-1][1:]

    # try:
    #     module = __import__(path, fromlist=[modules[-1]])
    # except ImportError:
    #     # no module in path
    #     module = None
    module = __import__(path, fromlist=[modules[-1]])

    return module, func


def get_obj_attr(obj, attr):
    """
    get given object attribute's value

    Args:
        obj(object): object contains the attribute
        attr(str): object attr full path

    Examples:
        normally used in class,
        obj = self
        attr = 'builder.component.name'
        component_name = get_obj_attr(obj, attr)

    Returns:
        obj_attr
    """
    attr_split = attr.split('.')
    attr_parent = obj

    for attr_part in attr_split:
        # check if attr_part contain []
        attr_part_split = attr_part.split('[')
        if len(attr_part_split) > 1:
            # means contain [], the attr is a list or dict
            # extract the info in []
            attr_index_str = attr_part_split[1][:-1]
            # check if it's int
            try:
                attr_index = int(attr_index_str)
            except ValueError:
                attr_index = attr_index_str
            attr_part = attr_part_split[0]
        else:
            attr_index = None

        if hasattr(attr_parent, attr_part):
            attr_parent = getattr(attr_parent, attr_part)
            # get list value or dict value
            if attr_index is not None:
                if ((isinstance(attr_parent, list) or isinstance(attr_parent, basestring)) and
                        isinstance(attr_index, int)):
                    try:
                        attr_parent = attr_parent[attr_index]
                    except IndexError:
                        attr_parent = None
                elif isinstance(attr_parent, dict) and isinstance(attr_index, basestring):
                    if attr_index in attr_parent:
                        attr_parent = attr_parent[attr_index]
                    else:
                        attr_parent = None
                else:
                    attr_parent = None
            if not attr_parent:
                break
        else:
            attr_parent = None
            break

    return attr_parent
