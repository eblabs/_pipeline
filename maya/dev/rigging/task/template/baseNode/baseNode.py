# IMPORT PACKAGES

# import os
import os

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.naming as naming
import utils.common.files as files
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.common.nodeUtils as nodeUtils
import utils.rigging.controls as controls

# import task
import dev.rigging.task.core.task as task

# CONSTANT
import dev.rigging.task.config as config
SPACE_CONFIG_PATH = os.path.join(os.path.dirname(config.__file__), 'SPACE.cfg')
SPACE_CONFIG = files.read_json_file(SPACE_CONFIG_PATH)


# CLASS
class BaseNode(task.Task):
    """
    base class for baseNode

    create base node hierarchy

    master
        - geometries
        - components
        - mover
            - world_control
                - layout_control
                    - local_control
        - nodes
        - skeleton
    """

    def __init__(self, **kwargs):
        super(BaseNode, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.template.baseNode.baseNode'

        self.master = None
        self.geometries = None
        self.components = None
        self.mover = None
        self.nodes = None
        self.skeleton = None
        self.world_control = None
        self.layout_control = None
        self.local_control = None

    def pre_build(self):
        super(BaseNode, self).pre_build()
        self.create_hierarchy()
        self.connect_vis()
        self.set_rig_info()
        self.create_controllers()

    def post_build(self):
        super(BaseNode, self).post_build()
        self.auto_scale_controls()
        self.check_resolution()

    def create_hierarchy(self):
        """
        create base node's transform hierarchy

        master
        - geometries
        - components
        - mover
        - nodes
        - skeleton
        """
        namer = naming.Namer(type=naming.Type.master)

        # master
        self.master = transforms.create(namer.name, lock_hide=attributes.Attr.all)

        # mover
        namer.type = naming.Type.mover
        self.mover = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self.master)

        # geometries
        namer.type = naming.Type.geometries
        self.geometries = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self.master)

        # create group for each resolution
        for res in naming.Resolution.all:
            namer_res = naming.Namer(type=naming.Type.group, side=naming.Side.middle, resolution=res,
                                     description='geometries')
            grp_res = transforms.create(namer_res.name, lock_hide=attributes.Attr.all, parent=self.geometries)
            setattr(self, res, grp_res)  # add resolution group to class as attribute

        # components
        namer.type = naming.Type.components
        self.components = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self.master)

        # nodes
        namer.type = naming.Type.nodes
        self.nodes = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self.master)

        # skeleton
        namer.type = naming.Type.skeleton
        self.skeleton = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self.master)

    def connect_vis(self):
        """
        create and connect visibility attributes

        geometriesDisplayType: normal, template, reference, default is reference
        geometriesVis: geometries visibility switch, default is 1
        moverVis: mover controls visibility switch, default is 1
        controlsVis: rig controls visibility switch, default is 1
        jointsVis: rig joints visibility switch, default is 0
        rigNodesVis: rig nodes visibility switch, default is 0
        skeletonVis: skeleton visibility switch, default is 0
        """
        attributes.add_attrs(self.master, 'geometriesDisplayType', attribute_type='enum', keyable=False,
                             default_value=2, channel_box=True, enum_name='normal:template:reference')
        attributes.add_attrs(self.master,
                             ['geometriesVis', 'moverVis', 'controlsVis', 'jointsVis', 'rigNodesVis', 'skeletonVis'],
                             attribute_type='long', range=[0, 1], default_value=[1, 1, 1, 0, 0, 0], keyable=False,
                             channel_box=True)

        # connect attrs
        attributes.connect_attrs([self.master + '.geometriesDisplayType', self.master + '.geometriesVis',
                                  self.master + '.moverVis', self.master + '.rigNodesVis',
                                  self.master + '.skeletonVis'],
                                 [self.geometries + '.overrideDisplayType', self.geometries + '.visibility',
                                  self.mover + '.visibility', self.nodes + '.visibility',
                                  self.skeleton + '.visibility'],
                                 force=True)

        # set attrs
        cmds.setAttr(self.geometries + '.overrideEnabled', 1)

    def set_rig_info(self):
        """
        add project, asset and rig type attribute to the master node
        """
        if self.builder:
            project = self.builder.project
            asset = self.builder.asset
            rig_type = self.builder.rig_type

            attributes.add_attrs(self.master, ['project', 'asset', 'rigType'], attribute_type='string',
                                 default_value=[project, asset, rig_type], lock=True)

    def create_controllers(self):
        """
        create mover controllers

        world_control
            layout_control
                local_control
        """
        self.world_control = controls.create('world', side=naming.Side.middle, shape='square', color='yellow',
                                             parent=self.mover, size=1.1, sub=False)
        self.layout_control = controls.create('layout', side=naming.Side.middle, shape='crossArrowCircle',
                                              color='royal heath', parent=self.world_control.output, sub=False)
        self.local_control = controls.create('local', side=naming.Side.middle, shape='circle', color='royal purple',
                                             parent=self.layout_control.output, size=0.5, sub=False)
        # rig scale
        attributes.add_attrs([self.world_control.name, self.layout_control.name, self.local_control.name],
                             'rigScale', attribute_type='float', range=[0, None], default_value=1, keyable=True,
                             channel_box=True)
        for control in [self.world_control, self.layout_control, self.local_control]:
            attributes.connect_attrs(control.name+'.rigScale', ['scaleX', 'scaleY', 'scaleZ'], driven=control.name,
                                     force=True)

    def auto_scale_controls(self):
        """
        automatically scale mover controls to fit the geometries' bounding box, will skip if no geo in the group
        """
        # get geo bounding box info
        geo_bbox_min = cmds.getAttr(self.geometries+'.boundingBoxMin')[0]
        geo_bbox_max = cmds.getAttr(self.geometries + '.boundingBoxMax')[0]

        geo_length = max(geo_bbox_max[0]-geo_bbox_min[0], geo_bbox_max[2]-geo_bbox_min[2])

        if geo_length > 0:
            # if no geo in the group, geo_length will be 0, skip in that case
            # get local control bounding box info
            local_control_bbox_min = cmds.getAttr(self.local_control.name+'.boundingBoxMin')[0]
            local_control_bbox_max = cmds.getAttr(self.local_control.name + '.boundingBoxMax')[0]

            # it's square for sure, no need to compare
            control_length = local_control_bbox_max[0] - local_control_bbox_min[0]

            # get scale multiplier
            scale_multiplier = geo_length/float(control_length) * 1.2
            controls.transform_ctrl_shape([self.world_control.control_shape, self.layout_control.control_shape,
                                           self.local_control.control_shape], scale=scale_multiplier)

    def check_resolution(self):
        enum_attr = ''
        cond_nodes = []
        default_val = 10  # all resolution space are under 10
        for res in naming.Resolution.all:
            grp_res = getattr(self, res)  # get group node
            meshes = cmds.listRelatives(grp_res, ad=True, type='mesh')  # check if grp has meshes
            if not meshes:
                # empty resolution, delete
                cmds.delete(grp_res)
                setattr(self, res, None)  # set res attribute to None
            else:
                enum_attr += '{}={}:'.format(res, SPACE_CONFIG[res])
                cond = nodeUtils.condition(0, SPACE_CONFIG[res], 1, 0, side=naming.Side.middle, description=res+'Vis',
                                           operation=0, attrs=grp_res+'.v', force=True, node_only=True)
                cond_nodes.append(cond+'.firstTerm')
                if SPACE_CONFIG[res] < default_val:
                    default_val = SPACE_CONFIG[res]
        if enum_attr:
            # add enum attr
            attributes.add_attrs(self.master, 'resolution', attribute_type='enum', keyable=False, channel_box=True,
                                 enum_name=enum_attr, default_value=default_val)
            # connect with condition nodes
            attributes.connect_attrs(self.master+'.resolution', cond_nodes)
