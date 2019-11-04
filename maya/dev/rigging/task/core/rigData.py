# IMPORT PACKAGES

# import utils
import utils.rigging.buildUtils as buildUtils

# import task
import task

# ICON
import dev.rigging.builder.ui.widgets.icons as icons


# CLASS
class RigData(task.Task):
    """
    base class for loading data

    used for tasks need load data (deformers, controlShapes, models etc)

    all tasks with load data function should inherit from this class

    Keyword Args:
        data(list): list of data path
    """
    def __init__(self, **kwargs):
        self.data_info = None

        super(RigData, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.core.data'
        self._task_type = 'data'
        self._save = True
        self.data_path = []

        self._icon_new = icons.data_new
        self._icon_ref = icons.data_reference

    def register_kwargs(self):
        super(RigData, self).register_kwargs()

        self.register_attribute('data', [{'project': '', 'asset': '', 'rig_type': ''}], attr_name='data_info',
                                short_name='d', select=False, template='rig_data',
                                hint='load data from following paths')

    def pre_build(self):
        super(RigData, self).pre_build()
        self.get_data()

    def get_data(self):
        """
        get data path from given information
        """
        data_folder_path = []

        for d_info in self.data_info:
            project = d_info['project']
            asset = d_info['asset']
            rig_type = d_info['rig_type']

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

        self.data_path = list(set(data_folder_path))
