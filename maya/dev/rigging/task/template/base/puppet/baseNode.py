# IMPORT PACKAGES

# import os
import os

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.naming as naming
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.common.nodeUtils as nodeUtils
import utils.rigging.controls as controls
import utils.modeling.meshes as meshes

# import task
import dev.rigging.task.core.task as task

# CONSTANT
RES_CONFIG = {"high": 0,
              "middle": 1,
              "low": 2,
              "proxy": 3,
              "simulation": 4}


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

    Properties:
        world_matrix_attr(str): global mover's position matrix output attribute
        world_matrix_transform_attrs(list): global mover's position attributes, ['translate', 'rotate', 'scale']
    """

    def __init__(self, **kwargs):
        super(BaseNode, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.template.base.puppet.baseNode'

        self.master = None
        self.geometries = None
        self.components = None
        self.mover = None
        self.nodes = None
        self.skeleton = None
        self.world_control = None
        self.layout_control = None
        self.local_control = None

    @ property
    def world_matrix_attr(self):
        return self.master + '.matrixWorld'

    @ property
    def world_matrix_transform_attrs(self):
        attrs = []
        for attr in ['translate', 'rotate', 'scale']:
            world_attr = 'world' + attr.title()
            attrs.append('{}.{}'.format(self.master, world_attr))
        return attrs

    def pre_build(self):
        super(BaseNode, self).pre_build()
        if self._builder:
            # plug self object as base node
            setattr(self._builder, 'base_node', self)
        self.create_hierarchy()
        self.connect_vis()
        self.set_rig_info()
        self.create_controllers()

    def post_build(self):
        super(BaseNode, self).post_build()
        self.auto_scale_controls()

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
        # add compound attr
        cmds.addAttr(self.master, longName='resolutionGroups', attributeType='compound', multi=True, numberOfChildren=3)
        cmds.addAttr(self.master, longName='resGroup', attributeType='message', parent='resolutionGroups')
        cmds.addAttr(self.master, longName='transformGroup', attributeType='message', parent='resolutionGroups')
        cmds.addAttr(self.master, longName='deformGroup', attributeType='message', parent='resolutionGroups')

        enum_attr = ''
        cond_nodes = []
        default_val = 10
        for i, res in enumerate(naming.Resolution.Key.all):
            namer_res = naming.Namer(type=naming.Type.group, side=naming.Side.middle, resolution=res,
                                     description='geometries')
            grp_res = transforms.create(namer_res.name, lock_hide=attributes.Attr.all, parent=self.geometries)

            # transform group
            namer_res.description = 'transform'
            grp_trans = transforms.create(namer_res.name, lock_hide=attributes.Attr.all, parent=grp_res)
            # deformation group
            namer_res.description = 'deform'
            grp_deform = transforms.create(namer_res.name, lock_hide=attributes.Attr.all, parent=grp_res)

            # connect to master's compound attr
            attributes.connect_attrs([grp_res+'.message', grp_trans+'.message', grp_deform+'.message'],
                                     ['{}.resolutionGroups[{}].resGroup'.format(self.master, i),
                                      '{}.resolutionGroups[{}].transformGroup'.format(self.master, i),
                                      '{}.resolutionGroups[{}].deformGroup'.format(self.master, i)])

            # enum attr info
            enum_attr += '{}={}:'.format(res, RES_CONFIG[res])

            cond = nodeUtils.condition(0, RES_CONFIG[res], 1, 0, side=naming.Side.middle, description=res+'Vis',
                                       operation=0, attrs=grp_res + '.v', force=True, node_only=True)
            cond_nodes.append(cond + '.firstTerm')

            if RES_CONFIG[res] < default_val:
                default_val = RES_CONFIG[res]

            # add to class as attribute
            res_grp_info = {'group': grp_res,
                            'transform': grp_trans,
                            'deform': grp_deform}
            self._add_obj_attr(res, res_grp_info)

        # add enum attr for resolution switch
        attributes.add_attrs(self.master, 'resolution', attribute_type='enum', keyable=False, channel_box=True,
                             enum_name=enum_attr[:-1], default_value=default_val)
        # connect with condition nodes
        attributes.connect_attrs(self.master + '.resolution', cond_nodes)

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
                             attribute_type='bool', default_value=[True, True, True, False, False, False],
                             keyable=False, channel_box=True)

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
            attributes.connect_attrs(control.name+'.rigScale', attributes.Attr.scale, driven=control.name,
                                     force=True)

        # world matrix
        attributes.add_attrs(self.master, 'matrixWorld', attribute_type='matrix', keyable=False)
        mult_matrix_world_output = nodeUtils.mult_matrix([self.local_control.object_matrix_attr,
                                                          self.layout_control.object_matrix_attr,
                                                          self.world_control.object_matrix_attr],
                                                         attrs=self.master+'.matrixWorld', side=naming.Side.middle,
                                                         description='masterWorldMatrix')

        # world translate/rotate/scale
        decompose_matrix_world = nodeUtils.node(type=naming.Type.decomposeMatrix, side=naming.Side.middle,
                                                description='masterWorldTransform')
        cmds.connectAttr(mult_matrix_world_output, decompose_matrix_world+'.inputMatrix')

        transform_attr = []

        for attr in ['translate', 'rotate', 'scale']:
            world_attr = 'world' + attr.title()
            cmds.addAttr(self.master, longName=world_attr, attributeType='float3')
            transform_attr.append('{}.{}'.format(self.master, world_attr))
            for axis in 'XYZ':
                cmds.addAttr(self.master, longName=world_attr+axis, attributeType='float', parent=world_attr)
            for axis in 'XYZ':
                # need to loop again because float3 attr won't be added until all axis attrs are added
                cmds.connectAttr('{}.output{}{}'.format(decompose_matrix_world, attr.title(), axis),
                                 '{}.{}{}'.format(self.master, world_attr, axis))

        # connect transform attr with res transform group
        for res in naming.Resolution.Key.all:
            grp_trans = self._get_obj_attr(res+'.transform')
            for pos_attr, trans_attr in zip(transform_attr, ['translate', 'rotate', 'scale']):
                attributes.connect_attrs([pos_attr+'X', pos_attr+'Y', pos_attr+'Z'],
                                         [trans_attr+'X', trans_attr+'Y', trans_attr+'Z'],
                                         driven=grp_trans, force=True)

    def auto_scale_controls(self):
        """
        automatically scale mover controls to fit the geometries' bounding box, will skip if no geo in the group
        """
        # get all meshes from geo group
        meshes_nodes = meshes.get_meshes_from_node(self.geometries)

        # get geo bounding box info
        if meshes_nodes:
            bbox_info = cmds.exactWorldBoundingBox(meshes_nodes)

            geo_length = max(bbox_info[3]-bbox_info[0], bbox_info[5]-bbox_info[2])

            # if no geo in the group, geo_length will be 0, skip in that case
            # get local control bounding box info
            local_control_bbox_min = cmds.getAttr(self.local_control.name+'.boundingBoxMin')[0]
            local_control_bbox_max = cmds.getAttr(self.local_control.name + '.boundingBoxMax')[0]

            # it's square for sure, no need to compare
            control_length = local_control_bbox_max[0] - local_control_bbox_min[0]

            # get scale multiplier
            scale_multiplier = geo_length/float(control_length)
            controls.transform_ctrl_shape([self.world_control.control_shape, self.layout_control.control_shape,
                                           self.local_control.control_shape], scale=scale_multiplier)
