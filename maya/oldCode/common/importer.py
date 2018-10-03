def importModule(sModulePath, bReload = False):
	lComponents = sModulePath.split('.')
	if len(lComponents) > 1:
		sModulePathUpper = ''
		for sComponent in lComponents:
			sModulePathUpper += '%s.' %sComponent
		oModule = __import__(sModulePathUpper[:-1], fromlist = [lComponents[-1]])
	else:
		oModule = __import__(sModulePath)
	if bReload:
		reload(oModule)
	return oModule