# IMPORT PACKAGES

# import os
import os

# import shutil
import shutil

# import utils
import files
import logUtils

# CONSTANT
import projects
PROJECTS_ROOT = os.path.dirname(projects.__file__)

logger = logUtils.logger


# FUNCTION
# project
def create_project(name):
    """
    create project folder, each project folder should contain assets folder and scripts folder

    Args:
        name(str): project name

    Returns:
        project_path(str): project folder's path, return None if error
    """
    # check if folder exist
    project_path = get_project_path(name, warning=False)
    if project_path:
        # skipped
        logger.warning('project: {} already exists, skipped'.format(name))
        return project_path
    else:
        try:
            project_path = os.path.join(PROJECTS_ROOT, name)
            # create project folder
            os.mkdir(project_path)

            # make folder for assets and scripts
            assets_path = os.path.join(project_path, 'assets')
            scripts_path = os.path.join(project_path, 'scripts')
            os.mkdir(assets_path)
            os.mkdir(scripts_path)

            # make tasks folder under scripts
            tasks_path = os.path.join(scripts_path, 'tasks')
            os.mkdir(tasks_path)

            # create init files
            _write_init_file_to_paths([project_path, assets_path, scripts_path, tasks_path])

        except OSError as exc:
            logger.error(exc)
            return None
        else:
            logger.info('project: {} has been created successfully at {}'.format(name, project_path))
            return project_path


def remove_project(name):
    """
    remove project folder

    Args:
        name(str): project name

    Returns:
        True/False
    """
    # check if folder exist
    project_path = get_project_path(name)
    if project_path:
        # try to remove folders
        try:
            shutil.rmtree(project_path)
        except OSError as exc:
            logger.error(exc)
            return False
        else:
            logger.info('project: {} has been removed successfully'.format(name))
            return True
    else:
        # folder doesn't exist
        return False


def rename_project(orig_name, update_name):
    """
    rename project folder

    Args:
        orig_name(str): project's original name
        update_name(str): project's update name

    Returns:
        project_path(str): project's folder's path, return None if not exist
    """
    # check if folder exist and no name clashing
    project_path_orig = get_project_path(orig_name, warning=False)
    project_path_update = get_project_path(update_name, warning=False)
    if project_path_orig and not project_path_update:
        # try to rename folder
        try:
            project_path_update = os.path.join(os.path.dirname(project_path_orig), update_name)
            os.rename(project_path_orig, project_path_update)
        except OSError as exc:
            logger.error(exc)
            return None
        else:
            logger.info('rename project {} to {} successfully'.format(orig_name, update_name))
            return project_path_update

    elif project_path_update:
        # name clash
        logger.warning('project {} already exists, skipped'.format(update_name))
        return None
    else:
        # original folder does not exist
        logger.warning('project {} does not exist, skipped'.format(orig_name))
        return None


def get_all_projects(full_path=False):
    """
    get all projects

    Keyword Args:
        full_path(bool): if return projects full path

    Returns:
        projects(list): projects names
    """
    projects = files.get_folders_from_path(PROJECTS_ROOT, full_path=full_path)
    return projects


def get_project_path(project, warning=True):
    """
    get given project folder's path

    Args:
        project(str): project's name

    Keyword Args:
        warning(bool): will warn if not exist, default is True

    Returns:
        project_path(str): project folder's path, return None if not exist
    """
    project_path = os.path.join(PROJECTS_ROOT, project)
    if os.path.exists(project_path):
        return project_path
    else:
        if warning:
            logger.warning('project {} does not exist'.format(project))
        return None


# asset
def create_asset(name, project):
    """
    create asset folder in project

    Args:
        name(str): asset name
        project(str): project name

    Returns:
        asset_path(str): asset's folder's path, return None if error
    """
    # check if project exist
    project_path = get_project_path(project, warning=False)
    if project_path:
        # check if asset exists
        asset_path = get_asset_path_from_project(name, project, warning=False)
        if asset_path:
            logger.warning('asset: {} already exists, skipped'.format(name))
            return None
        else:
            # project exists, create asset folder
            try:
                asset_path = os.path.join(project_path, 'assets', name)
                os.mkdir(asset_path)

                # create models and rigs folder under asset
                models_path = os.path.join(asset_path, 'models')
                rigs_path = os.path.join(asset_path, 'rigs')
                os.mkdir(models_path)
                os.mkdir(rigs_path)

                # create init files
                _write_init_file_to_paths([asset_path, models_path, rigs_path])

            except OSError as exc:
                logger.error(exc)
                return None
            else:
                logger.info('asset: {} has been created successfully at {}'.format(name, asset_path))
                return asset_path
    else:
        logger.warning('project {} does not exist'.format(project))
        return None


def remove_asset(name, project):
    """
    remove asset folder in project

    Args:
        name(str): asset name
        project(str): project name

    Returns:
        True/False
    """
    # check if project and asset exist
    asset_path = get_asset_path_from_project(name, project)
    if asset_path:
        # asset exists, remove it
        try:
            shutil.rmtree(asset_path)
        except OSError as exc:
            logger.error(exc)
            return False
        else:
            logger.info('asset: {} has been removed successfully'.format(name))
            return True
    else:
        return False


def rename_asset(orig_name, update_name, project):
    """
    rename asset folder in project

    Args:
        orig_name(str): asset's original name
        update_name(str): asset's update name
        project(str): project name

    Returns:
        asset_path(str): asset folder's path, return None if not exist
    """
    # check if project and asset exist
    project_path = get_project_path(project, warning=False)
    asset_path_orig = get_asset_path_from_project(orig_name, project, warning=False)
    asset_path_update = get_asset_path_from_project(update_name, project, warning=False)
    if asset_path_orig and not asset_path_update:
        # asset exists, rename
        try:
            asset_path_update = os.path.join(os.path.dirname(asset_path_orig), update_name)
            os.rename(asset_path_orig, asset_path_update)
        except OSError as exc:
            logger.error(exc)
            return None
        else:
            logger.info('rename asset {} to {} successfully'.format(orig_name, update_name))
            return asset_path_update
    elif asset_path_update:
        logger.warning('asset {} already exists, skipped'.format(update_name))
        return None
    elif not asset_path_orig and project_path:
        # asset does not exist, project exists
        logger.warning('asset {} does not exist, skipped'.format(orig_name))
        return None
    else:
        # project does not exists
        logger.warning('project {} does not exist, skipped'.format(project))
        return None


def get_all_assets_from_project(project, full_path=False):
    """
    get all assets names from given project

    Args:
        project(str): project name

    Keyword Args:
        full_path(str): if return asset folder's full path

    Returns:
        assets(list): assets names, return [] if project does not exist
    """
    # check if project exists
    project_path = get_project_path(project, warning=False)
    if project_path:
        project_path = os.path.join(project_path, 'assets')
        # get all assets
        assets = files.get_folders_from_path(project_path, full_path=full_path)
        return assets
    else:
        # project does not exist
        return []


def get_asset_path_from_project(asset, project, warning=True):
    """
    get given asset folder path from given project

    Args:
        asset(str): asset name
        project(str): project name

    Keyword Args:
        warning(bool): will warn if asset not exist

    Returns:
        asset_path(str): asset folder's path, return None if not exist
    """
    # check if project and asset exist
    project_path = get_project_path(project, warning=warning)
    if project_path:
        asset_path = os.path.join(project_path, 'assets', asset)
        if os.path.exists(asset_path):
            # asset exists
            return asset_path
        elif project_path:
            # project exists, asset not
            if warning:
                logger.warning('asset {} does not exist'.format(asset))
            return None
    else:
        # project does not exist
        return None


# rig
def create_rig(rig_type, asset, project):
    """
    create given type of rig under asset
    each rig type folder should contain 'build', 'data', 'wip' and 'publish'

    Args:
        rig_type(str): rig's type (animationRig, deformationRig, muscleRig, costumeRig etc..)
        asset(str): asset name
        project(str): project name

    Returns:
        rig_path(str): rig type folder's path
    """
    # check if asset folder exist
    asset_path = get_asset_path_from_project(asset, project, warning=False)
    if asset_path:
        # check if rig type exist
        rig_path = get_rig_path_from_asset(rig_type, asset, project, warning=False)
        if rig_path:
            # exist
            logger.warning('rig type: {} already exists, skipped'.format(rig_type))
            return None
        else:
            # asset exists, create rig type folder
            try:
                rig_path = os.path.join(asset_path, 'rigs', rig_type)
                os.mkdir(rig_path)
                # create sub folders under rig type
                build_path = os.path.join(rig_path, 'build')
                data_path = os.path.join(rig_path, 'data')
                wip_path = os.path.join(rig_path, 'wip')
                publish_path = os.path.join(rig_path, 'publish')
                os.mkdir(build_path)
                os.mkdir(data_path)
                os.mkdir(wip_path)
                os.mkdir(publish_path)

                # create init files
                _write_init_file_to_paths([rig_path, build_path, data_path, wip_path, publish_path])

            except OSError as exc:
                logger.error(exc)
                return None
            else:
                logger.info('rig type: {} has been created successfully at {}'.format(rig_type, rig_path))
                return rig_path
    else:
        # check project path
        project_path = get_project_path(project, warning=False)
        if project_path:
            # asset not exist
            logger.warning('asset {} does not exist, skipped'.format(asset))
            return None
        else:
            logger.warning('project {} does not exist, skipped'.format(project))
            return None


def remove_rig(rig_type, asset, project):
    """
    remove rig type from asset

    Args:
        rig_type(str): rig's type (animationRig, deformationRig, muscleRig, costumeRig etc..)
        asset(str): asset name
        project(str): project name

    Returns:
        True/False
    """
    # check if rig type exist
    rig_path = get_rig_path_from_asset(rig_type, asset, project)
    if rig_path:
        # rig type exists, remove it
        try:
            shutil.rmtree(rig_path)
        except OSError as exc:
            logger.error(exc)
            return False
        else:
            logger.info('rig type: {} has been removed successfully'.format(rig_type))
            return True
    else:
        return False


def get_all_rig_from_asset(asset, project, full_path=False):
    """
    get all rig types names from given asset

    Args:
        asset(str): asset name
        project(str): project name

    Keyword Args:
        full_path(str): if return asset folder's full path

    Returns:
        rig_types(list): rig types names, return [] if asset/project does not exist
    """
    asset_path = get_asset_path_from_project(asset, project, warning=False)
    if asset_path:
        asset_path = os.path.join(asset_path, 'rigs')
        # asset exist
        rig_types = files.get_folders_from_path(asset_path, full_path=full_path)
        return rig_types
    else:
        # asset/project not exist
        return []


def get_rig_path_from_asset(rig_type, asset, project, warning=True):
    """
    get rig type folder path from asset

    Args:
        rig_type(str): rig's type (animationRig, deformationRig, muscleRig, costumeRig etc..)
        asset(str): asset name
        project(str): project name

    Keyword Args:
        warning(bool): will warn if rig type not exist, default is True

    Returns:
        rig_path(str): rig type folder's path, return None if not exist
    """
    # check if asset exist
    asset_path = get_asset_path_from_project(asset, project, warning=warning)
    if asset_path:
        # check if rig type exist
        rig_path = os.path.join(asset_path, 'rigs', rig_type)
        if os.path.exists(rig_path):
            return rig_path
        else:
            # not exist
            if warning:
                logger.warning('rig type {} does not exist'.format(rig_type))
            return None
    else:
        return None


# SUB FUNCTION
def _write_init_file_to_paths(paths):
    """
    write __init__.py to given paths

    Args:
        paths(list): list of given paths
    """
    for p in paths:
        init_path = os.path.join(p, '__init__.py')
        files.write_python_file(init_path, '')
