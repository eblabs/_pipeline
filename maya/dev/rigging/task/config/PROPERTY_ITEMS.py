# import PySide
try:
    from PySide2.QtWidgets import *
except ImportError:
    from PySide.QtGui import *

# import OrderedDict
from collections import OrderedDict

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
                           'template': '',
                           'widget': QLineEdit},

                  'dict': {'default': {},
                           'template': [],
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
                  }
