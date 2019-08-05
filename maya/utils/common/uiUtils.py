# IMPORT PACKAGES

# import OpenMayaUI
# maya doesn't have MQtUtil in api 2.0
import maya.OpenMayaUI as OpenMayaUI

# import PySide
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2 import __version__
    from shiboken2 import wrapInstance
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import __version__
    from shiboken import wrapInstance


#  CLASS
class BaseWindow(QWidget):
    """class for Base Window in maya"""
    def __init__(self, **kwargs):
        super(BaseWindow, self).__init__()

        # get kwargs
        self._parent = kwargs.get('parent', None)
        self._title = kwargs.get('title', 'Window')
        self._geo = kwargs.get('geometry', [100, 100, 100, 100])

        # parent widget
        self.setParent(self._parent)
        self.setWindowFlags(Qt.Window)

        # set the object name
        self.setObjectName(self._title.replace(' ', '') + '_uniqueId')
        self.setWindowTitle(self._title)
        self.setGeometry(self._geo[0], self._geo[1], self._geo[2], self._geo[3])


# FUNCTION
def get_maya_window():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QMainWindow)
