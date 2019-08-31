# IMPORT PACKAGES

# import os
import os

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

# utils
import utils.common.files as files

# icons
import icons

# shortcuts
import config
KEY_CONFIG = os.path.join(os.path.dirname(config.__file__), 'KEY_SHORTCUT.cfg')
KEY_SHORTCUT = files.read_json_file(KEY_CONFIG)


# CLASS
class ButtonShelf(QWidget):
    """
    button shelf widget
    """
    SIGNAL_RELOAD = Signal()
    SIGNAL_EXECUTE = Signal(list)
    SIGNAL_EXECUTE_ALL = Signal(list)

    def __init__(self):
        super(ButtonShelf, self).__init__()

        layout_base = QHBoxLayout()
        self.setLayout(layout_base)
        layout_base.setSpacing(2)
        layout_base.setContentsMargins(2, 2, 2, 2)  # remove space between button and layout

        self.button_reload = Button(layout_base, icons.reload, shortcut=KEY_SHORTCUT['reload'],
                                    tool_tip='Reload Rig Builder')

        self.button_execute_all = Button(layout_base, icons.execute_all, shortcut=KEY_SHORTCUT['execute_all'],
                                         tool_tip='Execute All Tasks', sub_menu=True)

        self.button_execute_sel = Button(layout_base, icons.execute_select, shortcut=KEY_SHORTCUT['execute'],
                                         tool_tip='Execute Selection', sub_menu=True)

        self.button_reload_execute = Button(layout_base, icons.reload_execute, shortcut=KEY_SHORTCUT['reload_execute'],
                                            tool_tip='Reload and Execute All', sub_menu=True)

        self.button_save = Button(layout_base, icons.save, shortcut=KEY_SHORTCUT['save'], tool_tip='Save Rig Builder')

        # connect signal
        self.button_reload.clicked.connect(self.reload_pressed)

        self.button_execute_all.clicked.connect(self.execute_all_pressed)
        self.button_execute_all.sub_menu.SIGNAL_SECTION.connect(self.execute_all_pressed)

        self.button_execute_sel.clicked.connect(self.execute_sel_pressed)
        self.button_execute_sel.sub_menu.SIGNAL_SECTION.connect(self.execute_sel_pressed)

        self.button_reload_execute.clicked.connect(self.reload_execute_pressed)
        self.button_reload_execute.sub_menu.SIGNAL_SECTION.connect(self.reload_execute_pressed)

        layout_base.addStretch()  # add stretch so the buttons aliened from left

    def reload_pressed(self):
        """
        reload button pressed event
        """
        self.SIGNAL_RELOAD.emit()

    def execute_all_pressed(self, section=None):
        """
        execute all button pressed event

        Args:
            section(list): include 'pre_build', 'build' and 'post_build'
        """
        if section is None:
            section = ['pre_build', 'build', 'post_build']

        self.SIGNAL_EXECUTE_ALL.emit(section)

    def execute_sel_pressed(self, section=None):
        """
        execute selected button pressed event

        Args:
            section(list): include 'pre_build', 'build' and 'post_build'
        """
        if section is None:
            section = ['pre_build', 'build', 'post_build']

        self.SIGNAL_EXECUTE.emit(section)

    def reload_execute_pressed(self, section=None):
        """
        reload and execute button pressed event

        Args:
            section(list): include 'pre_build', 'build' and 'post_build'
        """
        if section is None:
            section = ['pre_build', 'build', 'post_build']
        self.SIGNAL_RELOAD.emit()
        self.SIGNAL_EXECUTE_ALL.emit(section)


class Button(QPushButton):
    """
    sub class for QPushButton, contains information and functions needed for buttons shelf
    """

    def __init__(self, layout, icon_button, shortcut='', tool_tip='', sub_menu=False):
        super(Button, self).__init__()
        size = 25  # button size

        self._icon = icon_button
        self._shortcut = shortcut
        self._tool_tip = tool_tip
        self._sub_menu = sub_menu

        self.setIcon(QIcon(self._icon))  # set enabled icon by default
        self.setIconSize(QSize(size, size))  # set icon size

        # resize button so no gap for the icon
        self.setFixedHeight(size)
        self.setFixedWidth(size)

        # shortcut
        if self._shortcut:
            self.setShortcut(shortcut)

        # tool tip
        if self._tool_tip:
            self.setToolTip('{} [{}]'.format(self._tool_tip, self._shortcut))

        # sub menu
        if self._sub_menu:
            self.sub_menu = SubMenu()
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self._show_menu)

        layout.addWidget(self)

    def _show_menu(self, pos):
        """
        show right click menu at clicked position
        """
        pos_parent = self.mapToGlobal(QPoint(0, 0))
        self.sub_menu.move(pos_parent + pos)

        self.sub_menu.show()


class SubMenu(QMenu):
    """
    sub menu for buttons, include pre-build-post
    emit custom signal for further use
    """
    SIGNAL_SECTION = Signal(list)

    def __init__(self):
        super(SubMenu, self).__init__()

        self.pre = self.addAction('Pre-Build')
        self.build = self.addAction('Build')
        self.post = self.addAction('Post-Build')

        self.pre.triggered.connect(self._pre_triggered)
        self.build.triggered.connect(self._build_triggered)
        self.post.triggered.connect(self._post_triggered)

    def _pre_triggered(self):
        self.SIGNAL_SECTION.emit(['pre_build'])

    def _build_triggered(self):
        self.SIGNAL_SECTION.emit(['build'])

    def _post_triggered(self):
        self.SIGNAL_SECTION.emit(['post_build'])
