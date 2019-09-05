# IMPORT PACKAGES

# import os
import os

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.naming as naming
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.rigging.joints as joints
import utils.modeling.curves as curves
import utils.modeling.surfaces as surfaces
import utils.modeling.meshes as meshes

# import task
import dev.rigging.task.core.rigData as rigData

# CONSTANT
BLUEPRINT_NAME = 'blueprint'


# CLASS
class Blueprint(rigData.RigData):
    """
    load blueprint joints, curves, surfaces and meshes
    """

    def __init__(self, **kwargs):
        super(Blueprint, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.template.base.puppet.blueprint'
        self.blueprint_grp = naming.Namer(type=naming.Type.group, side=naming.Side.middle, description='blueprint').name

    def pre_build(self):
        super(Blueprint, self).pre_build()
        self.build_blueprints()

    def build_blueprints(self):
        if not cmds.objExists(self.blueprint_grp):
            # create group if not exist
            transforms.create(self.blueprint_grp, lock_hide=attributes.Attr.all, vis=False)

        # build blueprints
        for path in self.data_path:
            for file_format, load_method in zip([joints.JOINT_INFO_FORMAT, curves.CURVE_INFO_FORMAT,
                                            surfaces.SURF_INFO_FORMAT, meshes.MESH_INFO_FORMAT],
                                           [joints.load_joints_info, curves.load_curves_info,
                                            surfaces.load_surfaces_info, meshes.load_meshes_info]):
                blueprint_path = os.path.join(path, BLUEPRINT_NAME+file_format)
                if os.path.exists(blueprint_path):
                    load_method(blueprint_path, BLUEPRINT_NAME, parent_node=self.blueprint_grp)

    def save_data(self):
        super(Blueprint, self).save_data()

        jnt_save_list = []
        crv_save_list = []
        surf_save_list = []
        mesh_save_list = []

        # check selection
        selection = cmds.ls(selection=True)

        if not selection:
            nodes_sel = cmds.listRelatives(self.blueprint_grp, allDescendents=True)
        else:
            nodes_sel = []
            for sel in selection:
                if sel not in nodes_sel:
                    # because we loop in all hierarchy node under the node, this means we already have the nodes
                    nodes.append(sel)
                    sel_hierarchy = cmds.listRelatives(sel, allDescendents=True)
                    if sel_hierarchy:
                        nodes_sel += sel_hierarchy
            nodes_sel = set(nodes_sel)  # remove multiple nodes with the same name
            nodes_sel = list(nodes_sel)

        # loop in each node
        for node_save in nodes_sel:
            # check name type
            namer = naming.Namer(node_save)
            if (namer.type == naming.Type.blueprintJoint and
                    cmds.objectType(node_save) == 'joint' and node_save not in jnt_save_list):
                jnt_save_list.append(node_save)
            elif cmds.objectType(node_save) == 'transform':
                shape_node = cmds.listRelatives(node_save, shapes=True)
                if shape_node:
                    shape_node = shape_node[0]
                    if (namer.type == naming.Type.blueprintCurve and
                            cmds.objectType(shape_node) == 'nurbsCurve' and node_save not in crv_save_list):
                        crv_save_list.append(node_save)
                    elif (namer.type == naming.Type.blueprintSurface and
                            cmds.objectType(shape_node) == 'nurbsSurface' and node_save not in surf_save_list):
                        surf_save_list.append(node_save)
                    elif (namer.type == naming.Type.blueprintMesh and
                            cmds.objectType(shape_node) == 'mesh' and node_save not in mesh_save_list):
                        mesh_save_list.append(node_save)

        # export blueprint
        for save_list, save_method in zip([jnt_save_list, crv_save_list, surf_save_list, mesh_save_list],
                                          [joints.export_joints_info, curves.export_curves_info,
                                           surfaces.export_surfaces_info, meshes.export_meshes_info]):
            if save_list:
                save_method(save_list, self.save_data_path, name=BLUEPRINT_NAME)
