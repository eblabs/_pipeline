# IMPORT PACKAGES

# import time
import time

# import task
import dev.rigging.task.core.task as task

# import utils
import utils.common.logUtils as logUtils

# CONSTANT
logger = logUtils.get_logger(name='testTask', level='info')


# CLASS
class TestTask(task.Task):
    """
    base class for testing

    """
    def __init__(self, **kwargs):
        super(TestTask, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.test.testTask'

    def register_kwargs(self):
        super(TestTask, self).register_kwargs()
        self.register_attribute('data', [], attr_name='data_path', short_name='d', select=False, template='str',
                                hint='load data from following paths')

        self.register_attribute('selection', [], attr_name='sel', select=True, template='str', hint='select nodes')

        self.register_attribute('connection', {'output1': 'input1'}, attr_name='connect', template='str', key_edit=True,
                                hint='connect nodes')

        self.register_attribute('joints', 5, attr_name='jnt_num', short_name='j', min=1, max=10, hint='joints number')

    def pre_build(self):
        super(TestTask, self).pre_build()
        logger.info('--------- Test Task Pre Build ---------')
        for i in range(10):
            time.sleep(0.1)
            print i

    def build(self):
        super(TestTask, self).build()
        logger.info('--------- Test Task Build ---------')
        for i in range(10):
            time.sleep(0.1)
            print i

    def post_build(self):
        super(TestTask, self).post_build()
        logger.info('--------- Test Task Post Build ---------')
        for i in range(10):
            time.sleep(0.1)
            print i
