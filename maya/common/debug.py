
def printer(sPrint = ''):
	print 'Debug Printer Start ------------------------------------'
	print sPrint
	print 'Debug Printer End --------------------------------------'

def error(sError = ''):
	print 'Debug Error --------------------------------------------'
	raise RuntimeError(sError)