# IMPORT PACKAGES

import os

# import maya packages
import maya.cmds as cmds

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
import utils.common.files as files
import utils.common.logUtils as logUtils
import utils.common.uiUtils as uiUtils

# import task
import dev.rigging.task.core.rigData as rigData

# CONSTANT
logger = logUtils.logger


# CLASS
class RigDataImport(rigData.RigData):
    """
    base class for dataImport

    used for tasks need import data from path (misc, model etc)

    Keyword Args:
        data(list): list of data path
        type(list): list of data type
    """
    def __init__(self, **kwargs):
        super(RigDataImport, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.base.dataImport'

    def register_kwargs(self):
        super(RigDataImport, self).register_kwargs()

        self.register_attribute('filter', [], attr_name='filter', select=False, template='str',
                                hint="filter, import either specific files or file types, import all if empty")

    def get_data(self):
        super(RigDataImport, self).get_data()

        path_import = []

        for path in self.data_path:
            if self.file_name:
                for f_name in self.file_name:
                    if f_name.startswith('.'):
                        # file type
                        files_import = files.get_files_from_path(path, extension=f_name)
                        path_import += files_import
                    else:
                        # should be file name
                        file_path = os.path.join(path, f_name)
                        if os.path.isfile(file_path) and os.path.exists(file_path):
                            path_import.append(file_path)
            else:
                # get all
                files_import = files.get_files_from_path(path)
                path_import += files_import

        path_import = list(set(path_import))

        self.data_path = path_import

    def import_data(self):
        for f in self.data_path:
            cmds.file(f, i=True)

    def pre_build(self):
        super(RigDataImport, self).pre_build()
        self.import_data()

    def save_data(self):
        super(RigDataImport, self).save_data()
        self.save_select_data()

    def save_select_data(self):
        sel = cmds.ls(selection=True)
        maya_window = uiUtils.get_maya_window()
        if sel:
            # pop up window
            file_name, ok = QInputDialog.getText(maya_window, 'Export Selection', 'File name:')
            if file_name and ok:
                file_path = os.path.join(self.save_data_path, file_name)
                if os.path.isfile(file_path):
                    if os.path.exists(file_path):
                        # check if override
                        title = "File exists"
                        text = "File: '{}' exists at Path: '{}', are you sure you want to override it?".format(file_name,
                                                                                                               file_path)
                        reply = QMessageBox.warning(maya_window, title, text, QMessageBox.Ok | QMessageBox.Cancel,
                                                    defaultButton=QMessageBox.Cancel)

                        if reply == QMessageBox.Ok:
                            # override
                            self.export_file(file_path)
                    else:
                        self.export_file(file_path)
                else:
                    logger.warning("export path '{}' is invalid".format(file_path))
        else:
            logger.warning('nothing selected, skipped')

    @staticmethod
    def export_file(file_path):
        file_type = os.path.splitext(file_path)[-1]
        if file_type == 'ma':
            cmds.file(file_path, exportSelected=True, type='mayaAscii', preserveReferences=True)
        elif file_type == 'mb':
            cmds.file(file_path, exportSelected=True, type='mayaBinary', preserveReferences=True)
        elif file_type == 'obj':
            cmds.file(file_path, exportSelected=True, type='OBJ', preserveReferences=True,
                      options="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")
        else:
            logger.warning('file type: {} does not supported'.format(file_type))
