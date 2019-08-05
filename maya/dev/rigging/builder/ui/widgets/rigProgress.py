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
class RigProgress(QProgressBar):
    """ProgressBar widget"""
    def __init__(self):
        super(RigProgress, self).__init__()
        self._pause = False

        self.setTextVisible(True)

        # set palette
        self._palette = QPalette()
        self._palette.setColor(QPalette.Highlight, QColor(0, 161, 62))
        self._palette.setColor(QPalette.Text, QColor(Qt.white))
        self._palette.setColor(QPalette.HighlightedText, QColor(Qt.black))
        self.setPalette(self._palette)

    def init_setting(self, max_num):
        """
        initialize settings

        Args:
            max_num(int): maximum number for the loop
        """
        self._pause = False
        # set range
        self.setRange(0, max_num)
        # zero progress bar
        self.setValue(0)
        # set color to green
        self._palette.setColor(QPalette.Highlight, QColor(0, 161, 62))
        self.setPalette(self._palette)

    def update_progress(self, value):
        self.setValue(value)

    def pause_progress(self):
        self._pause = not self._pause
        if self._pause:
            # pause
            # set color to blue
            self._palette.setColor(QPalette.Highlight, QColor(77, 193, 232))
            self.setPalette(self._palette)
        else:
            # run
            # set color to green
            self._palette.setColor(QPalette.Highlight, QColor(0, 161, 62))
            self.setPalette(self._palette)

    def stop_progress(self):
        self._pause = False
        # set color to red
        self._palette.setColor(QPalette.Highlight, QColor(250, 40, 71))
        self.setPalette(self._palette)
