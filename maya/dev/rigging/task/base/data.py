# IMPORT PACKAGES

# import os
import os

# import utils
import utils.rigging.buildUtils as buildUtils

# import task
import dev.rigging.task.core.task as task


# CLASS
class Data(task.Task):
    """
    base class for loading data

    used for tasks need load data (deformers, controlShapes, models etc)

    all tasks with load data function should inherit from this class

    Keyword Args:
        data(list): list of data path
    """
    def __init__(self, **kwargs):
        super(Data, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.base.data'
        self._data = {}
        self.data_path = []
        self.save_data_path = None

    def register_kwargs(self):
        super(Data, self).register_kwargs()

        self.register_attribute('data', [], attr_name='data_path', short_name='d', select=False, template='data',
                                hint='load data from following paths')

    def pre_build(self):
        super(Data, self).pre_build()
        self.get_data()

    def save_data(self):
        """
        save data to current rig's data folder, will automatically create folder if not exist
        """
        self.save_data_path = buildUtils.get_data_path(self._name, self.rig_type, self.asset, self.project,
                                                       warning=False, check_exist=False)
        # create folder if not exist
        if not os.path.exists(self.save_data_path):
            os.mkdir(self.save_data_path)

    def get_data(self):
        """
        get data path from given information
        """
        data_folder_path = []

        for path in self.data_path:
            project = path['project']
            asset = path['asset']
            rig_type = path['rig_type']

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
                    data_folder_path.append(data_folder)

        self.data_path = data_folder_path
