# IMPORT PACKAGES

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

    func = variables.kwargs('function', '', kwargs, short_name='func')

    modules = path.split('.')  # split into parts to get the last section

    if not func:
        # get function name is not given, use the module name with first letter in cap
        func = modules[-1][0].upper() + modules[-1][1:]

    try:
        module = __import__(path, fromlist=[modules[-1]])
    except ImportError:
        # no module in path
        module = None

    return module, func
