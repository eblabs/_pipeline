# IMPORT PACKAGES

# import utils
import utils.common.logUtils as logUtils
import utils.common.attributes as attributes

# import task
import dev.rigging.task.component.core.pack as pack

# CONSTANT
logger = logUtils.logger


# CLASS
class MultiGroup(pack.Pack):
    """
    base class for multi group pack, it will group multi components as one group pack, like fingers
    """
    def __init__(self, *args, **kwargs):
        super(MultiGroup, self).__init__(*args, **kwargs)
        self._task = 'dev.rigging.task.component.pack.multiGroup'

    def override_sub_components(self):
        super(MultiGroup, self).override_sub_components()
        self.override_sub_component_kwarg('ctrl_offsets', self.ctrl_offsets)
        self.override_sub_component_kwarg('ctrl_size', self.ctrl_size)

    def create_component(self):
        super(MultiGroup, self).create_component()
        # connect vis attributes
        for sub_component_obj in self._sub_components_objs:
            attributes.connect_attrs(['controlsVis', 'jointsVis'], ['controlsVis', 'jointsVis'],
                                     driver=self._component, driven=sub_component_obj.component, force=True)
