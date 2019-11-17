# IMPORT PACKAGES

# import os
import os

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.files as files
import utils.common.logUtils as logUtils
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
logger = logUtils.logger


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
            transforms.create(self.blueprint_grp, lock_hide=attributes.Attr.transform, vis=False)

        # build blueprints
        for path in self.data_path:
            for load_method in [joints.load_joints_info, curves.load_curves_info, surfaces.load_surfaces_info,
                                meshes.load_meshes_info]:
                load_method(path, BLUEPRINT_NAME, parent_node=self.blueprint_grp)

    def save_data(self):
        super(Blueprint, self).save_data()

        jnt_save_list = []
        crv_save_list = []
        surf_save_list = []
        mesh_save_list = []

        nodes_sel = cmds.listRelatives(self.blueprint_grp, allDescendents=True)

        # loop in each node
        for node_save in nodes_sel:
            # check name type
            namer = naming.check_name_convention(node_save)
            if namer:
                # node is a recognized type
                if (namer.type == naming.Type.Key.bjnt and
                        cmds.objectType(node_save) == 'joint' and node_save not in jnt_save_list):
                    jnt_save_list.append(node_save)
                elif cmds.objectType(node_save) == 'transform':
                    shape_node = cmds.listRelatives(node_save, shapes=True)
                    if shape_node:
                        shape_node = shape_node[0]
                        if (namer.type == naming.Type.Key.bcrv and
                                cmds.objectType(shape_node) == 'nurbsCurve' and node_save not in crv_save_list):
                            crv_save_list.append(node_save)
                        elif (namer.type == naming.Type.Key.bsurf and
                                cmds.objectType(shape_node) == 'nurbsSurface' and node_save not in surf_save_list):
                            surf_save_list.append(node_save)
                        elif (namer.type == naming.Type.Key.bmsh and
                                cmds.objectType(shape_node) == 'mesh' and node_save not in mesh_save_list):
                            mesh_save_list.append(node_save)

        # export blueprint
        for save_list, save_method in zip([jnt_save_list, crv_save_list, surf_save_list, mesh_save_list],
                                          [joints.export_joints_info, curves.export_curves_info,
                                           surfaces.export_surfaces_info, meshes.export_meshes_info]):

            if save_list:
                save_method(save_list, self.save_data_path, name=BLUEPRINT_NAME)

    def update_data(self):
        super(Blueprint, self).update_data()
        # get data from data file
        bp_data = []

        for file_type in [joints.JOINT_INFO_FORMAT, curves.CURVE_INFO_FORMAT, surfaces.SURF_INFO_FORMAT,
                          meshes.MESH_INFO_FORMAT]:
            path = os.path.join(self.save_data_path, BLUEPRINT_NAME+file_type)
            if os.path.exists(path):
                # get data
                data_from_path = files.read_json_file(path)
            else:
                data_from_path = {}
            bp_data.append(data_from_path)

        # get selection
        selection = cmds.ls(selection=True)

        if selection:
            nodes_sel = []
            for sel in selection:
                if sel not in nodes_sel:
                    # because we loop in all hierarchy node under the node, this means we already have the nodes
                    nodes_sel.append(sel)
                    sel_hierarchy = cmds.listRelatives(sel, allDescendents=True)
                    if sel_hierarchy:
                        nodes_sel += sel_hierarchy
            nodes_sel = list(set(nodes_sel))  # remove multiple nodes with the same name

            # put checker here, will read those check after all to see if we need to export anything
            jnt_check = False
            crv_check = False
            surf_check = False
            mesh_check = False

            # loop in each node
            for node in nodes_sel:
                # check name
                namer = naming.check_name_convention(node)
                if namer:
                    # node is a recognized type
                    if namer.type == naming.Type.Key.bjnt and cmds.objectType(node) == 'joint':
                        # it's a blueprint joint, update joint info
                        bp_data[0], jnt_check = self.update_blueprint_node_info(node, bp_data[0], joints.get_joint_info)

                    elif cmds.objectType(node) == 'transform':
                        shape_node = cmds.listRelatives(node, shapes=True)
                        if shape_node:
                            shape_node = shape_node[0]
                            if namer.type == naming.Type.Key.bcrv and cmds.objectType(shape_node) == 'nurbsCurve':
                                # it's a blueprint curve, update curve info
                                bp_data[1], crv_check = self.update_blueprint_node_info(node, bp_data[1],
                                                                                        curves.get_curve_info)

                            elif namer.type == naming.Type.Key.bsurf and cmds.objectType(shape_node) == 'nurbsSurface':
                                # it's a blueprint surface, update surf info
                                bp_data[2], surf_check = self.update_blueprint_node_info(node, bp_data[2],
                                                                                         surfaces.get_surface_info)

                            elif namer.type == naming.Type.Key.bmsh and cmds.objectType(shape_node) == 'mesh':
                                # it's a blueprint mesh, update mesh info
                                bp_data[3], mesh_check = self.update_blueprint_node_info(node, bp_data[3],
                                                                                         meshes.get_mesh_info)

            # save updated info
            self.write_blueprint_info_to_file(BLUEPRINT_NAME + joints.JOINT_INFO_FORMAT, self.save_data_path,
                                              bp_data[0], jnt_check)
            self.write_blueprint_info_to_file(BLUEPRINT_NAME + curves.CURVE_INFO_FORMAT, self.save_data_path,
                                              bp_data[1], crv_check)
            self.write_blueprint_info_to_file(BLUEPRINT_NAME + surfaces.SURF_INFO_FORMAT, self.save_data_path,
                                              bp_data[2], surf_check)
            self.write_blueprint_info_to_file(BLUEPRINT_NAME + meshes.MESH_INFO_FORMAT, self.save_data_path,
                                              bp_data[3], mesh_check)

            # warn if nothing to be updated
            if not jnt_check and not crv_check and not surf_check and not mesh_check:
                logger.warning("no blueprint node selected, skipped")

        else:
            logger.warning("nothing selected, skipped")

    @ staticmethod
    def update_blueprint_node_info(node, bp_dict, get_info_method):
        """
        update given blueprint node to given dict
        Args:
            node(str): node name
            bp_dict(dict): blueprint info
            get_info_method(function): get info function

        Returns:
            bp_dict(dict)
            checker(bool)
        """
        node_info = get_info_method(node)
        bp_dict.update(node_info)
        checker = True
        return bp_dict, checker

    @ staticmethod
    def write_blueprint_info_to_file(file_name, file_path, bp_data, checker):
        """
        write given blueprint info to file

        Args:
            file_name(str)
            file_path(str)
            bp_data(dict)
            checker(bool)
        """
        if checker:
            bp_path = os.path.join(file_path, file_name)
            files.write_json_file(bp_path, bp_data)
            logger.info("update {} to path {} successfully".format(file_name, bp_path))
