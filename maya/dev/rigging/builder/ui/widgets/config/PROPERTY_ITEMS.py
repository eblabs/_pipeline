# IMPORT PACKAGES

# import PySide
try:
    from PySide2.QtWidgets import *
except ImportError:
    from PySide.QtGui import *


#  CONSTANT
PROPERTY_ITEMS = {'str': {'value': '',
                          'widget': QLineEdit},

                  'float': {'value': 0.0,
                            'min': None,
                            'max': None,
                            'widget': QDoubleSpinBox},

                  'int': {'value': -1,
                          'min': -1,
                          'max': None,
                          'skippable': False,
                          'widget': QSpinBox},

                  'enum': {'value': None,
                           'enum': [],
                           'widget': QComboBox},

                  'bool': {'value': True,
                           'widget': QComboBox},

                  'list': {'value': [],
                           'template': '',
                           'widget': QLineEdit},

                  'dict': {'value': {},
                           'template': [],
                           'widget': QLineEdit},

                  # common task property type
                  'strPath': {'value': [],
                              'template': 'str',
                              'widget': QLineEdit},
                  }
