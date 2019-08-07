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

#  CONSTANT
import icons

# shortcuts
SC_RELOAD = 'Ctrl+R'
SC_EXECUTE_ALL = 'Ctrl+Shift+Space'
SC_EXECUTE_PAUSE = 'Ctrl+Space'
SC_STOP = 'ESC'
SC_RELOAD_EXECUTE = 'Ctrl+Shift+R'


# CLASS
class ButtonShelf(QWidget):
    """
    button shelf widget
    """
    SIGNAL_RELOAD = Signal()
    SIGNAL_EXECUTE = Signal(list)
    SIGNAL_PAUSE = Signal()
    SIGNAL_STOP = Signal()
    SIGNAL_EXECUTE_ALL = Signal(list)

    def __init__(self):
        super(ButtonShelf, self).__init__()

        self._pause = False
        self._running = False

        layout_base = QHBoxLayout()
        self.setLayout(layout_base)
        layout_base.setSpacing(2)
        layout_base.setContentsMargins(2, 2, 2, 2)  # remove space between button and layout

        self.button_reload = Button(layout_base, [icons.reload, icons.reload_disabled], shortcut=SC_RELOAD,
                                    tool_tip='Reload Rig Builder[{}]'.format(SC_RELOAD))

        self.button_execute_all = Button(layout_base, [icons.execute_all, icons.execute_all_disabled],
                                         shortcut=SC_EXECUTE_ALL,
                                         tool_tip='Execute All Tasks[{}]'.format(SC_EXECUTE_ALL), sub_menu=True)

        self.button_execute_sel = Button(layout_base, [icons.execute_select, icons.execute_select_disabled],
                                         shortcut=SC_EXECUTE_PAUSE,
                                         tool_tip='Execute Selection[{}]'.format(SC_EXECUTE_PAUSE), sub_menu=True)

        self.button_reload_execute = Button(layout_base, [icons.reload_execute, icons.reload_execute_disabled],
                                            shortcut=SC_RELOAD_EXECUTE,
                                            tool_tip='Reload and Execute All[{}]'.format(SC_RELOAD_EXECUTE),
                                            sub_menu=True)

        self.button_pause_resume = Button(layout_base, [icons.pause, icons.pause_disabled], shortcut=SC_EXECUTE_PAUSE,
                                          tool_tip='Execute Selection[{}]'.format(SC_EXECUTE_PAUSE))

        self.button_stop = Button(layout_base, [icons.stop, icons.stop_disabled], shortcut=SC_STOP,
                                  tool_tip='Stop Execution[{}]'.format(SC_STOP))

        # set stop disabled
        self.button_pause_resume.setEnabled(False)
        self.button_stop.setEnabled(False)

        # connect signal
        self.button_reload.clicked.connect(self.reload_pressed)

        self.button_execute_all.clicked.connect(self.execute_all_pressed)
        self.button_execute_all.sub_menu.SIGNAL_SECTION.connect(self.execute_all_pressed)

        self.button_execute_sel.clicked.connect(self.execute_sel_pressed)
        self.button_execute_sel.sub_menu.SIGNAL_SECTION.connect(self.execute_sel_pressed)

        self.button_reload_execute.clicked.connect(self.reload_execute_pressed)
        self.button_reload_execute.sub_menu.SIGNAL_SECTION.connect(self.reload_execute_pressed)

        self.button_pause_resume.clicked.connect(self.pause_resume_pressed)

        self.button_stop.clicked.connect(self.stop_pressed)

        layout_base.addStretch()  # add stretch so the buttons aliened from left

    def reload_pressed(self):
        """
        reload button pressed event
        """
        self._pause = False

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

    def pause_resume_pressed(self):
        """
        pause resume button pressed event
        """
        self._pause = not self._pause
        self._set_button(reload_val=False, execute_all_val=False, execute_sel_val=False, pause_resume_val=True,
                         stop_val=True, reload_execute_val=False)
        self._pause_resume_set(pause_resume_val=self._pause)
        self.SIGNAL_PAUSE.emit()

    def stop_pressed(self):
        """
        stop button pressed event
        """
        self._pause = False
        self._set_button()
        self._pause_resume_set(pause_resume_val=False)
        self.SIGNAL_STOP.emit()

    def reset_all(self):
        """
        reset all buttons
        """
        self._pause = False
        self._set_button()

    def execute_button_set(self):
        """
        set buttons when execute tasks, will be connected with signal from other widget
        """
        self._set_button(reload_val=False, execute_all_val=False, execute_sel_val=False, pause_resume_val=True,
                         stop_val=True, reload_execute_val=False)
        self._pause_resume_set(pause_resume_val=False)

    def _set_button(self, reload_val=True, execute_all_val=True, execute_sel_val=True, pause_resume_val=False,
                    stop_val=False, reload_execute_val=True):
        """
        set buttons enabled/disabled

        Keyword Args:
            reload_val(bool): reload button's enabled/disabled value, default is True
            execute_all_val(bool): execute all button's enabled/disabled value, default is True
            execute_sel_val(bool): execute selected button's enabled/disabled value, default is True
            pause_resume_val(bool): pause resume button's enabled/disabled value, default is False
            stop_val(bool): stop button's enabled/disabled value, default is False
            reload_execute_val(bool): reload and execute button's enabled/disabled value, default is True
        """
        # set reload button
        self.button_reload.setEnabled(reload_val)

        # set execute all button
        self.button_execute_all.setEnabled(execute_all_val)

        # set execute select button
        self.button_execute_sel.setEnabled(execute_sel_val)

        # set reload execute button
        self.button_reload_execute.setEnabled(reload_execute_val)

        # set pause resume button
        self.button_pause_resume.setEnabled(pause_resume_val)

        # set stop button
        self.button_stop.setEnabled(stop_val)

    def _pause_resume_set(self, pause_resume_val=False):
        """
        set pause resume button's icon

        Keyword Args:
            pause_resume_val(bool): True is resume icon, False is pause icon, default is False
        """
        if pause_resume_val:
            self.button_pause_resume.setIcon(QIcon(icons.resume))
        else:
            self.button_pause_resume.setIcon(QIcon(icons.pause))


class Button(QPushButton):
    """
    sub class for QPushButton, contains information and functions needed for buttons shelf
    """

    def __init__(self, layout, icons_button, shortcut='', tool_tip='', sub_menu=False):
        super(Button, self).__init__()
        size = 25  # button size

        self._icons = icons_button
        self._shortcut = shortcut
        self._tool_tip = tool_tip
        self._sub_menu = sub_menu

        self.setIcon(QIcon(self._icons[0]))  # set enabled icon by default
        self.setIconSize(QSize(size, size))  # set icon size

        # resize button so no gap for the icon
        self.setFixedHeight(size)
        self.setFixedWidth(size)

        # shortcut
        if self._shortcut:
            self.setShortcut(self._shortcut)

        # tool tip
        if self._tool_tip:
            self.setToolTip('{} [{}]'.format(self._tool_tip, self._shortcut))

        # sub menu
        if self._sub_menu:
            self.sub_menu = SubMenu()
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self._show_menu)

        layout.addWidget(self)

    def setEnabled(self, arg):
        super(Button, self).setEnabled(arg)
        if arg:
            # push button enabled
            self.setIcon(QIcon(self._icons[0]))
        else:
            # push button disabled
            self.setIcon(QIcon(self._icons[1]))

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
