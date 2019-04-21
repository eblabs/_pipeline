import ast

def convertStringToDict(sString):
	dDict = ast.literal_eval(sString)
	return dDict
	