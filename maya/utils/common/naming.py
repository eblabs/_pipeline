# IMPORT PACKAGES

# import system packages
import sys
import os

# import re
import re

# import utils
import files
import variables
import logUtils

# CONSTANT
import config
FILE_CONFIG = os.path.join(os.path.dirname(config.__file__), 'NAME_CONVENTION.cfg')
DATA_CONFIG = files.read_json_file(FILE_CONFIG)

DATA_INVERSE = {}
for key, item in DATA_CONFIG.iteritems():
    DATA_INVERSE.update({key: {v: k for k, v in item.iteritems()}})

logger = logUtils.logger


#  CLASS
class Type(object):
    """Type class to access type variables"""
    def __init__(self):
        pass


class Side(object):
    """Side class to access side variables"""
    def __init__(self):
        pass


class Resolution(object):
    """Resolution class to access resolution variables"""
    def __init__(self):
        pass


# add static attrs for above classes base on dictionary
for key, item in DATA_CONFIG.iteritems():
    Obj = getattr(sys.modules[__name__], key.title())
    for nameLong, nameShort in item.iteritems():
        setattr(Obj, nameLong, nameShort)
    setattr(Obj, 'all', item.keys())


class Namer(object):
    """
    class to compose/decompose name base on naming convention

    """

    # shortcuts for inputs
    shortcuts = {'type':        't',
                 'side':        's',
                 'resolution':  'res',
                 'description': 'des',
                 'index':       'i',
                 'suffix':      'sfx'}

    def __init__(self, *args, **kwargs):
        """
        Args:
            name(str): decompose the given name

        Keyword Args:
            compose name with given parts

            type/t(str): name's type
            side/s(str): name's side
            resolution/res(str): name's resolution
            description/des(str): name's description
            index/i(str): name's index
            suffix/sfx(str): name's suffix

        Properties:
            type/t(str)
            side/s(str)
            resolution/res(str)
            description/des(str)
            index/i(str)
            suffix/sfx(str)
            name(str)
        """

        self._name = ''
        self._type = None
        self._side = None
        self._resolution = None
        self._description = None
        self._index = None
        self._suffix = None

        if args:
            self._decompose_name(args[0])
        else:
            for key_long, key_short in self.shortcuts.iteritems():
                val = variables.kwargs(key_long, None, kwargs, short_name=key_short)
                setattr(self, '_'+key_long, val)

            if not isinstance(self._index, int) or self._index < 0:
                self._index = None

            if not isinstance(self._suffix, int) or self._suffix < 0:
                self._suffix = None

            self._compose_name()

    # property
    @property
    def type(self):
        return self._get_name(self._type,
                              'type',
                              return_type='long')

    @property
    def t(self):
        return self._get_name(self._type,
                              'type',
                              return_type='long')

    @property
    def side(self):
        return self._get_name(self._side,
                              'side',
                              return_type='long')

    @property
    def s(self):
        return self._get_name(self._side,
                              'side',
                              return_type='long')

    @property
    def resolution(self):
        return self._get_name(self._resolution,
                              'resolution',
                              return_type='long')

    @property
    def res(self):
        return self._get_name(self._resolution,
                              'resolution',
                              return_type='long')

    @property
    def description(self):
        return self._description

    @property
    def des(self):
        return self._description

    @property
    def index(self):
        return self._index

    @property
    def i(self):
        return self._index

    @property
    def suffix(self):
        return self._suffix

    @property
    def sfx(self):
        return self._suffix

    @property
    def name(self):
        self._compose_name()
        return self._name

    # set attrs
    @type.setter
    def type(self, key_value):
        self._type = self._get_name(key_value,
                                    'type',
                                    return_type='long')

    @t.setter
    def t(self, key_value):
        self._type = self._get_name(key_value,
                                    'type',
                                    return_type='long')

    @side.setter
    def side(self, key_value):
        self._side = self._get_name(key_value,
                                    'side',
                                    return_type='long')

    @s.setter
    def s(self, key_value):
        self._side = self._get_name(key_value,
                                    'side',
                                    return_type='long')

    @resolution.setter
    def resolution(self, key_value):
        self._resolution = self._get_name(key_value,
                                          'resolution',
                                          return_type='long')

    @res.setter
    def res(self, key_value):
        self._resolution = self._get_name(key_value,
                                          'resolution',
                                          return_type='long')

    @description.setter
    def description(self, key_value):
        if key:
            self._description = key_value
        else:
            self._description = None

    @des.setter
    def des(self, key_value):
        if key:
            self._description = key_value
        else:
            self._description = None

    @index.setter
    def index(self, num):
        if isinstance(num, int) and num >= 0:
            self._index = int(num)
        else:
            self._index = None

    @i.setter
    def i(self, num):
        if isinstance(num, int) and num >= 0:
            self._index = int(num)
        else:
            self._index = None

    @suffix.setter
    def suffix(self, num):
        if isinstance(num, int) and num >= 0:
            self._suffix = int(num)
        else:
            self._suffix = None

    @sfx.setter
    def sfx(self, num):
        if isinstance(num, int) and num >= 0:
            self._suffix = int(num)
        else:
            self._suffix = None

    def _decompose_name(self, name):
        """
        decompose name to get each parts name individually

        Args:
            name(str): name for decompose

        Returns:
            self._type(str): name's type
            self._side(str): name's side
            self._resolution(str): name's resolution
            self._description(str): name's description
            self._index(str): name's index
            self._suffix(str): name's suffix
        """
        self._type = None
        self._side = None
        self._resolution = None
        self._description = None
        self._index = None
        self._suffix = None

        name_split = name.split('_')  # split name parts by '_'

        split_num = len(name_split)  # check how many parts

        self._type = self._get_name(name_split[0], 'type', return_type='long')

        if not self._type:
            logger.error('Type is invalid')

        if split_num > 2:
            self._side = self._get_name(name_split[1], 'side', return_type='long')
            if not self._side:
                logger.error('Side is invalid')

            if split_num == 3:
                # name only contains type side and des
                self._description = name_split[2]

            elif split_num == 4:
                # name contains type side des and res/index
                self._resolution = self._get_name(name_split[2], 'resolution', return_type='long')
                if self._resolution:
                    self._description = name_split[3]
                else:
                    self._description = name_split[2]
                    self._index = int(name_split[3])

            elif split_num == 5:
                # name contains type side des index and res/suffix
                self._resolution = self._get_name(name_split[2], 'resolution', return_type='long')
                if self._resolution:
                    self._description = name_split[3]
                    self._index = int(name_split[4])
                else:
                    self._description = name_split[2]
                    self._index = int(name_split[3])
                    self._suffix = int(name_split[4])

            elif split_num == 6:
                # name contains type side res des index and suffix
                self._resolution = self._get_name(name_split[2], 'resolution', return_type='long')
                if not self._resolution:
                    logger.error('Resolution is invalid')
                self._description = name_split[3]
                self._index = name_split[4]
                self._suffix = name_split[5]

            else:
                logger.error('{} is invalid'.format(name))

        elif split_num == 2:
            logger.error('{} is invalid'.format(name))

    def _compose_name(self):
        """
        compose name with given parts
        pattern: type_side_(resolution)_part_index_suffix

        Args:
            self._type(str): name's type
            self._side(str): name's side
            self._resolution(str): name's resolution
            self._description(str): name's description
            self._index(str): name's index
            self._suffix(str): name's suffix

        Returns:
            self._name(str): composed name
        """
        self._name = ''

        if self._type:
            # check if the name has side and des
            if self._side and self._description:
                for key_value, key_type in zip([self._type, self._side, self._resolution],
                                               ['type', 'side', 'resolution']):
                    if key_value:
                        key_value = self._get_name(key_value, key_type, return_type='short')
                        self._name += (key_value + '_')

                self._name += (self._description+'_')

                for i in [self._index, self._suffix]:
                    if i is not None:
                        self._name += '{:03d}_'.format(int(i))

                self._name = self._name[:-1]  # remove the last '_'

            else:
                # name only contains type ('master')
                self._name = self._get_name(self._type, 'type', return_type='short')

        else:
            # the name is invalid, should at least has type
            logger.error('Name is invalid, should at least has Type')

    @staticmethod
    def _get_name(key_value, key_type, return_type='short'):
        """
        get the name from the NAME_CONVENTION config file

        Args:
            key_value(str): naming's type's name ('group'/'jnt' etc..)
            key_type(str): naming's type ('type'/'resolution'/'side')
            return_type(str): short/long, return the short name or full name

        Returns:
            name(str): name from the NAME_CONVENTION config file
        """
        if key_value in DATA_CONFIG[key_type]:
            long_name = key_value
            short_name = DATA_CONFIG[key_type][key_value]

        elif key_value in DATA_INVERSE[key_type]:
            long_name = DATA_INVERSE[key_type][key_value]
            short_name = key_value
        else:
            long_name = None
            short_name = None

        if return_type == 'short':
            name = short_name
        else:
            name = long_name

        return name


# functions
def update_name(name, **kwargs):
    """
    update name's parts

    Args:
        name(str)

    Keyword Args:
        type/t(str): name's type
        side/s(str): name's side
        resolution/res(str): name's resolution
        description/des(str): name's description
        index/i(str): name's index
        suffix/sfx(str): name's suffix

    Returns:
        name_update(str)
    """
    # because some parts can be removed when setting to None, like resolution and index, we set -1 as default to skip
    _type = variables.kwargs('type', -1, kwargs, short_name=Namer.shortcuts['type'])
    _side = variables.kwargs('side', -1, kwargs, short_name=Namer.shortcuts['side'])
    _res = variables.kwargs('resolution', -1, kwargs, short_name=Namer.shortcuts['resolution'])
    _des = variables.kwargs('description', -1, kwargs, short_name=Namer.shortcuts['description'])
    _index = variables.kwargs('index', -1, kwargs, short_name=Namer.shortcuts['index'])
    _suffix = variables.kwargs('suffix', -1, kwargs, short_name=Namer.shortcuts['suffix'])

    namer = Namer(name)

    # check each part
    if _type != -1:
        namer.type = _type
    if _side != -1:
        namer.side = _side
    if _res != -1:
        namer.resolution = _res
    if _des != -1:
        namer.description = _des
    if _index != -1:
        namer.index = _index
    if _suffix != -1:
        namer._suffix = _suffix

    return namer.name


def convert_camel_case(name, output_format='snake_case'):
    """
    get function from stackoverflow
    https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    if output_format == 'snake_case':
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name_convert = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    elif output_format == 'lowercase_space':
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        name_convert = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower()
    else:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        name_convert = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).upper()
    return name_convert


def convert_snake_case_to_camel_case(name):
    """
    get function from stackoverflow
    https://stackoverflow.com/questions/4303492/how-can-i-simplify-this-conversion-from-underscore-to-camelcase-in-python
    """
    def camelcase():
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    name = convert_camel_case(name, output_format='snake_case')
    return "".join(c.next()(x) if x else '_' for x in name.split("_"))