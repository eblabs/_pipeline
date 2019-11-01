# IMPORT PACKAGES

# import utils
import utils.common.naming as naming
import utils.common.modules as modules

# import task
import dev.rigging.task.core.task as task


# CLASS
class Mirror(task.Task):
    """mirror create component """
    def __init__(self, **kwargs):
        self.mirror_component = None
        super(Mirror, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.base.mirror'

    def register_kwargs(self):
        super(Mirror, self).register_kwargs()

        self.register_attribute('mirror component', '', attr_name='mirror_component', attr_type='str',
                                hint="mirror create the given component")

    def get_component_info(self):
        # get component attached to builder
        component_orig = self._get_obj_attr('builder' + self.mirror_component)
        if not component_orig:
            raise KeyError("can't find given component '{}' in the builder".format(self.mirror_component))

        # get component info
        component_path = component_orig.task
        component_parent = naming.mirror_name(component_orig.parent, keep_orig=True)
        component_name_flip = naming.mirror_name(self.mirror_component)
        component_kwargs = component_orig.kwargs_task

        # load component
        component_import, component_function = modules.import_module(component_path)
        component = getattr(component_import, component_function)(name=component_name_flip, builder=self._builder,
                                                                  parent=component_parent, mirror=True)

        # set kwargs
        component.kwargs_task = component_kwargs
        component.register_inputs()
        component.mirror_kwargs()
