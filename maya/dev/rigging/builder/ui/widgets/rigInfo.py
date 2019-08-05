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

# CONSTANT

TT_PROJECT = 'Set Project'
TT_ASSET = 'Set Asset'
TT_RIG = 'Set Rig Type'


# CLASS
class RigInfo(QWidget):
    """
    class for rig info widget

    users use this widget to get rig info for building
    """
    def __init__(self):
        super(RigInfo, self).__init__()
        self._enable = True

        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        for section, tip in zip(['project', 'asset', 'rig'],
                                [TT_PROJECT, TT_ASSET, TT_RIG]):
            # QLineEdit
            line_edit_section = LineEdit(name=section, tool_tip=tip)
            # add obj to class for further use
            setattr(self, 'lineEdit_'+section, line_edit_section)

            # add section to base layout
            layout_base.addWidget(line_edit_section)

        # so it won't focus on QLineEdit when startup
        self.setFocus()

    def enable_widget(self):
        self._enable = not self._enable
        self.setEnabled(self._enable)


class LineEdit(QLineEdit):
    """lineEdit for each rig info section"""
    def __init__(self, name='', tool_tip=''):
        super(LineEdit, self).__init__()

        self._name = name
        self._tool_tip = tool_tip

        self.setFrame(False)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('border-radius: 4px')
        self.setPlaceholderText(self._name.title())
        if self._tool_tip:
            self.setToolTip(self._tool_tip)
