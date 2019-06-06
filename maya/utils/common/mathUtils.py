#=================#
# IMPORT PACKAGES #
#=================#

## import python packages
import math

## import compiled packages
import numpy

## import maya packages
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

## import utils
import naming

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

MATRIX_DEFAULT = [1.0, 0.0, 0.0, 0.0, 
				  0.0, 1.0, 0.0, 0.0, 
				  0.0, 0.0, 1.0, 0.0, 
				  0.0, 0.0, 0.0, 1.0]
				  
#=================#
#      CLASS      #
#=================#

#=================#
#    FUNCTION     #
#=================#

# points
def distance(pointA, pointB):
	'''
	distance between two given points

	Args:
		pointA(list): first point 
		pointB(list): second point

	Returns:
		distance(float): distance between two points
	'''
	dis = math.sqrt(math.pow(pointB[0]-pointA[0], 2) +
					math.pow(pointB[1]-pointA[1], 2) +
					math.pow(pointB[2]-pointA[2], 2))
	return dis 

# vector
def get_vector_from_points(pointA, pointB):
	'''
	get vector from two points

	Args:
		pointA(list)
		pointB(list)
	return:
		vector(list)
	'''
	vec = [pointA[0]-pointB[0],
		   pointA[1]-pointB[1],
		   pointA[2]-pointB[2]]
	return vec

def get_point_from_vector(point, vector, distance=1):
	'''
	get point from vector and given point, vector can be scaled by distance

	Args:
		point(list): point as orign
		vector(list): vector to shoot from the orign point

	Kwargs:
		distance(float): scale factor of the vector

	Returns:
		point(list): point from vector and given point
	'''
	vec = [vector[0]*distance, vector[1]*distance, vector[2]*distance]
	pnt = [point[0]+vec[0], point[1]+vec[1], point[2]+vec[2]]
	
	return pnt

def get_unit_vector(vector):
	'''
	get unit vector

	Args:
		vector(list)
	Returns:
		vectorUnit(list): unit vector
	'''
	vector = numpy.array(vector)
	scalar = numpy.linalg.norm(vector)
	vector /= scalar

	return vector.tolist()

# matrix
def list_to_matrix(array, column=4, row=4):
	'''
	convert list to numpy matrix

	Args:
		array(list): given list

	Kwargs:
		row(int): matrix's row number
		column(int): matrix's column number

	Return:
		matrix(np_matrix): numpy array
	'''
	np_array = numpy.reshape(array, (column, row))
	
	return numpy.asmatrix(np_array)
	
def matrix_to_list(matrix):
	'''
	convert numpy matrix to list

	Args:
		matrix(np_array): numpy array

	Returns:
		array(list): list
	'''
	matrix = numpy.reshape(matrix, matrix.size)
	array = matrix.tolist()[0]
	
	return array

def inverse_matrix(matrix):
	'''
	inverse numpy matrix

	Args:
		matrix(np_array/list)
	Returns:
		array(list): list
	'''
	if isinstance(matrix, list):
		matrix = list_to_matrix(matrix)
	matrixInv = numpy.linalg.inv(matrix)
	matrixInv = matrix_to_list(matrixInv)

	return matrixInv

def mult_matrix(matrices):
	'''
	multiply given matrices

	Args:
		matrices(list): list of numpy matrix/list
	Returns:
		array(list): list
	'''
	if isinstance(matrices[0], list):
		matrixMult = list_to_matrix(matrices[0])
	else:
		matrixMult = matrices[0]
	for matrix in matrices[1:]:
		if isinstance(matrix, list):
			matrix = list_to_matrix(matrix)
		matrixMult = numpy.matmul(matrixMult, matrix)
	matrixMult = matrix_to_list(matrixMult)

	return matrixMult

def get_local_matrix(matrixA, matrixB):
	'''
	get matrixA' local matrix on matrixB

	Args:
		matrixA(list): list of numpy matrix/list
		matrixB(list): list of numpy matrix/list
	Returns:
		array(list): list
	'''
	matrixInv = inverse_matrix(matrixB)
	matrixLocal = mult_matrix([matrixA, matrixInv])
	
	return matrixLocal
