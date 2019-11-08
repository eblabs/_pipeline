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

        self._pack_kwargs_override = {}

        self._sub_components_grp = None
        self._sub_components_objs = []
        self._sub_components_override = {}

    def pre_build(self):
        super(Pack, self).pre_build()
        self.pack_override_kwargs_registration()
        self.set_override_kwargs_to_builder()

    def in_class_attributes_mirror_registration(self):
        super(Pack, self).in_class_attributes_mirror_registration()
        self.set_attribute_for_mirror('sub_components_attrs')

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
            -- subComponentsGroup
        """
        namer = naming.Namer(type=naming.Type.subComponentsGroup, side=self.side,
                             description=self.description+self.description_suffix, index=1)

        # create transforms
        # sub component group
        self._sub_components_grp = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self._component)

        # message attr for sub components
        attributes.add_attrs(self._component, 'subComponents', attribute_type='message', multi=True)

    def pack_override_kwargs_registration(self):
        """
        because the pack shares some of the kwargs with its sub components,
        and we don't want the user to set each separately and keep those the same by themselves
        the problem is because the pack object register before its sub components,
        especially when we do mirror, there won't be sub components when we do pack's pre build
        so we register those override kwargs back to the builder as a dict, with sub components attr name as key,
        and in each component, we will search the dict to see if anything need to be override before set kwargs
        """
        # mirror behavior should keep consistent
        self.register_override_kwarg('mirror', self.mirror)

        # sub components input should always be connected to pack, so skip this attr
        self.register_override_kwarg('input_connect', None)

    def register_override_kwarg(self, attr, value):
        """
        register each  pack override kwarg to the builder

        Args:
            attr(str): attribute name
            value: attribute value to override
        """
        self._pack_kwargs_override.update({attr: value})

    def set_override_kwargs_to_builder(self):
        """
        set override kwargs back to builder, with sub components attr names as key
        """
        pack_kwargs_override = self._get_obj_attr('_builder.pack_kwargs_override')
        if pack_kwargs_override is not None and self._pack_kwargs_override:
            # get mirrored pack override kwargs
            pack_kwargs_override_mirror = self._flip_val(self._pack_kwargs_override)
            for sub_attr_name in self.sub_components_attrs:
                self._builder.pack_kwargs_override.update({sub_attr_name: self._pack_kwargs_override})
                # set for mirror component as well
                # if self.mirror:
                #     sub_attr_name_mirror = self._flip_val(sub_attr_name)
                #     self._builder.pack_kwargs_override.update({sub_attr_name_mirror: pack_kwargs_override_mirror})

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

        # connect input and some attr, keep them consistent with pack
        # parent sub components to sub group
        for sub_component_obj in self._sub_components_objs:
            # parent sub component to sub group
            cmds.parent(sub_component_obj.component, self._sub_components_grp)
            # connect attr
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