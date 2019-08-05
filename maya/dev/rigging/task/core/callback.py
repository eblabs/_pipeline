# IMPORT PACKAGES

# import OrderedDict
from collections import OrderedDict

# import PySide widgets
try:
    from PySide2.QtWidgets import *
except ImportError:
    from PySide.QtGui import *

# import utils
import utils.common.logUtils as logUtils

# CONSTANT
import dev.rigging.task.config.PROPERTY_ITEMS as PROPERTY_ITEMS
PROPERTY_ITEMS = PROPERTY_ITEMS.PROPERTY_ITEMS

logger = logUtils.get_logger(name='callback', level='info')

# kwargs_ui for further use
kwargs_ui = OrderedDict()
for section in ['pre_build', 'build', 'post_build']:
    kwargs_item = PROPERTY_ITEMS['callback'].copy()
    kwargs_item.update({'select': False,
                        'hint': 'Execute following code at '+section})
    kwargs_ui.update({section: kwargs_item})


# FUNCTION
def Callback(self, code):
    """
    callback function
    (keep the function first letter in Cap so all modules can be called like
     moduleName.moduleName[0].title() + moduleName[1:])

    used for tasks need callback

    it will show as QTreeWidgetItem(task) in the ui,
    but it's the only task not inherit from task class, just a function

    Args:
        self: this function will attached to the builder class,
              so we need self to get vars from builder
        code(str): the callback code we need to execute
    """
    if code:
        exec code
