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

        self.project_check = False
        self.asset_check = False
        self.rig_check = False

        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        for section, tip in zip(['project', 'asset', 'rig'],
                                [TT_PROJECT, TT_ASSET, TT_RIG]):
            # QLineEdit
            line_edit_section = LineEdit(name=section, tool_tip=tip)
            # add obj to class for further use
            setattr(self, 'line_edit_'+section, line_edit_section)

            # add section to base layout
            layout_base.addWidget(line_edit_section)

        # rig right clicked menu
        self.menu = QMenu()
        self.create_action = self.menu.addAction('Create')
        self.remove_action = self.menu.addAction('Remove')
        self.line_edit_rig.setContextMenuPolicy(Qt.CustomContextMenu)

        # get all projects
        projects_list = assets.get_all_projects()
        self.line_edit_project.completer.setModel(QStringListModel(projects_list))

        # connect signal
        self.line_edit_project.textChanged.connect(self.assets_completer)
        self.line_edit_project.textChanged.connect(self.check_project)

        self.line_edit_asset.textChanged.connect(self.rigs_completer)
        self.line_edit_asset.textChanged.connect(self.check_asset)

        self.line_edit_rig.textChanged.connect(self.check_rig)
        self.line_edit_rig.customContextMenuRequested.connect(self.show_menu)

        self.create_action.triggered.connect(self.create_rig)
        self.remove_action.triggered.connect(self.remove_rig)

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
        self.project_check = assets.get_project_path(project, warning=False)
        self.set_text_color(self.line_edit_project, self.project_check)

    def check_asset(self):
        asset = self.line_edit_asset.text()
        project = self.line_edit_project.text()
        self.asset_check = assets.get_asset_path_from_project(asset, project, warning=False)
        self.set_text_color(self.line_edit_asset, self.asset_check)

    def check_rig(self):
        rig = self.line_edit_rig.text()
        asset = self.line_edit_asset.text()
        project = self.line_edit_project.text()
        self.rig_check = assets.get_rig_path_from_asset(rig, asset, project, warning=False)
        self.set_text_color(self.line_edit_rig, self.rig_check)

    def create_rig(self):
        rig = self.line_edit_rig.text()
        asset = self.line_edit_asset.text()
        project = self.line_edit_project.text()

        title = "Create Rig"
        text = "This will create rig {} under {} - {}, are you sure you want to create it?".format(rig, asset, project)
        reply = QMessageBox.warning(self, title, text, QMessageBox.Ok | QMessageBox.Cancel,
                                    defaultButton=QMessageBox.Cancel)

        if reply == QMessageBox.Ok:
            # create rig
            assets.create_rig(rig, asset, project)
            self.check_rig()

    def remove_rig(self):
        rig = self.line_edit_rig.text()
        asset = self.line_edit_asset.text()
        project = self.line_edit_project.text()

        title = "Remove Rig"
        text = "This will remove rig {} under {} - {}, are you sure you want to remove it?".format(rig, asset, project)
        reply = QMessageBox.warning(self, title, text, QMessageBox.Ok | QMessageBox.Cancel,
                                    defaultButton=QMessageBox.Cancel)

        if reply == QMessageBox.Ok:
            # create rig
            assets.remove_rig(rig, asset, project)
            self.check_rig()

    def show_menu(self, pos):
        # check if typed rig available
        if self.rig_check:
            # disable create, enable remove
            self.create_action.setEnabled(False)
            self.remove_action.setEnabled(True)
        else:
            # check if text in rig
            rig = self.line_edit_rig.text()
            if rig:
                # enable remove disable create
                self.create_action.setEnabled(True)
            else:
                self.create_action.setEnabled(False)
            self.remove_action.setEnabled(False)

        pos = self.line_edit_rig.mapToGlobal(pos)
        self.menu.move(pos)  # move menu to the clicked position
        self.menu.show()

    @staticmethod
    def set_text_color(line_edit, check):
        """
        set line edit text color, white if available, else is red

        Args:
            line_edit(QLineEdit): rig info widget
            check(bool): True/False
        """
        palette = QPalette()
        if check:
            palette.setColor(QPalette.Text, Qt.white)
        else:
            palette.setColor(QPalette.Text, Qt.red)
        line_edit.setPalette(palette)


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

        self.completer = QCompleter()
        self.setCompleter(self.completer)
