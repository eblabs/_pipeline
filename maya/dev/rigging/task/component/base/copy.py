# IMPORT PACKAGES

# import utils
import utils.common.logUtils as logUtils
import utils.common.modules as modules

# import task
import dev.rigging.task.component.core.component as component

# ICON
import dev.rigging.builder.ui.widgets.icons as icons

# CONSTANT
logger = logUtils.logger


# CLASS
class Copy(component.Component):
    """
    copy component with kwargs override, it will override the current component with the target duplication

    Keyword Args:
        duplicate component(str): [duplicate_component] the source component name in builder
        override attributes(dict): [override_kwargs] override the given attributes to the original one,
                                                     attribute name should be the name registered in class
                                                     (the actual attr name)

    Properties:
        name(str): task's name in builder
        task(str): task's path (it will return the duplication's path instead)

        component(str): component node name
        controls(list): component's controls names
        joints(list): component's joints names
        input_matrix_attr(str): component's input matrix attribute
        input_matrix(list): component's input matrix
        offset_matrix_attr(str): component's offset matrix attribute
        offset_matrix(list): component's offset matrix
        output_matrix_attr(list): component's output matrices attributes
        output_matrix(list): component's output matrices
    """
    def __init__(self, *args, **kwargs):
        self.duplicate_component = None
        self.override_kwargs = None

        super(Copy, self).__init__(*args, **kwargs)

        self._task = 'dev.rigging.task.component.base.duplicate'
        self._task_type = 'copy'

        # icon
        self._icon_new = icons.copy_new
        self._icon_lock = icons.copy_lock
        self._icon_warn = icons.copy_warn

    def register_kwargs(self):
        self.register_attribute('duplicate component', '', attr_name='duplicate_component', attr_type='str',
                                hint="duplicate the given component", skippable=False)

        self.register_attribute('override attributes', {}, attr_name='override_kwargs', attr_type='dict',
                                hint=("override the given attributes to the original one,\n"
                                      "attribute name should be the display name in ui, or registered name in class"),
                                custom=True, skippable=False)

    def pre_build(self):
        """
        override existing pre build function, because we will need to replace with duplicated component's pre build
        """
        self.signal = 1  # preset the signal to avoid overwrite
        self.message = ''

        self.register_inputs()  # register inputs to class
        # get component object we want to duplicate
        component_orig = modules.get_obj_attr(self.builder, self.duplicate_component)
        if not component_orig:
            logger.error("can't find given component '{}' in the builder".format(self.duplicate_component))
            raise KeyError("can't find given component '{}' in the builder".format(self.duplicate_component))

        # get component path
        component_path = component_orig.task

        # because the input override kwargs may use attribute's display name as key, we need to convert into attr name
        override_kwargs_convert = {}
        for key, val in self.override_kwargs.iteritems():
            if key in component_orig.kwargs_task:
                # key is a display name, get attr name
                attr_name = component_orig.kwargs_task[key][0]
                override_kwargs_convert.update({attr_name: val})
            else:
                # assume it's the attr name
                override_kwargs_convert.update({key: val})

        # override the override_kwargs attr
        self.override_kwargs = override_kwargs_convert

        # get component kwargs
        kwargs_input = component_orig.kwargs_input
        # override kwargs
        kwargs_input.update(self.override_kwargs)

        # get component object
        component_import, component_function = modules.import_module(component_path)
        component_duplicate = getattr(component_import, component_function)(name=self._name, builder=self._builder)

        # set kwargs
        component_duplicate.kwargs_input = kwargs_input

        # attach the duplicate component to builder, override current component
        setattr(self._builder, self._name, component_duplicate)

        # call duplicate component's pre build, and because we replaced the component object in the builder,
        # it should call the duplication's build and post build function later
        component_duplicate.pre_build()
