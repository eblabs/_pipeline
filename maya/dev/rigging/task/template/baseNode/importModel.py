# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.naming as naming
import utils.modeling.modelUtils as modelUtils

# import task
import dev.rigging.task.core.task as task


# CLASS
class ImportModel(task.Task):
    """
    import model for current asset
    """

    def __init__(self, **kwargs):
        super(ImportModel, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.template.baseNode.importModel'
        self.model_info = []
        self.import_model_groups = []

    def register_kwargs(self):
        super(ImportModel, self).register_kwargs()

        self.register_attribute('model', [{'model_type': '', 'resolution': []}], attr_name='model_info', select=False,
                                template='model_data', hint='load model from following paths')

    def pre_build(self):
        super(ImportModel, self).pre_build()
        self.import_model_from_paths()
        self.parent_model_groups()

    def import_model_from_paths(self):
        # loop in each model path
        for model_data in self.model_info:
            model_type = model_data['model_type']
            model_res = model_data['resolution']
            if model_type:
                model_grps = modelUtils.import_model(model_type, self.asset, self.project, resolution=model_res)
                if model_grps:
                    for res in model_grps:
                        self.import_model_groups.append(model_grps[res])

    def parent_model_groups(self):
        # get master node
        master_node = naming.Namer(type=naming.Type.master).name

        # check if master exist
        if cmds.objExists(master_node):
            # get all resolution transform group
            trans_grps = {}
            for i in range(len(naming.Resolution.all)):
                trans_grp = cmds.listConnections('{}.resolutionGroups[{}].transformGroup'.format(master_node, i))
                if trans_grp:
                    trans_namer = naming.Namer(trans_grp[0])
                    trans_grps.update({trans_namer.resolution: trans_grp[0]})

            # parent each model group to resolution
            for model_grp in self.import_model_groups:
                model_namer = naming.Namer(model_grp)
                res = model_namer.resolution
                if res in trans_grps:
                    cmds.parent(model_grp, trans_grps[res])

