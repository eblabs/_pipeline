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

# import widget
import taskCreator

# import utils
import utils.common.naming as naming
import utils.common.logUtils as logUtils

# CONSTANT
logger = logUtils.logger

TT_TASK_NAME = 'Task Name used in the build script as attribute'
TT_TASK_TYPE = 'Task function path'

ROLE_TASK_INFO = Qt.UserRole + 1


# CLASS
class TaskInfo(QWidget):
    """
    class for task info widget

    use this widget to show task's important information
    task name
    task type
    """
    SIGNAL_TASK_TYPE = Signal()

    def __init__(self):
        super(TaskInfo, self).__init__()

        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        for section, tip in zip(['name', 'type'], [TT_TASK_NAME, TT_TASK_TYPE]):
            # task label
            label_section = TaskLabel(tool_tip=tip)

            # add obj to class for further use
            setattr(self, 'label_'+section, label_section)

            # add section to base layout
            layout_base.addWidget(label_section)

        self.label_name.action_edit.triggered.connect(self.edit_name_widget)
        self.label_type.action_edit.triggered.connect(self.edit_task_widget)

        self.task_name_window = TaskAttrName(self)

    def keyPressEvent(self, event):
        pass

    def set_label(self, item):
        task_info = item.data(0, ROLE_TASK_INFO)
        task_name = task_info['attr_name']
        task_path = task_info['task_path']
        self.label_name.setText(task_name)
        self.label_type.setText(task_path)

    def refresh(self):
        self.setEnabled(True)
        self.label_name.setText('')
        self.label_type.setText('')

    def edit_name_widget(self):
        """
        change task's attr name in the builder
        """
        title = "Change task's object name in the builder"
        text = ("This will break all functions call this task object in the builder, \nare you sure you want"
                "to change it?")
        reply = QMessageBox.warning(self, title, text, QMessageBox.Ok | QMessageBox.Cancel,
                                    defaultButton=QMessageBox.Cancel)

        if reply == QMessageBox.Ok:
            # get current task name
            current_name = self.label_name.text()
            namer = naming.Namer(current_name)
            side = namer.side
            description = namer.description

            # set attr for window
            self.task_name_window.task_name_widget.side = side
            self.task_name_window.task_name_widget.description = description

            # show window
            # try to close first in case it's opened
            self.task_name_window.close()
            self.task_name_window.move(QCursor.pos())
            self.task_name_window.show()

    def edit_task_widget(self):
        """
        change task's type
        """
        title = "Change task's type"
        text = ("This will change the task's behavior, some kwargs may not switch as expected,\n"
                "are you sure you want to change it?")
        reply = QMessageBox.warning(self, title, text, QMessageBox.Ok | QMessageBox.Cancel,
                                    defaultButton=QMessageBox.Cancel)

        if reply == QMessageBox.Ok:
            # shoot the signal to switch the task type
            self.SIGNAL_TASK_TYPE.emit()


class TaskAttrName(QDialog):
    """
    widget to set task attr name
    """
    SIGNAL_ATTR_NAME = Signal(str)

    def __init__(self, parent=None):
        super(TaskAttrName, self).__init__(parent)

        self.setWindowTitle('Set Task Name')
        self.setGeometry(100, 100, 250, 100)

        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        self.task_name_widget = taskCreator.TaskName(display=False)
        layout_base.addWidget(self.task_name_widget)

        # create button
        self.button = QPushButton('Set Name')
        self.button.setFixedWidth(80)
        self.button.setEnabled(False)
        layout_base.addWidget(self.button)

        layout_base.setAlignment(self.button, Qt.AlignRight)

        self.task_name_widget.task_des.textChanged.connect(self.set_button_with_name_check)
        self.button.clicked.connect(self.set_name)

    def set_button_with_name_check(self):
        des = self.task_name_widget.task_des.text()
        if des:
            self.button.setEnabled(True)
        else:
            self.button.setEnabled(False)

    def set_name(self):
        side = self.task_name_widget.side
        des = self.task_name_widget.description
        task_name = naming.Namer(type=naming.Type.task, side=side, description=des).name
        self.SIGNAL_ATTR_NAME.emit(task_name)
        self.close()


class TaskLabel(QLabel):
    """
    label to show task info for each section
    """
    def __init__(self, tool_tip=''):
        super(TaskLabel, self).__init__()

        self._tool_tip = tool_tip

        # set stylesheet
        self.setStyleSheet("""border: 1.3px solid black; border-radius: 2px""")
        if self._tool_tip:
            self.setToolTip(self._tool_tip)

        # right click menu
        self.menu = QMenu()
        self.action_edit = self.menu.addAction('Edit')

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

    def _show_menu(self, pos):
        if self.text():
            self.menu.move(self.mapToGlobal(pos))  # move menu to the clicked position

            self.menu.show()
