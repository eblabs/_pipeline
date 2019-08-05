# IMPORT PACKAGES

# import system packages
import sys
import os

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

logger = logUtils.get_logger(name='naming', level='info')


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

            type/typ(str): name's type
            side/sid(str): name's side
            resolution/res(str): name's resolution
            description/des(str): name's description
            index/idx(str): name's index
            suffix/sfx(str): name's suffix

        Properties:
            type/typ(str)
            side/sid(str)
            resolution/res(str)
            description/des(str)
            index/idx(str)
            suffix/sfx(str)
            name(str)
        """

        self.__name = ''
        self.__type = None
        self.__side = None
        self.__resolution = None
        self.__description = None
        self.__index = None
        self.__suffix = None

        if args:
            self.__decompose_name(args[0])
        else:
            for key_long, key_short in self.shortcuts.iteritems():
                val = variables.kwargs(key_long, None, kwargs, short_name=key_short)
                setattr(self, '__'+key_long, val)

            self.__compose_name()

    # property
    @property
    def type(self):
        return self.__get_name(self.__type,
                               'type',
                               return_type='long')

    @property
    def typ(self):
        return self.__get_name(self.__type,
                               'type',
                               return_type='long')

    @property
    def side(self):
        return self.__get_name(self.__side,
                               'side',
                               return_type='long')

    @property
    def sid(self):
        return self.__get_name(self.__side,
                               'side',
                               return_type='long')

    @property
    def resolution(self):
        return self.__get_name(self.__resolution,
                               'resolution',
                               return_type='long')

    @property
    def res(self):
        return self.__get_name(self.__resolution,
                               'resolution',
                               return_type='long')

    @property
    def description(self):
        return self.__description

    @property
    def des(self):
        return self.__description

    @property
    def index(self):
        return self.__index

    @property
    def idx(self):
        return self.__index

    @property
    def suffix(self):
        return self.__suffix

    @property
    def sfx(self):
        return self.__suffix

    @property
    def name(self):
        self.__compose_name()
        return self.__name

    # set attrs
    @type.setter
    def type(self, key_value):
        self.__type = self.__get_name(key_value,
                                      'type',
                                      return_type='long')

    @typ.setter
    def typ(self, key_value):
        self.__type = self.__get_name(key_value,
                                      'type',
                                      return_type='long')

    @side.setter
    def side(self, key_value):
        self.__side = self.__get_name(key_value,
                                      'side',
                                      return_type='long')

    @sid.setter
    def sid(self, key_value):
        self.__side = self.__get_name(key_value,
                                      'side',
                                      return_type='long')

    @resolution.setter
    def resolution(self, key_value):
        self.__resolution = self.__get_name(key_value,
                                            'resolution',
                                            return_type='long')

    @res.setter
    def res(self, key_value):
        self.__resolution = self.__get_name(key_value,
                                            'resolution',
                                            return_type='long')

    @description.setter
    def description(self, key_value):
        if key:
            self.__description = key_value
        else:
            self.__description = None

    @des.setter
    def des(self, key_value):
        if key:
            self.__description = key_value
        else:
            self.__description = None

    @index.setter
    def index(self, num):
        if isinstance(num, int) and num >= 0:
            self.__index = int(num)
        else:
            self.__index = None

    @idx.setter
    def idx(self, num):
        if isinstance(num, int) and num >= 0:
            self.__index = int(num)
        else:
            self.__index = None

    @suffix.setter
    def suffix(self, num):
        if isinstance(num, int) and num >= 0:
            self.__suffix = int(num)
        else:
            self.__suffix = None

    @sfx.setter
    def sfx(self, num):
        if isinstance(num, int) and num >= 0:
            self.__suffix = int(num)
        else:
            self.__suffix = None

    def __decompose_name(self, name):
        """
        decompose name to get each parts name individually

        Args:
            name(str): name for decompose

        Returns:
            self.__type(str): name's type
            self.__side(str): name's side
            self.__resolution(str): name's resolution
            self.__description(str): name's description
            self.__index(str): name's index
            self.__suffix(str): name's suffix
        """
        self.__type = None
        self.__side = None
        self.__resolution = None
        self.__description = None
        self.__index = None
        self.__suffix = None

        name_split = name.split('_')  # split name parts by '_'

        split_num = len(name_split)  # check how many parts

        self.__type = self.__get_name(name_split[0], 'type', return_type='long')

        if not self.__type:
            logger.error('Type is invalid')

        if split_num > 2:
            self.__side = self.__get_name(name_split[1], 'side', return_type='long')
            if not self.__side:
                logger.error('Side is invalid')

            if split_num == 3:
                # name only contains type side and des
                self.__description = name_split[2]

            elif split_num == 4:
                # name contains type side des and res/index
                self.__resolution = self.__get_name(name_split[2], 'resolution', return_type='long')
                if self.__resolution:
                    self.__description = name_split[3]
                else:
                    self.__description = name_split[2]
                    self.__index = int(name_split[3])

            elif split_num == 5:
                # name contains type side des index and res/suffix
                self.__resolution = self.__get_name(name_split[2], 'resolution', return_type='long')
                if self.__resolution:
                    self.__description = name_split[3]
                    self.__index = int(name_split[4])
                else:
                    self.__description = name_split[2]
                    self.__index = int(name_split[3])
                    self.__suffix = int(name_split[4])

            elif split_num == 6:
                # name contains type side res des index and suffix
                self.__resolution = self.__get_name(name_split[2], 'resolution', return_type='long')
                if not self.__resolution:
                    logger.error('Resolution is invalid')
                self.__description = name_split[3]
                self.__index = name_split[4]
                self.__suffix = name_split[5]

            else:
                logger.error('{} is invalid'.format(name))

        elif split_num == 2:
            logger.error('{} is invalid'.format(name))

    def __compose_name(self):
        """
        compose name with given parts
        pattern: type_side_(resolution)_part_index_suffix

        Args:
            self.__type(str): name's type
            self.__side(str): name's side
            self.__resolution(str): name's resolution
            self.__description(str): name's description
            self.__index(str): name's index
            self.__suffix(str): name's suffix

        Returns:
            self.__name(str): composed name
        """
        self.__name = ''

        if self.__type:
            # check if the name has side and des
            if self.__side and self.__description:
                for key_value, key_type in zip([self.__type, self.__side, self.__resolution],
                                               ['type', 'side', 'resolution']):
                    if key_value:
                        key_value = self.__get_name(key_value, key_type, return_type='short')
                        self.__name += (key_value + '_')

                self.__name += (self.__description+'_')

                for i in [self.__index, self.__suffix]:
                    if i is not None:
                        self.__name += '{:03d}_'.format(int(i))

                self.__name = self.__name[:-1]  # remove the last '_'

            else:
                # name only contains type ('master')
                self.__name = self.__get_name(self.__type, 'type', return_type='short')

        else:
            # the name is invalid, should at least has type
            logger.error('Name is invalid, should at least has Type')

    @staticmethod
    def __get_name(key_value, key_type, return_type='short'):
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
