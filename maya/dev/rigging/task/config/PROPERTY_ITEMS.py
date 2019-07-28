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
						   'widget': QComboBox},

				  'list': {'default': [],
						   'template': '',
						   'widget': QLineEdit},

				  'dict': {'default': {},
						   'template': [],
						   'widget': QLineEdit},

				  'callback': {'default': '',
				  			   'height': 100,
				  			   'widget': QPlainTextEdit}
				  			  }

