# IMPORT PACKAGES

# import os
import os

# import utils
import utils.common.assets as assets
import utils.common.logUtils as logUtils

# CONSTANT
import config.BUILD_TEMPLATE as BUILD_TEMPLATE
infile = open(BUILD_TEMPLATE.__file__, 'r')
BUILD_TEMPLATE = infile.read()
infile.close()

logger = logUtils.get_logger(name='assets', level='info')


# FUNCTION
def get_builder(rig_type, asset, project, warning=True):
    """
    get build script from given rig

    Args:
        rig_type(str): rig's type (animationRig, deformationRig, muscleRig, costumeRig etc..)
        asset(str): asset name
        project(str): project name

    Keyword Args:
        warning(bool): will warn if build script not exist, default is True

    Returns:
        builder_path(str): build script's python path, return None if not exist
    """
    # get rig path
    rig_path = assets.get_rig_path_from_asset(rig_type, asset, project, warning=warning)
    if rig_path:
        # rig exists, check if has builder
        builder_path = os.path.join(rig_path, 'build', 'builder.py')
        if os.path.exists(builder_path):
            # get python path
            builder_path = 'projects.{}.assets.{}.rigs.{}.build.builder'.format(project, asset, rig_type)
            return builder_path
        else:
            # builder not exists
            if warning:
                logger.warning("asset {}'s rig {} doesn't have a build script file".format(asset, rig_type))
            return None
    else:
        return None


def get_builder_path(rig_type, asset, project, warning=True):
    """
    get build script path from given rig

    Args:
        rig_type(str): rig's type (animationRig, deformationRig, muscleRig, costumeRig etc..)
        asset(str): asset name
        project(str): project name

    Keyword Args:
        warning(bool): will warn if given rig type not exist, default is True

    Returns:
        builder_path(str): build script's os path, return None if given rig type not exist
    """
    # get rig path
    rig_path = assets.get_rig_path_from_asset(rig_type, asset, project, warning=warning)
    if rig_path:
        # rig exists
        builder_path = os.path.join(rig_path, 'build', 'builder.py')
        return builder_path
    else:
        return None


def generate_builder(rig_type, asset, project, builder_inherit_path):
    """
    generate build script for given asset's rig type

    Args:
        rig_type(str): rig's type (animationRig, deformationRig, muscleRig, costumeRig etc..)
        asset(str): asset name
        project(str): project name
        builder_inherit_path(str): inherited build script's python path

    Returns:
        builder_path(str): generated build script's python path
    """
    # check if args in correct format
    if not rig_type or not asset or not project or not builder_inherit_path:
        logger.error("input arg is invalid, can't generate builder")
        return None

    # get build script file path, and check if rig type exist
    builder_path = get_builder_path(rig_type, asset, project, warning=True)
    if not builder_path:
        # given rig type does not exist
        return None

    # remove template docstring
    template = BUILD_TEMPLATE[5:]
    template = template[:-4]

    # get args in docstring
    rig_type_docs = "'{}'".format(rig_type)
    asset_docs = "'{}'".format(asset)
    project_docs = "'{}'".format(project)
    builder_inherit_path_docs = "'{}'".format(builder_inherit_path)

    # replace keywords with args
    builder = template
    for input_arg, temp_keyword in zip([rig_type_docs, asset_docs, project_docs, builder_inherit_path_docs],
                                       ['TEMP_RIG_TYPE_NAME', 'TEMP_ASSET_NAME', 'TEMP_PROJECT_NAME',
                                        'TEMP_BUILDER_PATH']):
        builder = builder.replace(temp_keyword, input_arg)

    # write file
    outfile = open(builder_path, 'w')
    outfile.write(builder)
    outfile.close()

    logger.info('create builder successfully for {} - {} - {} at {}'.format(project, asset, rig_type, builder_path))

    # get builder python path
    builder_path = 'projects.{}.assets.{}.rigs.{}.build.builder'.format(project, asset, rig_type)

    return builder_path


def get_data_path(data_name, rig_type, asset, project, warning=True, check_exist=True):
    """
    get given data folder path in the given rig

    Args:
        data_name(str): data folder's name
        rig_type(str): rig's type (animationRig, deformationRig, muscleRig, costumeRig etc..)
        asset(str): asset name
        project(str): project name

    Keyword Args:
        warning(bool): will warn if given data folder not exist, default is True
        check_exist(bool): if False will return the path even the data folder does not exist
                           (it will still return None if rig does not exist)
                           default is True

    Returns:
        data_path(str): data folder's os path, return None if not exist
    """
    # get rig path
    rig_path = assets.get_rig_path_from_asset(rig_type, asset, project, warning=warning)
    if rig_path:
        # data folder path
        data_path = os.path.join(rig_path, 'data', data_name)
        if check_exist and not os.path.exists(data_path):
            if warning:
                logger.warning("asset {}'s rig {} doesn't have given data folder {}".format(asset, rig_type, data_name))
            return None
        else:
            return data_path
    else:
        return  None
