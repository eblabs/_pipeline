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
import utils.rigging.buildUtils as buildUtils

# CONSTANT
TT_PROJECT = 'Set Project'
TT_ASSET = 'Set Asset'
TT_RIG = 'Set Rig Type'


# CLASS
class RigInfoBase(QWidget):
    """
    base class for rig info widget

    has three input line to set project, asset and rig type, each input has its own completer,
    will turn red if not exist
    """
    def __init__(self, label=''):
        super(RigInfoBase, self).__init__()

        self.project_checker = False
        self.asset_checker = False
        self.rig_checker = False

        self.layout_base = QVBoxLayout()
        self.setLayout(self.layout_base)

        if label:
            label = QLabel(label)
            self.layout_base.addWidget(label)

        for section, tip in zip(['project', 'asset', 'rig'],
                                [TT_PROJECT, TT_ASSET, TT_RIG]):
            # QLineEdit
            line_edit_section = LineEdit(name=section, tool_tip=tip)
            # add obj to class for further use
            setattr(self, 'line_edit_'+section, line_edit_section)

            # add section to base layout
            self.layout_base.addWidget(line_edit_section)

        # get all projects
        projects_list = assets.get_all_projects()
        self.line_edit_project.completer.setModel(QStringListModel(projects_list))

        # connect signal
        self.line_edit_project.textChanged.connect(self.assets_completer)
        self.line_edit_project.textChanged.connect(self.check_project)

        self.line_edit_asset.textChanged.connect(self.rigs_completer)
        self.line_edit_asset.textChanged.connect(self.check_asset)

        self.line_edit_rig.textChanged.connect(self.check_rig)

        # so it won't focus on QLineEdit when startup
        self.setFocus()

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
        self.project_checker = assets.get_project_path(project, warning=False)
        self.set_text_color(self.line_edit_project, self.project_checker)

    def check_asset(self):
        asset = self.line_edit_asset.text()
        project = self.line_edit_project.text()
        self.asset_checker = assets.get_asset_path_from_project(asset, project, warning=False)
        self.set_text_color(self.line_edit_asset, self.asset_checker)

    def check_rig(self):
        rig = self.line_edit_rig.text()
        asset = self.line_edit_asset.text()
        project = self.line_edit_project.text()
        self.rig_checker = assets.get_rig_path_from_asset(rig, asset, project, warning=False)
        self.set_text_color(self.line_edit_rig, self.rig_checker)

    @staticmethod
    def set_text_color(line_edit, checker):
        """
        set line edit text color, white if available, else is red

        Args:
            line_edit(QLineEdit): rig info widget
            checker(bool): True/False
        """
        palette = QPalette()
        if checker:
            palette.setColor(QPalette.Text, Qt.white)
        else:
            palette.setColor(QPalette.Text, Qt.red)
        line_edit.setPalette(palette)


class RigInfo(RigInfoBase):
    """
    class for rig info widget

    users use this widget to get rig info for building
    """
    SIGNAL_BUILDER = Signal(str)

    def __init__(self):
        super(RigInfo, self).__init__()
        self._enable = True
        self._pos = None

        # rig right clicked menu
        self.menu = QMenu()
        self.create_action = self.menu.addAction('Create')
        self.remove_action = self.menu.addAction('Remove')
        self.build_action = self.menu.addAction('Build Script')
        self.line_edit_rig.setContextMenuPolicy(Qt.CustomContextMenu)

        # builder generator
        self.builder_generator = BuilderGenerator()

        # connect signal
        self.line_edit_rig.customContextMenuRequested.connect(self.show_menu)

        self.create_action.triggered.connect(self.create_rig)
        self.remove_action.triggered.connect(self.remove_rig)
        self.build_action.triggered.connect(self.generate_builder)

        # so it won't focus on QLineEdit when startup
        self.setFocus()

    def keyPressEvent(self, event):
        pass

    def enable_widget(self):
        self._enable = not self._enable
        self.setEnabled(self._enable)

    def create_rig(self):
        rig = self.line_edit_rig.text()
        asset = self.line_edit_asset.text()
        project = self.line_edit_project.text()

        title = "Create Rig"
        text = "This will create rig {} under {} - {}, are you sure you want to create it?".format(rig, project, asset)
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
        text = "This will remove rig {} under {} - {}, are you sure you want to remove it?".format(rig, project, asset)
        reply = QMessageBox.warning(self, title, text, QMessageBox.Ok | QMessageBox.Cancel,
                                    defaultButton=QMessageBox.Cancel)

        if reply == QMessageBox.Ok:
            # create rig
            assets.remove_rig(rig, asset, project)
            self.check_rig()

    def show_menu(self, pos):
        # check if typed rig available
        if self.rig_checker:
            # disable create, enable remove
            self.create_action.setEnabled(False)
            self.remove_action.setEnabled(True)
            self.build_action.setEnabled(True)
        else:
            # check if text in rig
            rig = self.line_edit_rig.text()
            if rig:
                # enable remove disable create
                self.create_action.setEnabled(True)
            else:
                self.create_action.setEnabled(False)
            self.remove_action.setEnabled(False)
            self.build_action.setEnabled(False)

        self._pos = self.line_edit_rig.mapToGlobal(pos)
        self.menu.move(self._pos)  # move menu to the clicked position
        self.menu.show()

    def generate_builder(self):
        """
        create build script from given rig
        """
        rig = self.line_edit_rig.text()
        asset = self.line_edit_asset.text()
        project = self.line_edit_project.text()

        self.builder_generator.project = project
        self.builder_generator.asset = asset
        self.builder_generator.rig_type = rig

        # set default inheritance path here, it won't do the check in init for some reason
        self.builder_generator.line_edit_project.setText('template')
        self.builder_generator.line_edit_asset.setText('baseNode')
        self.builder_generator.line_edit_rig.setText('animationRig')

        self.builder_generator.move(self._pos)
        self.builder_generator.show()

    def get_builder(self):
        if self.rig_checker:
            rig = self.line_edit_rig.text()
            asset = self.line_edit_asset.text()
            project = self.line_edit_project.text()

            # get builder
            builder_path = buildUtils.get_builder(rig, asset, project, warning=False)

            if not builder_path:
                title = "Builder doesn't exist"
                text = "the rig builder doesn't exist for {} - {} - {}, " \
                       "do you want to create it?".format(self.project, self.asset, self.rig_type)
                reply = QMessageBox.warning(self, title, text, QMessageBox.Ok | QMessageBox.Cancel,
                                            defaultButton=QMessageBox.Cancel)
                if reply == QMessageBox.Ok:
                    self.generate_builder()
            else:
                self.SIGNAL_BUILDER.emit(builder_path)


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


class BuilderGenerator(RigInfoBase):
    """
    widget to generate build script
    """

    def __init__(self):
        super(BuilderGenerator, self).__init__(label='Generate the builder inherited from the given rig builder')
        self.project = None
        self.asset = None
        self.rig_type = None

        self.project_inherit = None
        self.asset_inherit = None
        self.rig_type_inherit = None
        self.builder_inherit_path = None

        self.setWindowTitle('Generate Builder')
        self.setGeometry(100, 100, 250, 100)

        # push button
        self.create_button = QPushButton('Create')
        self.create_button.setFixedWidth(80)
        self.layout_base.addWidget(self.create_button)
        self.layout_base.setAlignment(self.create_button, Qt.AlignRight)

        # connect signal
        self.line_edit_rig.textChanged.connect(self.create_button_enable)
        self.create_button.clicked.connect(self.generate_builder)

    def create_button_enable(self):
        if self.rig_checker:
            self.project_inherit = self.line_edit_project.text()
            self.asset_inherit = self.line_edit_asset.text()
            self.rig_type_inherit = self.line_edit_rig.text()
            self.builder_inherit_path = buildUtils.get_builder(self.rig_type_inherit, self.asset_inherit,
                                                               self.project_inherit, warning=False)
            if self.builder_inherit_path:
                # inherit builder exists
                self.create_button.setEnabled(True)
            else:
                self.create_button.setEnabled(False)
        else:
            self.create_button.setEnabled(False)

    def generate_builder(self):
        # check if have builder exist
        builder_checker = buildUtils.get_builder(self.rig_type, self.asset, self.project, warning=False)

        if builder_checker:
            title = "Overwrite Builder"
            text = "This will overwrite the existing rig builder for {} - {} - {}, " \
                   "are you sure you want to do it?".format(self.project, self.asset, self.rig_type)
            reply = QMessageBox.warning(self, title, text, QMessageBox.Ok | QMessageBox.Cancel,
                                        defaultButton=QMessageBox.Cancel)
            if reply != QMessageBox.Ok:
                return

        buildUtils.generate_builder(self.rig_type, self.asset, self.project, self.builder_inherit_path)
        self.close()
