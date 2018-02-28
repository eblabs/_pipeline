def importModule(sModulePath):
	lComponents = sModulePath.split('.')
	if len(lComponents) > 1:
		sModulePathUpper = ''
		for sComponent in lComponents:
			sModulePathUpper += '%s.' %sComponent
		oModule = __import__(sModulePathUpper[:-1], fromlist = [lComponents[-1]])
	else:
		oModule = __import__(sModulePath)
	return oModule