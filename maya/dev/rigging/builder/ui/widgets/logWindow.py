# IMPORT PACKAGES

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


# CLASS
class LogWindow(QTextEdit):
    """
    log window widget, this window is for printing any log info from rig build
    """

    def __init__(self):
        super(LogWindow, self).__init__()
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.NoFocus)

    def keyPressEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        pass

    def add_log_info(self, message, level):
        color = self.get_level_color(level)
        self.setTextColor(color)
        self.append(message)

    def refresh(self):
        self.clear()

    def show_status_info(self, message, level):
        self.clear()
        color = self.get_level_color(level)
        self.setTextColor(color)
        self.append(message)

    @ staticmethod
    def get_level_color(level):
        """
        get level color
        critical/error: red
        warning: dark yellow
        info: white
        debug: dark green

        Args:
            level(str): log level

        Returns:
            color(QColor)
        """

        if level == 'info':
            color_code = QColor(255, 255, 255)
        elif level == 'warning':
            color_code = QColor(217, 166, 0)
        elif level in ['critical', 'error']:
            color_code = QColor(255, 0, 0)
        else:
            color_code = QColor(28, 150, 0)
        return color_code
