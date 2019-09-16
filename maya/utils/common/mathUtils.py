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
def distance(point_a, point_b):
    """
    distance between two given points

    Args:
        point_a(list): first point
        point_b(list): second point

    Returns:
        distance(float): distance between two points
    """

    dis = math.sqrt(math.pow(point_b[0] - point_a[0], 2) +
                    math.pow(point_b[1] - point_a[1], 2) +
                    math.pow(point_b[2] - point_a[2], 2))
    return dis


# vector
def get_vector_from_points(point_a, point_b, normalize=True):
    """
    get vector from two points

    Args:
        point_a(list): first point
        point_b(list): second point
    Keyword Args:
        normalize(bool): normalize vector

    Returns:
        vector(list)
    """

    vec = [point_a[0] - point_b[0],
           point_a[1] - point_b[1],
           point_a[2] - point_b[2]]
    if normalize:
        vec = get_unit_vector(vec)
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
        vector(list)

    Returns:
        vector_unit(list)

    """

    vector = numpy.array(vector)
    scalar = numpy.linalg.norm(vector)
    vector /= scalar

    return vector.tolist()


def reverse_vector(vector, normalize=False):
    """
    get vector on opposite direction

    Args:
        vector(list)
    Keyword Args:
        normalize(bool): normalize vector

    Returns:
        vector_reverse(list)
    """
    if normalize:
        vector = get_unit_vector(vector)
    return [-vector[0], -vector[1], -vector[2]]


def dot_product(vector_a, vector_b):
    """
    dot product two vectors

    Args:
        vector_a(list)
        vector_b(list)

    Returns:
        dot_product_value(float)
    """
    val = numpy.dot(vector_a, vector_b)
    return val


def cross_product(vector_a, vector_b, normalize=True):
    """
    cross product two vectors

    Args:
        vector_a(list)
        vector_b(list)
    Keyword Args:
        normalize(bool): normalize vector

    Returns:
        cross_product_vector(list)
    """
    np_vec = numpy.cross(vector_a, vector_b)
    vec = np_vec.tolist()
    if normalize:
        vec = get_unit_vector(vec)
    return vec


def build_coordinate_system(vector_x, vector_y, flip_check_vec=None):
    """
    build object coordinate system base on the vec
    Args:
        vector_x(list)
        vector_y(list)
    Keyword Args:
        flip_check_vec(list): third vector reference to check for flip

    Returns:
        [vector_x, vector_y, vector_z]
    """
    vector_x = get_unit_vector(vector_x)
    vector_z = cross_product(vector_x, vector_y, normalize=True)
    if flip_check_vec:
        dot_product_check = dot_product(vector_z, flip_check_vec)
        if dot_product_check < 0:
            vector_z = inverse_matrix(vector_z)
    vector_y = cross_product(vector_z, vector_x, normalize=True)
    return [vector_x, vector_y, vector_z]


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


def get_local_matrix(matrix_a, matrix_b):
    """
    get matrix_a' local matrix on matrix_b

    Args:
        matrix_a(list): list of numpy matrix/list
        matrix_b(list): list of numpy matrix/list

    Returns:
        matrix_local(list): local matrix as list
    """

    matrix_b_inverse = inverse_matrix(matrix_b)
    matrix_local = mult_matrix([matrix_a, matrix_b_inverse])

    return matrix_local


def four_by_four_matrix(vector_x, vector_y, vector_z, position):
    """
    create four by four matrix

    Args:
        vector_x(list)
        vector_y(list)
        vector_z(list)
        position(list)

    Returns:
        matrix(list)
    """
    matrix = [vector_x[0], vector_x[1], vector_x[2], 0,
              vector_y[0], vector_y[1], vector_y[2], 0,
              vector_z[0], vector_z[1], vector_z[2], 0,
              position[0], position[1], position[2], 1]
    return matrix
