# IMPORT PACKAGES

# import os
import os

# import utils
import utils.common.assets as assets
import utils.common.logUtils as logUtils

# CONSTANT
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
        builder_path(str): build script's path, return None if not exist
    """
    # get rig path
    rig_path = assets.get_rig_path_from_asset(rig_type, asset, project, warning=warning)
    if rig_path:
        # rig exists, check if has builder
        builder_path = os.path.join(rig_path, 'build', 'build.py')
        if os.path.exists(builder_path):
            # get python path
            builder_path = '{}.assets.{}.rigs.{}.build.build'.format(project, asset, rig_type)
            return builder_path
        else:
            # builder not exists
            if warning:
                logger.warning("asset {}'s rig {} doesn't have a build script file".format(asset, rig_type))
            return None
    else:
        return None
