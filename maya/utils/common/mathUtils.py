# IMPORT PACKAGES

# import python packages
import math

# import compiled packages
import numpy

# import utils
import logUtils

# CONSTANT
logger = logUtils.logger

MATRIX_DEFAULT = [1.0, 0.0, 0.0, 0.0,
                  0.0, 1.0, 0.0, 0.0,
                  0.0, 0.0, 1.0, 0.0,
                  0.0, 0.0, 0.0, 1.0]


# FUNCTION

# value
def clamp_value(value, clamp_range):
    """
    clamp the given value in range

    Args:
        value(float): given value
        clamp_range(list): [min, max]

    Returns:
        clamp_value(float)
    """
    if value < clamp_range[0]:
        value = clamp_range[0]
    if value > clamp_range[1]:
        value = clamp_range[1]
    return value


def remap_value(value, input_range, output_range):
    """
    remap given value from the input range to output range

    Args:
        value(float): given value
        input_range(list): [min, max]
        output_range(list): [min, max]

    Returns:
        remap_value(float)
    """
    # clamp value
    value = clamp_value(value, input_range)
    # get weight
    weight = (value - input_range[0])/float(input_range[1] - input_range[0])
    # remap to output range
    value = (output_range[1] - output_range[0])*weight + output_range[0]

    return value


# points
def distance(pointA, pointB):
    """
    distance between two given points

    Args:
        pointA(list): first point
        pointB(list): second point

    Returns:
        distance(float): distance between two points
    """

    dis = math.sqrt(math.pow(pointB[0] - pointA[0], 2) +
                    math.pow(pointB[1] - pointA[1], 2) +
                    math.pow(pointB[2] - pointA[2], 2))
    return dis


# vector
def get_vector_from_points(pointA, pointB):
    """
    get vector from two points

    Args:
        pointA(list): first point
        pointB(list): second point

    Returns:
        vector(list)
    """

    vec = [pointA[0] - pointB[0],
           pointA[1] - pointB[1],
           pointA[2] - pointB[2]]
    return vec


def get_point_from_vector(point, vector, distance=1):
    """
    get point from vector and given point, vector can be scaled by distance

    Args:
        point(list): point as initial position
        vector(list): vector to shoot from the initial position

    Keyword Args:
        distance(float): scale factor of the vector

    Returns:
        point(list): point from vector and given point
    """

    vec = [vector[0] * distance, vector[1] * distance, vector[2] * distance]
    pnt = [point[0] + vec[0], point[1] + vec[1], point[2] + vec[2]]

    return pnt


def get_unit_vector(vector):
    """
    Args:
        vector(list):

    Returns:
        vector_unit(list)

    """

    vector = numpy.array(vector)
    scalar = numpy.linalg.norm(vector)
    vector /= scalar

    return vector.tolist()


# matrix
def list_to_matrix(array, column=4, row=4):
    """
    convert list to numpy matrix

    Args:
        array(list): given list

    Keyword Args:
        column(int): matrix's column number, default is 4
        row(int): matrix's row number, default is 4

    Returns:
        matrix(np_matrix): numpy array
    """

    np_array = numpy.reshape(array, (column, row))

    return numpy.asmatrix(np_array)


def matrix_to_list(matrix):
    """
    convert numpy matrix to list

    Args:
        matrix(np_array): numpy array

    Returns:
        array(list): list
    """

    matrix = numpy.reshape(matrix, matrix.size)
    array = matrix.tolist()[0]

    return array


def inverse_matrix(matrix):
    """
    inverse numpy matrix

    Args:
        matrix(np_array/list): given matrix

    Returns:
        matrix_inverse(list): inverse matrix as list
    """

    if isinstance(matrix, list):
        matrix = list_to_matrix(matrix)
    matrix_inverse = numpy.linalg.inv(matrix)
    matrix_inverse = matrix_to_list(matrix_inverse)

    return matrix_inverse


def mult_matrix(matrices):
    """
    multiply given matrices

    Args:
        matrices(list): list of numpy matrix/list

    Returns:
        matrix_mult(list): matrix as list
    """

    if isinstance(matrices[0], list):
        matrix_mult = list_to_matrix(matrices[0])
    else:
        matrix_mult = matrices[0]

    for matrix in matrices[1:]:
        if isinstance(matrix, list):
            matrix = list_to_matrix(matrix)
        matrix_mult = numpy.matmul(matrix_mult, matrix)
    matrix_mult = matrix_to_list(matrix_mult)

    return matrix_mult


def get_local_matrix(matrixA, matrixB):
    """
    get matrixA' local matrix on matrixB

    Args:
        matrixA(list): list of numpy matrix/list
        matrixB(list): list of numpy matrix/list

    Returns:
        matrix_local(list): local matrix as list
    """

    matrixB_inverse = inverse_matrix(matrixB)
    matrix_local = mult_matrix([matrixA, matrixB_inverse])

    return matrix_local
