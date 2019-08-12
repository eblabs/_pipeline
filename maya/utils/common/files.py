# IMPORT PACKAGES

# import system packages
import os

# import python packages
import json
import cPickle

# import compiled packages
import numpy


# FUNCTION
def write_json_file(path, data):
    """
    write data to the given path as json file

    Args:
        path(str): given path
        data(dict/list): given data
    """

    outfile = open(path, 'w')
    json.dump(data, outfile, indent=4, sort_keys=True)
    outfile.close()


def read_json_file(path):
    """
    read data from the given json file path

    Args:
        path(str): given json file path

    Returns:
        data(dict/list): data from json file
    """

    infile = open(path, 'r')
    data = json.load(infile)
    infile.close()
    return data


def write_python_file(path, data):
    """
    write data to the given path as python file

    Args:
        path(str): given path
        data(dict/list): given data
    """
    outfile = open(path, 'w')
    if data:
        outfile.write(data)
    outfile.close()


def write_cPickle_file(path, data):
    """
    write data to the given path as cPickle file

    Args:
        path(str): given path
        data(dict/list): given data
    """

    outfile = open(path, 'wb')
    cPickle.dump(data, outfile, cPickle.HIGHEST_PROTOCOL)
    outfile.close()


def read_cPickle_file(path):
    """
    read data from the given cPickle file path

    Args:
        path(str): given cPickle file path

    Returns:
        data(dict/list): data from cPickle file
    """

    infile = open(path, 'rb')
    data = cPickle.load(infile)
    infile.close()
    return data


def write_numpy_file(path, data):
    """
    write data to the given path as numpy file

    Args:
        path(str): given path
        data(dict/list): given data
    """

    numpy.save(path, data)


def read_numpy_file(path):
    """
    read data from the given numpy file path

    Args:
        path(str): given numpy file path

    Returns:
        data(array): numpy array from the numpy file
    """

    data = numpy.load(path)
    return data


def get_files_from_path(path, extension=None, exceptions=None, full_paths=True):
    """
    get files from the given path

    Args:
        path(str): given path
        extension(list/str): specific extension
        exceptions(list/str): skip if worlds in exceptions
        full_paths(bool): return full path or just file name, default is True

    Returns:
        file_paths(list): all files path
    """

    files = os.listdir(path)
    file_paths = []

    if isinstance(extension, basestring):
        extension = [extension]
    if isinstance(exceptions, basestring):
        exceptions = [exceptions]

    if files:
        for f in files:
            path_file = os.path.join(path, f)
            if os.path.isfile(path_file):
                ext = os.path.splitext(path_file)[-1].lower()
                if ext in extension or not extension:
                    # check exceptions
                    add = True
                    for exp in exceptions:
                        if exp in f:
                            add = False
                            break
                    if add:
                        if full_paths:
                            file_paths.append(path_file)
                        else:
                            file_paths.append(f)
    return file_paths


def get_folders_from_path(path, full_path=True):
    """
    get folders from the given path

    Args:
        path(str): given path

    Keyword Args:
        full_path(bool): if return the full path

    Returns:
        folder(list): all folders/all folders paths
    """

    all_files = os.listdir(path)

    folders = []

    for f in all_files:
        path_file = os.path.join(path, f)
        if os.path.isdir(path_file):
            # check if folder
            if full_path:
                folders.append(path_file)
            else:
                folders.append(f)

    return folders
