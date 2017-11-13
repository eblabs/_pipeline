## External Import
import math

#### Functions
def getAvgValueFromList(lList):
	fValue = 0
	iList = len(lList)
	for v in lList:
		fValue += v / float(iList)
	return fValue

#--------------- vector ------------
def vector(pointA, pointB):
	return [pointB[0] - pointA[0], pointB[1] - pointA[1], pointB[2] - pointA[2]]

def vectorScale(vector, fScale):
	return [vector[0]*fScale, vector[1]*fScale, vector[2]*fScale]

def getPointFromVectorAndPoint(pointA, vector):
	return [pointA[0] + vector[0], pointA[1] + vector[1], pointA[2] + vector[2]]