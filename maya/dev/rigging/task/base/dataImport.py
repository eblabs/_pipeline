# IMPORT PACKAGES

import os

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.files as files

# import task
import dev.rigging.task.core.task as task


# CLASS
class DataImport(task.Task):
    """
    base class for dataImport

    used for tasks need import data from path (misc, model etc)

    Keyword Args:
        data(list): list of data path
        type(list): list of data type
    """
    def __init__(self, **kwargs):
        super(DataImport, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.base.dataImport'
        self._data = []

    def register_kwargs(self):
        super(DataImport, self).register_kwargs()

        self.register_attribute('data', [], attr_name='data_path', short_name='d', select=False, template='str',
                                hint='import data from following paths')

        self.register_attribute('type', ['ma', 'mb', 'obj'], attr_name='file_ext', select=False, template='str',
                                hint='import following type of data')

    def get_data(self):
        # self.data_path and self.file_ext are defined from self.register_attribute
        for path in self.data_path:
            if os.path.isfile(path):
                # check extension
                ext = os.path.splitext(path)[-1].lower()
                if ext in self.file_ext and path not in self._data:
                    self._data.append(path)
            elif os.path.isdir(path):
                file_paths = files.get_files_from_path(path, extension=self.file_ext)
                for p in file_paths:
                    if p not in self._data:
                        self._data.append(p)

    def import_data(self):
        for f in self._data:
            cmds.file(f, i=True)

    def pre_build(self):
        super(DataImport, self).pre_build()
        self.get_data()
        self.import_data()