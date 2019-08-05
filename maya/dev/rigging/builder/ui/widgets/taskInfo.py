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
TT_TASK_NAME = 'Task Name used in the build script as attribute'
TT_TASK_TYPE = 'Task function path'

ROLE_TASK_NAME = Qt.UserRole + 1
ROLE_TASK_FUNC_NAME = Qt.UserRole + 2


# CLASS
class TaskInfo(QWidget):
    """
    class for task info widget

    use this widget to show task's important information
    task name
    task type
    """
    SIGNAL_ATTR_NAME = Signal(str)

    def __init__(self):
        super(TaskInfo, self).__init__()
        self._enable = True

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

    def set_label(self, item):
        name = item.data(0, ROLE_TASK_NAME)
        func_name = item.data(0, ROLE_TASK_FUNC_NAME)
        self.label_name.setText(name)
        self.label_type.setText(func_name)

    def refresh(self):
        self.setEnabled(True)
        self.label_name.setText('')
        self.label_type.setText('')

    def enable_widget(self):
        self._enable = not self._enable
        self.setEnabled(self._enable)

    def edit_name_widget(self):
        title = "Change task's attribute name in the builder"
        text = "This will break all functions call this attribute in the builder, \nare you sure you want to change it?"
        reply = QMessageBox.warning(self, title, text, QMessageBox.Ok | QMessageBox.Cancel,
                                    defaultButton=QMessageBox.Cancel)

        if reply == QMessageBox.Ok:
            # change the attr name
            current_name = self.label_name.text()
            text, ok = QInputDialog.getText(self, 'Attribute Name', 'Set Attribute Name', text=current_name)
            if text and ok and text != current_name:
                self.SIGNAL_ATTR_NAME.emit(text)


class TaskLabel(QLabel):
    """
    label to show task info for each section

    """
    def __init__(self, tool_tip=''):
        super(TaskLabel, self).__init__()

        self._tool_tip = tool_tip
        self.menu = None

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
            pos_parent = self.mapToGlobal(QPoint(0, 0))
            self.menu.move(pos_parent + pos)  # move menu to the clicked position

            self.menu.show()
