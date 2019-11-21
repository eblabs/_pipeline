# import PySide
try:
    from PySide2.QtWidgets import *
except ImportError:
    from PySide.QtGui import *


PROPERTY_ITEMS = {'str': {'default': '',
                          'widget': QLineEdit},

                  'float': {'default': 0.0,
                            'min': None,
                            'max': None,
                            'widget': QDoubleSpinBox},

                  'int': {'default': 0,
                          'min': None,
                          'max': None,
                          'widget': QSpinBox},

                  'enum': {'default': None,
                           'enum': [],
                           'widget': QComboBox},

                  'bool': {'default': True,
                           'widget': QComboBox,
                           'enum': ['True', 'False']},

                  'list': {'default': [],
                           'template': 'null',
                           'widget': QLineEdit},

                  'dict': {'default': {},
                           'template': 'null',
                           'widget': QLineEdit},

                  'callback': {'default': '',
                               'height': 100,
                               'widget': QPlainTextEdit},

                  'rig_data': {'default': {'project': '', 'asset': '', 'rig_type': '', 'task': ''},
                               'template': {'project': '', 'asset': '', 'rig_type': '', 'task': ''},
                               'keys_order': ['project', 'asset', 'rig_type', 'task'],
                               'widget': QLineEdit},

                  'model_data': {'default': {'model_type': '', 'resolution': []},
                                 'template': {'model_type': '', 'resolution': []},
                                 'keys_order': ['model_type', 'resolution'],
                                 'widget': QLineEdit},

                  'rig_data_import': {'default': {'project': '', 'asset': '', 'rig_type': '', 'task': '', 'filter': ''},
                                      'template': {'project': '', 'asset': '', 'rig_type': '', 'task': '',
                                                   'filter': ''},
                                      'keys_order': ['project', 'asset', 'rig_type', 'task', 'filter'],
                                      'widget': QLineEdit},

                  'space_info': {'default': {'parent': {'space': {},
                                                        'defaults': []},
                                             'point': {'space': {},
                                                       'defaults': []},
                                             'orient': {'space': {},
                                                        'defaults': []},
                                             'scale': {'space': {},
                                                       'defaults': []}},
                                 'template': {'parent': 'space_data', 'point': 'space_data', 'orient': 'space_data',
                                              'scale': 'space_data'},
                                 'template_lock': True,
                                 'keys_order': ['parent', 'point', 'orient', 'scale'],
                                 'widget': QLineEdit,
                                 'key_edit': False,
                                 'val_edit': False,
                                 'checkable': True},

                  'space_data': {'default': {'space': {}, 'defaults': []},
                                 'template': {'space': 'space_input', 'defaults': []},
                                 'template_lock': True,
                                 'keys_order': ['space', 'defaults'],
                                 'widget': QLineEdit,
                                 'key_edit': False,
                                 'val_edit': False,
                                 'checkable': False},

                  'space_input': {'default': {},
                                  'template': 'str',
                                  'widget': QLineEdit,
                                  'key_edit': True,
                                  'val_edit': True,
                                  'checkable': True}
                  }
