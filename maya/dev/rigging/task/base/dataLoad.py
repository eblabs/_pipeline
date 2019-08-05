# IMPORT PACKAGES

# import utils
import utils.common.files as files

# import task
import dev.rigging.task.core.task as task


# CLASS
class DataLoad(task.Task):
    """
    base class for dataLoad

    used for tasks need load data from files (deformers, controlShapes etc)

    all tasks with load data function should inherit from this class

    self._dataType(str): json/numpy/cPickle
                         determine which load function to use

    Keyword Args:
        data(list): list of data path
    """
    def __init__(self, **kwargs):
        super(DataLoad, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.base.dataLoad'
        self._data_type = 'json'
        self.load_method = None
        self._data = {}

    def register_kwargs(self):
        super(DataLoad, self).register_kwargs()

        self.register_attribute('data', [], attr_name='data_path', short_name='d', select=False, template='str',
                                hint='load data from following paths')

    def get_load_method(self):
        if self._data_type == 'json':
            self.load_method = files.read_json_file
        elif self._data_type == 'numpy':
            self.load_method = files.read_numpy_file
        elif self._data_type == 'cPickle':
            self.load_method = files.read_cPickle_file

    def get_data(self):
        for path in self.data_path:
            # self.data_path is defined from self.register_attribute
            data_load = self.load_method(path)
            for key, item in data_load.iteritems():
                if key not in self._data:
                    self._data.update({key: item})

    def pre_build(self):
        super(DataLoad, self).pre_build()
        self.get_load_method()
        self.get_data()
