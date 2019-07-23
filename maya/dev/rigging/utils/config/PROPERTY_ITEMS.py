# =================#
# IMPORT PACKAGES  #
# =================#

# import PySide
try:
	from PySide2.QtWidgets import *
except ImportError:
	from PySide.QtGui import *

# =================#
#   GLOBAL VARS    #
# =================#

PROPERTY_ITEMS = {'str': {'value': '',
						  'widget': QLineEdit},

				  'float': {'value': 0.0,
							'min': None,
							'max': None,
							'widget': QDoubleSpinBox},

				  'int': {'value': 0,
						  'min': None,
						  'max': None,
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

				  'callback': {'value': '',
				  			   'widget': QPlainTextEdit}
				  			  }

