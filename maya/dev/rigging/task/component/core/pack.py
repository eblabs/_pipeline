# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.logUtils as logUtils
import utils.common.variables as variables
import utils.common.naming as naming
import utils.common.modules as modules
import utils.common.transforms as transforms
import utils.common.attributes as attributes

# import task
import component

# ICON
import dev.rigging.builder.ui.widgets.icons as icons

# CONSTANT
logger = logUtils.logger


# CLASS
class Pack(component.Component):
    """
    base class for pack, it will connect multi components base on feature
    """
    def __init__(self, *args, **kwargs):
        super(Pack, self).__init__(*args, **kwargs)
        self._task = 'dev.rigging.task.component.core.pack'
        self._task_type = 'pack'

        # icon
        self._icon_new = icons.pack_new
        self._icon_ref = icons.pack_reference

        # vars
        # the sub components attr name in builder, use this var in widget to assign sub components
        self.sub_components_attrs = variables.kwargs('sub_components_attrs', [], kwargs)

        self._sub_component_grp = None
        self._sub_components_objs = []
        self._sub_components_override = {}

    def mirror_kwargs(self):
        super(Pack, self).mirror_kwargs()
        self.sub_components_attrs = self._flip_list(self.sub_components_attrs)

    def build(self):
        self.override_sub_components()
        self.set_sub_components_kwargs()
        super(Pack, self).build()

    def create_hierarchy(self):
        super(Pack, self).create_hierarchy()
        """
        create component group hierarchy

        component
            -- localGroup
                -- controlsGroup
                -- jointsGroup
                -- nodesShowGroup
                -- nodesHideGroup
            -- worldGroup
                -- nodesWorldGroup
            -- subComponentGroup
        """
        namer = naming.Namer(type=naming.Type.subComponentGroup, side=self.side,
                             description=self.description+self.description_suffix, index=1)

        # create transforms
        # sub component group
        self._sub_component_grp = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self._component)

        # message attr for sub components
        attributes.add_attrs(self._component, 'subComponents', attribute_type='message', multi=True)

    def override_sub_components(self):
        """
        override sub components kwargs to pack's information
        """
        # sub components input should always be the same with pack
        self.override_sub_component_kwarg('input_connect', self.input_connect)
        # sub components should be parented to pack's sub component group
        self.override_sub_component_kwarg('_parent', self._sub_component_grp)

    def override_sub_component_kwarg(self, sub_component_attr, value):
        """
        override sub component kwarg to given value

        Args:
            sub_component_attr(str): sub component attr need to be override
            value: value to override
        """
        self._sub_components_override.update({sub_component_attr: value})

    def set_sub_components_kwargs(self):
        for sub_component_obj in self._sub_components_objs:
            for attr, val in self._sub_components_override.iteritems():
                setattr(sub_component_obj, attr, val)

    def create_component(self):
        super(Pack, self).create_component()
        # get sub objects
        for sub_attr in self.sub_components_attrs:
            sub_obj = self._get_obj_attr('_builder.'+sub_attr)
            if sub_obj:
                self._sub_components_objs.append(sub_obj)
            else:
                logger.error("can't find given component '{}' in the builder".format(sub_attr))
                raise RuntimeError()

        # parent each sub component to sub component group
        for sub_component_obj in self._sub_components_objs:
            cmds.parent(sub_component_obj.component, self._sub_component_grp)
            attributes.connect_attrs(['rigNodesVis', 'inputMatrix', 'offsetMatrix'],
                                     ['rigNodesVis', 'inputMatrix', 'offsetMatrix'],
                                     driver=self._component, driven=sub_component_obj.component, force=True)

    def register_component_info(self):
        """
        register component information to component node
        """
        super(Pack, self).register_component_info()
        # connect sub component's top node to subComponentGroup
        for i, sub_obj in enumerate(self._sub_components_objs):
            cmds.connectAttr(sub_obj.component+'.message', '{}.subComponents[{}]'.format(self._component, i))

    def get_component_info(self, component_node):
        """
        get component information from component node
        """
        super(Pack, self).get_component_info(component_node)
        sub_component_nodes = self._get_attr(self._component+'.subComponents')

        sub_components_dict = {'sub_components': {'nodes': []}}

        # get sub component obj
        for sub_node in sub_component_nodes:
            sub_node_type = cmds.getAttr(sub_node+'.componentType')
            sub_obj = modules.import_module(sub_node_type)
            sub_obj_name = cmds.getAttr(sub_node+'.inClassName')
            sub_components_dict['sub_components']['nodes'].append(sub_obj_name)
            sub_components_dict['sub_components'].update({sub_obj_name: sub_obj})

        self._add_attr_from_dict(sub_components_dict)
