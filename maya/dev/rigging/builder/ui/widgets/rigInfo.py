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
import utils.common.assets as assets

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

        for section, tip, menu in zip(['project', 'asset', 'rig'],
                                [TT_PROJECT, TT_ASSET, TT_RIG],
                                [False, False, True]):
            # QLineEdit
            line_edit_section = LineEdit(name=section, tool_tip=tip, menu=menu)
            # add obj to class for further use
            setattr(self, 'line_edit_'+section, line_edit_section)

            # add section to base layout
            layout_base.addWidget(line_edit_section)

        # get all projects
        projects_list = assets.get_all_projects()
        self.line_edit_project.completer.setModel(QStringListModel(projects_list))

        # connect signal
        self.line_edit_project.textChanged.connect(self.assets_completer)
        self.line_edit_project.textChanged.connect(self.check_project)
        self.line_edit_asset.textChanged.connect(self.rigs_completer)
        self.line_edit_rig.customContextMenuRequested.connect(self.show_menu)

        # so it won't focus on QLineEdit when startup
        self.setFocus()

    def enable_widget(self):
        self._enable = not self._enable
        self.setEnabled(self._enable)

    def assets_completer(self):
        # remove any input
        self.line_edit_asset.clear()
        self.line_edit_rig.clear()
        # get project
        project = self.line_edit_project.text()
        if project:
            assets_list = assets.get_all_assets_from_project(project)
            # set completer
            self.line_edit_asset.completer.setModel(QStringListModel(assets_list))

    def rigs_completer(self):
        # remove any input
        self.line_edit_rig.clear()
        # get project and asset
        asset = self.line_edit_asset.text()
        if asset:
            # get project
            project = self.line_edit_project.text()
            rigs_list = assets.get_all_rig_from_asset(asset, project)
            # set completer
            self.line_edit_rig.completer.setModel(QStringListModel(rigs_list))

    def check_project(self):
        project = self.line_edit_project.text()
        check = assets.get_project_path(project, warning=False)
        palette = QPalette()
        if check:
            palette.setColor(QPalette.Text, Qt.white)
            self.line_edit_project.setPalette(palette)
        else:
            palette.setColor(QPalette.Text, Qt.red)
            self.line_edit_project.setPalette(palette)

    def show_menu(self, pos):
        pos = self.line_edit_rig.mapToGlobal(pos)
        self.line_edit_rig.menu.move(pos)  # move menu to the clicked position
        self.line_edit_rig.menu.show()


class LineEdit(QLineEdit):
    """lineEdit for each rig info section"""
    def __init__(self, name='', tool_tip='', menu=False):
        super(LineEdit, self).__init__()

        self._name = name
        self._tool_tip = tool_tip

        self.setFrame(False)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('border-radius: 4px')
        self.setPlaceholderText(self._name.title())
        if self._tool_tip:
            self.setToolTip(self._tool_tip)

        self.completer = QCompleter()
        self.setCompleter(self.completer)

        if menu:
            self.menu = QMenu()
            self.create_action = self.menu.addAction('Create')
            self.remove_action = self.menu.addAction('Remove')
            self.setContextMenuPolicy(Qt.CustomContextMenu)
