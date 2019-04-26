#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import python packages
import json
import cPickle

## import compiled packages
import numpy

#=================#
#   GLOBAL VARS   #
#=================#

#=================#
#    FUNCTION     #
#=================#
def write_json_file(path, data):
	'''
	Write data to the given path as json file

	Args:
		path(str): Given path
		data(dict/list): Given data
	'''
	with open(path, 'w') as outfile:
		json.dump(data, outfile, indent=4, sort_keys=True)
	file.close(outfile)

def read_json_file(path):
	'''
	Read data from the given json file path

	Args:
		path(str): Given json file path

	Return:
		data(dict/list): Data from the json file
	'''
	with open(path, 'r') as infile:
		data = json.load(infile)
	file.close(infile)
	return data

def write_cPickle_file(path, data):
	'''
	Write data to the given path as cPickle file

	Args:
		path(str): Given path
		data(dict/list): Given data
	'''
	with open(path, 'wb') as outfile:
		cPickle.dump(data, outfile, cPickle.HIGHEST_PROTOCOL)
	outfile.close()

def read_cPickle_file(path):
	'''
	Read data from the given cPickle file path

	Args:
		path(str): Given cPickle file path

	Return:
		data(dict/list): Data from the cPickle file
	'''
	with open(path, 'rb') as infile:
		data = cPickle.load(infile)
	infile.close()
	return data

def write_numpy_file(path, arr):
	'''
	Write data to the given path as numpy file

	Args:
		path(str): Given path
		data(dict/list): Given numpy array
	'''
	numpy.save(path, arr)

def read_numpy_file(path):
	'''
	Read data from the given numpy file path

	Args:
		path(str): Given numpy file path

	Return:
		data(array): Numpy array from the numpy file
	'''
	data = numpy.load(path)
	return data