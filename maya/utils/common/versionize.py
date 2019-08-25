# IMPORT PACKAGES

# import os
import os

# import datetime
import datetime

# import shutil
import shutil

# import utils
import utils.common.logUtils as logUtils
import utils.common.files as files

# CONSTANT
logger = logUtils.logger
VERSION_LIMIT = 20
VERSION_FILE = 'version_info.versionize'
VERSION_FOLDER = 'versions'
VERSION_INFO_TEMPLATE = {'version': 1, 'comment': '', 'date': ''}


# FUNCTION
def version_set_up(path):
    """
    set up version folders

    Args:
        path(str): given path
    """
    # check if has version folder
    version_folder_path = os.path.join(path, VERSION_FOLDER)
    if not os.path.exists(version_folder_path):
        # set up folders and files
        # create folder
        os.mkdir(version_folder_path)
        # create version file
        version_file_path = os.path.join(version_folder_path, VERSION_FILE)
        files.write_json_file(version_file_path, [])
        # log info
        logger.info('set up versionize for {} successfully'.format(path))
    else:
        logger.warning('given path {} already has versionize set up, skipped'.format(path))


def version_up(path, comment=''):
    """
    version up current files in path

    Args:
        path(str): given path
    Keyword Args:
        comment(str): given comment
    """
    # check files in path
    files_version = files.get_files_from_path(path, full_paths=False)
    # get version folder path
    version_folder_path = os.path.join(path, VERSION_FOLDER)
    if files_version:
        # have file to be versioned up
        if not os.path.exists(version_folder_path):
            # version set up doesn't exist, set up
            version_set_up(path)
        # get version info
        version_file_path = os.path.join(version_folder_path, VERSION_FILE)
        version_info = files.read_json_file(version_file_path)
        version_add = 1  # version count starts at 1
        if version_info:
            version_add = version_info[0]['version'] + 1
        # add version folder
        version_latest_path = os.path.join(version_folder_path, 'version_{:03d}'.format(version_add))
        os.mkdir(version_latest_path)
        # copy files to version folder
        for f in files_version:
            shutil.copyfile(os.path.join(path, f), os.path.join(version_latest_path, f))
        # append version info
        version_info_latest = VERSION_INFO_TEMPLATE.copy()
        version_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version_info_latest['version'] = version_add
        version_info_latest['comment'] = comment
        version_info_latest['date'] = version_date
        version_info.insert(0, version_info_latest)
        # check version limitation
        if len(version_info) > VERSION_LIMIT:
            for version_info_remove in version_info[VERSION_LIMIT:]:
                # get version
                version_remove = version_info_remove['version']
                # remove folder and files inside
                shutil.rmtree(os.path.join(version_folder_path, 'version_{:03d}'.format(version_remove)))
            version_info = version_info[:VERSION_LIMIT]
        # override version info file
        files.write_json_file(version_file_path, version_info)
        # log info
        logger.info("version: {}\ncomment: '{}'\ndate: {}".format(version_add, comment, version_date))
    else:
        logger.warning('no file to be versioned up at {}, skipped'.format(path))


