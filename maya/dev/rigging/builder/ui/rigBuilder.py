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
import utils.common.uiUtils as uiUtils
import utils.common.logUtils as logUtils

# import widgets
import widgets.taskTree as taskTree
import widgets.propertyEditor2 as propertyEditor
import widgets.buttonShelf as buttonShelf
import widgets.rigInfo as rigInfo
import widgets.rigProgress as rigProgress
import widgets.taskInfo as taskInfo
import widgets.logWindow as logWindow

# Constant
logger = logUtils.logger


# CLASS
class RigBuilder(uiUtils.BaseWindow):
    """class for RigBuilder UI"""
    def __init__(self, **kwargs):
        kwargs.update({'title': 'Rig Builder'})
        super(RigBuilder, self).__init__(**kwargs)

        # rig builder layout

        # base layout
        layout_base = QGridLayout(self)
        self.setLayout(layout_base)

        # splitter
        splitter_base = QSplitter()
        layout_base.addWidget(splitter_base)
        # splitter right for log
        splitter_right = QSplitter()

        # left layout
        frame_left = QFrame()
        frame_left.setMinimumSize(320, 700)
        layout_left = QVBoxLayout(frame_left)

        # rig layout
        frame_right = QFrame()
        # frame_right.setMinimumSize(550, 550)
        layout_right = QVBoxLayout(frame_right)

        # log layout
        frame_log = QFrame()
        frame_log.setMinimumSize(550, 150)
        layout_log = QVBoxLayout(frame_log)

        # attach frame
        splitter_base.addWidget(frame_left)
        splitter_base.addWidget(splitter_right)

        # attach right side widgets
        splitter_right.addWidget(frame_right)
        splitter_right.addWidget(frame_log)

        # splitter setting
        splitter_base.setCollapsible(0, False)
        splitter_base.setCollapsible(1, False)
        splitter_base.setStretchFactor(0, 1)
        splitter_base.setStretchFactor(1, 2)
        splitter_right.setOrientation(Qt.Vertical)
        splitter_right.setCollapsible(0, False)
        splitter_right.setCollapsible(1, False)
        splitter_right.setStretchFactor(0, 3)
        splitter_right.setStretchFactor(1, 1)

        # widgets
        self.rig_info = rigInfo.RigInfo()
        self.button_shelf = buttonShelf.ButtonShelf()
        self.task_tree = taskTree.TaskTree()
        self.rig_progress = rigProgress.RigProgress()
        self.task_info = taskInfo.TaskInfo()
        self.property_editor = propertyEditor.PropertyEditor()
        self.log_window = logWindow.LogWindow()

        # attach widget
        self.attach_rig_widget(self.rig_info, 'Rig Info', layout_left)
        self.attach_rig_widget(self.button_shelf, '', layout_left, no_space=True)
        self.attach_rig_widget(self.task_tree, 'Build Info', layout_left)
        self.attach_rig_widget(self.rig_progress, '', layout_left)

        self.attach_rig_widget(self.task_info, 'Task Info', layout_right)
        self.attach_rig_widget(self.property_editor, 'Property Editor', layout_right)
        self.attach_rig_widget(self.log_window, 'Log', layout_log)

        # connect signal
        self.connect_signals()

        # so it won't focus on QLineEdit when startup
        self.setFocus()

    def keyPressEvent(self, event):
        pass

    @ staticmethod
    def attach_rig_widget(widget, title, layout, no_space=False):
        """
        attach widget to the given layout with a group box

        Args:
            widget(QWidget): widget need to be attached
            title(str): group box title
            layout(QLayout): layout where the widget should be attached to

        Keyword Args:
            no_space(bool): if remove the space in the layout, default is False
        """
        group_box = QGroupBox(title)
        group_box.setStyleSheet("""QGroupBox {
                                                border: 1px solid gray;
                                                border-radius: 2px;
                                                margin-top: 0.5em;
                                            }

                                            QGroupBox::title {
                                                subcontrol-origin: margin;
                                                left: 10px;
                                                padding: 0 3px 0 3px;
                                            }""")

        layout_widget = QGridLayout(group_box)

        if no_space:
            layout_widget.setContentsMargins(0, 0, 0, 0)  # remove spaces

        layout_widget.addWidget(widget)  # add widget to group box
        layout.addWidget(group_box)  # attach group box to layout

    def connect_signals(self):
        # hook up buttons
        self.button_shelf.SIGNAL_RELOAD.connect(self.task_tree.check_save)
        self.button_shelf.SIGNAL_RELOAD.connect(self.property_editor.refresh)
        self.button_shelf.SIGNAL_RELOAD.connect(self.task_info.refresh)

        self.button_shelf.SIGNAL_EXECUTE.connect(self.task_tree.run_sel_tasks)
        self.button_shelf.SIGNAL_EXECUTE_ALL.connect(self.task_tree.run_all_tasks)

        # get builder
        self.task_tree.SIGNAL_GET_BUILDER.connect(self.rig_info.get_builder)

        # rig info, plug builder path to tree widget
        self.rig_info.SIGNAL_BUILDER.connect(self.task_tree.reload_builder)

        # save
        self.button_shelf.button_save.clicked.connect(self.task_tree.export_current_builder)

        # progress bar
        # init progress bar settings
        self.task_tree.SIGNAL_PROGRESS_INIT.connect(self.rig_progress.init_setting)
        # update progress
        self.task_tree.SIGNAL_PROGRESS.connect(self.rig_progress.update_progress)
        # stop progress
        self.task_tree.SIGNAL_ERROR.connect(self.rig_progress.stop_progress)

        # task info
        self.task_tree.itemPressed.connect(self.task_info.set_label)

        # task info edit attr name
        self.task_info.task_name_window.SIGNAL_ATTR_NAME.connect(self.task_tree.set_attr_name)

        # task info edit task type
        self.task_info.SIGNAL_TASK_TYPE.connect(self.task_tree.task_switch_window_open)

        # reset attr name once updated
        self.task_tree.SIGNAL_ATTR_NAME.connect(self.task_info.set_label)

        # property editor
        self.task_tree.itemPressed.connect(self.property_editor.init_property)

        # clear when not select anything
        self.task_tree.SIGNAL_CLEAR.connect(self.property_editor.refresh)
        self.task_tree.SIGNAL_CLEAR.connect(self.task_info.refresh)

        # log
        logger.connector.SIGNAL_EMIT.connect(self.log_window.log_info_widget.add_log_info)
        self.button_shelf.SIGNAL_RELOAD.connect(self.log_window.log_info_widget.refresh)
        self.task_tree.SIGNAL_LOG_INFO.connect(self.log_window.log_info_widget.show_status_info)
