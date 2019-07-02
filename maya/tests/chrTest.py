import dev.rigging.builder.core.builder as builder

import time

class ChrTest(builder.Builder):
    def __init__(self):
        super(ChrTest, self).__init__()

    def registertion(self):
        super(ChrTest, self).registertion()
        
        self.register_task(name='importModel',
                           display='Model',
                           task='dev.rigging.task.test.testTask')
        self.register_task(name='miscs',
                           task=self._func)
        self.register_task(name='blueprints',
                           task=self._func,
                           index=1)
        self.register_task(name='blueprintJoints',
                           display='Joints',
                           task=self._func,
                           parent='blueprints')
        self.register_task(name='blueprintCurve',
                           task=self._func,
                           parent='blueprints')
        self.register_task(name='blueprintMesh',
                           task=self._func,
                           parent='blueprints')
        self.register_task(name='components',
                           task=self._func)
        self.register_task(name='arm',
                           task=self._func,
                           parent='components')
        self.register_task(name='ik',
                           task=self._func,
                           parent='arm')
        self.register_task(name='fk',
                           task=self._error,
                           parent='arm')
        self.register_task(name='baseNode',
                           task=self._func,
                           kwargs={'name': {'value': 'register task name',
                                            'type': 'str'}},
                           index=1)

    def _func(self, name='my test function'):
        for i in range(20):
            time.sleep(0.1)
            print i

    def _error(self):
        raise RuntimeError('Error Test')