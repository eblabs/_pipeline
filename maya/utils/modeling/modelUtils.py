# IMPORT PACKAGES

# import os
import os

# import datetime
import datetime

# import shutil
import shutil

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.assets as assets
import utils.common.logUtils as logUtils
import utils.common.files as files
import utils.common.naming as naming
import utils.common.versionize as versionize

# CONSTANT
logger = logUtils.logger
PUBLISH_INFO_FILE = 'publish_info.pub'
PUBLISH_INFO_TEMPLATE = {'resolution': [],
                         'comment': '',
                         'date': ''}


# FUNCTION
def publish_model(model_type, asset, project, comment=''):
    """
    publish model, will separate into different resolution and write in a json file for query

    Args:
        model_type(str): model's type (body, costume, anatomy etc...)
        asset(str): asset name
        project(str): project name

    Keyword Args:
        comment(str): publish comment

    Returns:
        model_paths(list): published model path for each resolution
    """
    # check model type exist
    model_path = assets.get_model_path_from_asset(model_type, asset, project, warning=False)
    if model_path:
        # model type exist, prepare to publish
        publish_folder = os.path.join(model_path, 'publish')
        publish_info = PUBLISH_INFO_TEMPLATE.copy()
        publish_info['resolution'] = []
        publish_grps = {}
        model_paths_return = []
        # get all resolution model groups
        namer_res = naming.Namer(type=naming.Type.group, side=naming.Side.middle, description=model_type, index=1)
        for res in naming.Resolution.all:
            namer_res.resolution = res
            res_grp = namer_res.name

            # check if resolution group exist
            if cmds.objExists(res_grp):
                # check if has mesh
                meshes = cmds.listRelatives(res_grp, ad=True, type='mesh')
                if meshes:
                    # ready to publish
                    # generate path
                    publish_path = os.path.join(publish_folder, res + '.mb')
                    # add to publish_grps
                    publish_grps.update({res: [res_grp, publish_path]})
                    # add publish info
                    publish_info['resolution'].append(res)
                    # add to return paths
                    model_paths_return.append(publish_path)
                else:
                    logger.warning('there is no mesh in {}, skipped'.format(res))
            else:
                logger.warning('there is no model group for {}, skipped'.format(res))
        # write publish info and publish models
        if publish_info['resolution']:
            # empty folder
            files_remove = files.get_files_from_path(publish_folder, exceptions=['__init__.py'], full_paths=True)
            for f in files_remove:
                try:
                    os.remove(f)
                except OSError as exc:
                    logger.error(exc)
                    return False

            # publish models
            for res, publish_data_info in publish_grps.iteritems():
                cmds.select(publish_data_info[0])
                cmds.file(publish_data_info[1], exportSelected=True, type='mayaBinary', preserveReferences=True)

            # write publish info
            publish_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            publish_info['comment'] = comment
            publish_info['date'] = publish_date
            publish_info_path = os.path.join(model_path, 'publish', PUBLISH_INFO_FILE)
            files.write_json_file(publish_info_path, publish_info)

            # log info
            publish_log = "published model {} - {} - {} successfully".format(project, asset, model_type)
            publish_log += "\nresolution: {}\ncomment: '{}'\ndate: {}".format(str(publish_info['resolution']), comment,
                                                                              publish_date)
            logger.info(publish_log)

            # version up
            versionize.version_up(os.path.join(model_path, 'publish'), comment=comment)

            # return
            return model_paths_return
        else:
            logger.error('there is no model to publish in the scene')
            return None
    else:
        logger.error('there is no model type {} for {} - {}, cannot publish the model'.format(model_type, project,
                                                                                              asset))
        return None


def import_model(model_type, asset, project, resolution=None):
    """
    import published model

    Args:
        model_type(str): model's type (body, costume, anatomy etc...)
        asset(str): asset name
        project(str): project name
    Keyword Args:
        resolution(list): model's resolution, will import all res if None

    Returns:
        model_grps(dict): imported model resolution groups
    """
    # check if model_type exist
    model_path = assets.get_model_path_from_asset(model_type, asset, project, warning=False)
    if model_path:
        # check if publish model
        publish_info_path = os.path.join(model_path, 'publish', PUBLISH_INFO_FILE)
        if os.path.exists(publish_info_path):
            # has published model, prepare to import models
            model_grps = {}
            namer_res = naming.Namer(type=naming.Type.group, side=naming.Side.middle, description=model_type, index=1)
            # get publish info data
            publish_info = files.read_json_file(publish_info_path)
            if not resolution:
                resolution = publish_info['resolution']

            for res in resolution:
                print res
                if res in publish_info['resolution']:
                    # resolution available
                    res_path = os.path.join(model_path, 'publish', res + '.mb')
                    cmds.file(res_path, i=True)
                    # res group
                    namer_res.resolution = res
                    model_grps.update({res: namer_res.name})
                    # log info
                    logger.info('import {} - {} - {} - {} successfully'.format(project, asset, model_type, res))
                else:
                    logger.warning('no published model for {} - {} - {} - {}, skipped'.format(project, asset,
                                                                                              model_type, res))
            return model_grps
        else:
            logger.warning('no publish model found for {} - {} - {}'.format(project, asset, model_type))
            return []
    else:
        logger.warning('model type {} does not exist for {} - {}'.format(model_type, project, asset))
        return []
