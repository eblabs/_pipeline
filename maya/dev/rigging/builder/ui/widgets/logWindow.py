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

# import utils
import utils.common.logUtils as logUtils


# CLASS
class LogWindow(QWidget):
    def __init__(self):
        super(LogWindow, self).__init__()
        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        layout_level = QHBoxLayout()
        layout_base.addLayout(layout_level)
        self.level_label = LevelLabel()
        layout_level.addWidget(self.level_label)

        layout_level.setAlignment(self.level_label, Qt.AlignRight)

        self.log_info_widget = LogInfo()
        layout_base.addWidget(self.log_info_widget)

        self.level_label.menu.SIGNAL_LEVEL.connect(self.log_info_widget.set_level)


class LevelLabel(QLabel):
    """
    widget to show the current log level
    """
    def __init__(self):
        super(LevelLabel, self).__init__()
        self.setText('info')
        self.setMaximumWidth(50)
        self.setStyleSheet("""border: 1px solid grey; border-radius: 1px""")
        self.setToolTip('log level')

        self.menu = LogLevelMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.menu.SIGNAL_LEVEL.connect(self.set_level)

    def show_menu(self, pos):
        self.menu.move(self.mapToGlobal(pos))  # move menu to the clicked position
        self.menu.show()

    def set_level(self, level):
        self.setText(level)
        self.menu.close()


class LogLevelMenu(QMenu):
    """
    log level right click menu, contains several radio buttons to set log level to display
    """
    SIGNAL_LEVEL = Signal(str)

    def __init__(self):
        super(LogLevelMenu, self).__init__()
        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        self.critical = QRadioButton('critical')
        self.error = QRadioButton('error')
        self.warning = QRadioButton('warning')
        self.info = QRadioButton('info')
        self.debug = QRadioButton('debug')

        self.info.setChecked(True)

        layout_base.addWidget(self.critical)
        layout_base.addWidget(self.error)
        layout_base.addWidget(self.warning)
        layout_base.addWidget(self.info)
        layout_base.addWidget(self.debug)

        # signal
        self.critical.toggled.connect(lambda: self.get_level(self.critical))
        self.error.toggled.connect(lambda: self.get_level(self.error))
        self.warning.toggled.connect(lambda: self.get_level(self.warning))
        self.info.toggled.connect(lambda: self.get_level(self.info))
        self.debug.toggled.connect(lambda: self.get_level(self.debug))

    def get_level(self, button):
        level = button.text()
        if button.isChecked():
            self.SIGNAL_LEVEL.emit(level)


class LogInfo(QTextEdit):
    """
    log info widget, this widget is for printing any log info from rig build
    """

    def __init__(self):
        super(LogInfo, self).__init__()
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.level = logUtils.LOG_LEVEL_INDEX['info']

    def keyPressEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        pass

    def add_log_info(self, message, level):
        level_index = logUtils.LOG_LEVEL_INDEX[level]
        if level_index >= self.level:
            color = self.get_level_color(level)
            self.setTextColor(color)
            self.append(message)

    def refresh(self):
        self.clear()

    def show_status_info(self, message, level):
        level_index = logUtils.LOG_LEVEL_INDEX[level]
        if level_index >= self.level and message:
            self.clear()
            color = self.get_level_color(level)
            self.setTextColor(color)
            self.append(message)

    def set_level(self, level):
        self.level = logUtils.LOG_LEVEL_INDEX[level]

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
