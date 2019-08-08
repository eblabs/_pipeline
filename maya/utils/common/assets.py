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
PROJECTS_ROOT = projects.__file__

logger = logUtils.get_logger(name='assets', level='info')


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
    project_path = os.path.join(PROJECTS_ROOT, name)
    if os.path.exists(project_path):
        # skipped
        logger.warning('project: {} already exists, skipped'.format(name))
        return project_path
    else:
        try:
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
    project_path = os.path.join(PROJECTS_ROOT, name)
    if os.path.exists(project_path):
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
        logger.warning('project: {} does not exist, skipped'.format(name))
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
    project_path_orig = os.path.join(PROJECTS_ROOT, orig_name)
    project_path_update = os.path.join(PROJECTS_ROOT, update_name)
    if os.path.exists(project_path_orig) and not os.path.exists(project_path_update):
        # try to rename folder
        try:
            os.rename(project_path_orig, project_path_update)
        except OSError as exc:
            logger.error(exc)
            return None
        else:
            logger.info('rename project {} to {} successfully'.format(orig_name, update_name))
            return project_path_update

    elif os.path.exists(project_path_update):
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


def get_project_path(project):
    """
    get given project folder's path

    Args:
        project(str): project's name

    Returns:
        project_path(str): project folder's path, return None if not exist
    """
    project_path = os.path.join(PROJECTS_ROOT, project)
    if os.path.exists(project_path):
        return project_path
    else:
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
    project_path = os.path.join(PROJECTS_ROOT, project)
    if os.path.exists(project_path):
        # project exists, create asset folder
        try:
            asset_path = os.path.join(project_path, 'assets', name)
            os.mkdir(asset_path)
            # create models and rigs folder under asset
            models_path = os.path.join(asset_path, 'models')
            rigs_path = os.path.join(asset_path, 'rigs')
            os.mkdir(models_path)
            os.mkdir(rigs_path)

        except OSError as exc:
            logger.error(exc)
            return None
        else:
            logger.info('asset: {} has been created successfully at {}'.format(name, asset_path))
            return asset_path
    else:
        # project not exists
        logger.warning('project {} does not exist, skipped'.format(project))
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
    project_path = os.path.join(PROJECTS_ROOT, project)
    asset_path = os.path.join(project_path, 'assets', name)
    if os.path.exists(asset_path):
        # asset exists, remove it
        try:
            shutil.rmtree(asset_path)
        except OSError as exc:
            logger.error(exc)
            return False
        else:
            logger.info('asset: {} has been removed successfully'.format(name))
            return True
    elif os.path.exists(project_path):
        # project exists, asset not
        logger.warning('asset {} does not exist, skipped'.format(name))
        return False
    else:
        # project does not exist
        logger.warning('project {} does not exist, skipped'.format(project))
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
    project_path = os.path.join(PROJECTS_ROOT, project)
    asset_path_orig = os.path.join(project_path, 'assets', orig_name)
    asset_path_update = os.path.join(project_path, 'assets', update_name)
    if os.path.exists(asset_path_orig) and not os.path.exists(asset_path_update):
        # asset exists, rename
        try:
            os.rename(asset_path_orig, asset_path_update)
        except OSError as exc:
            logger.error(exc)
            return None
        else:
            logger.info('rename asset {} to {} successfully'.format(orig_name, update_name))
            return asset_path_update
    elif os.path.exists(asset_path_update):
        logger.warning('asset {} already exists, skipped'.format(update_name))
        return None
    elif not os.path.exists(asset_path_orig) and os.path.exists(project_path):
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
        assets(list): assets names, return None if project does not exist
    """
    # check if project exists
    project_path = os.path.join(PROJECTS_ROOT, project, 'assets')
    if os.path.exists(project_path):
        # get all assets
        assets = files.get_folders_from_path(project_path, full_path=full_path)
        return assets
    else:
        # project does not exist
        logger.warning('project: {} does not exist'.format(project))
        return None


def get_asset_path_from_project(asset, project):
    """
    get given asset folder path from given project

    Args:
        asset(str): asset name
        project(str): project name

    Returns:
        asset_path(str): asset folder's path, return None if not exist
    """
    # check if project and asset exist
    project_path = os.path.join(PROJECTS_ROOT, project)
    asset_path = os.path.join(project_path, 'assets', asset)
    if os.path.exists(asset_path):
        # asset exists
        return asset_path
    elif os.path.exists(project_path):
        # project exists, asset not
        logger.warning('asset {} does not exist'.format(asset))
        return None
    else:
        # project does not exist
        logger.warning('project {} does not exist'.format(project))
        return None
