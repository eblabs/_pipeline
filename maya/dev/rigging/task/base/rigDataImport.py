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
import utils.rigging.buildUtils as buildUtils

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

        self.update_attribute('data', default=[{'project': '', 'asset': '', 'rig_type': '', 'filter': ''}],
                              template='rig_data_import')

        # self.register_attribute('filter', [], attr_name='filter', select=False, template='str',
        #                         hint="filter, import either specific files or file types, import all if empty")

    def get_data(self):
        data_import_path = []

        for d_info in self.data_info:
            project = d_info['project']
            asset = d_info['asset']
            rig_type = d_info['rig_type']
            d_filter = d_info['filter']
            if not project:
                project = self.project
            if not asset:
                asset = self.asset
            if not rig_type:
                rig_type = self.rig_type

            if project and asset and rig_type:
                data_folder = buildUtils.get_data_path(self._name, rig_type, asset, project, warning=False,
                                                       check_exist=True)

                if data_folder:
                    # has path, check filter
                    if d_filter:
                        for f_name in d_filter:
                            if f_name in ['.mb', '.ma', '.obj']:
                                # file type
                                files_import = files.get_files_from_path(data_folder, extension=f_name)
                                data_import_path += files_import
                            elif not f_name.startswith('.'):
                                # should be file name
                                file_path = os.path.join(data_folder, f_name)
                                if os.path.isfile(file_path):
                                    data_import_path.append(file_path)
                    else:
                        # get all
                        files_import = files.get_files_from_path(data_folder, extension=['.mb', '.ma', '.obj'])
                        data_import_path += files_import

        self.data_path = list(set(data_import_path))

    def import_data(self):
        for f in self.data_path:
            cmds.file(f, i=True)
            logger.info("import '{}' successfully".format(f))

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
                if file_name.endswith('.ma') or file_name.endswith('.mb') or file_name.endswith('.obj'):
                    self.export_file(file_path)
                    logger.info("export file '{}' to path '{}' successfully".format(file_name, file_path))
                else:
                    logger.warning("export path '{}' is invalid".format(file_path))
        else:
            logger.warning('nothing selected, skipped')

    @staticmethod
    def export_file(file_path):
        file_type = os.path.splitext(file_path)[-1]
        if file_type == '.ma':
            cmds.file(file_path, exportSelected=True, type='mayaAscii', preserveReferences=True)
        elif file_type == '.mb':
            cmds.file(file_path, exportSelected=True, type='mayaBinary', preserveReferences=True)
        elif file_type == '.obj':
            cmds.file(file_path, exportSelected=True, type='OBJexport', preserveReferences=True,
                      options="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")
        else:
            logger.warning('file type: {} does not supported'.format(file_type))
