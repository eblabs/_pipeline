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

    Keyword Args:
        mirror(bool): [mirror] mirror component, default is False
        side(str): [side] component's side, default is middle
        description(str): [description] component's description
        description suffix(str): [description_suffix] if the component nodes description need additional suffix,
                                                      like Ik, Fk etc, put it here
        offsets(int): [ctrl_offsets] component's controls' offset groups number, default is 1
        control_size(float): [ctrl_size] component's controls' size, default is 1.0
        input connection(str):  [input_connect] component's input connection, should be a component's joint's output
                                                matrix, or an existing maya node's matrix attribute

    Properties:
        name(str): task's name in builder
        task(str): task's path

        component(str): component node name
        controls(list): component's controls names
        joints(list): component's joints names
        input_matrix_attr(str): component's input matrix attribute
        input_matrix(list): component's input matrix
        offset_matrix_attr(str): component's offset matrix attribute
        offset_matrix(list): component's offset matrix
        output_matrix_attr(list): component's output matrices attributes
        output_matrix(list): component's output matrices

        sub_components_nodes(list): pack's sub components in builder names
        sub_components_objs(list): pack's sub components objects
    """
    def __init__(self, *args, **kwargs):
        super(MultiGroup, self).__init__(*args, **kwargs)
        self._task = 'dev.rigging.task.component.pack.multiGroup'

    def register_kwargs(self):
        super(MultiGroup, self).register_kwargs()
        self.remove_attribute('blueprint joints')

    def pack_override_kwargs_registration(self):
        super(MultiGroup, self).pack_override_kwargs_registration()
        self.register_override_kwarg('ctrl_offsets', self.ctrl_offsets)
        self.register_override_kwarg('ctrl_size', self.ctrl_size)

    def create_component(self):
        super(MultiGroup, self).create_component()
        # connect vis attributes
        for sub_component_obj in self._sub_components_objs:
            attributes.connect_attrs(['controlsVis', 'jointsVis'], ['controlsVis', 'jointsVis'],
                                     driver=self._component, driven=sub_component_obj.component, force=True)
