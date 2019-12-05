# FUNCTION
def kwargs(long_name, default_value, kwargs_dict, short_name='', connect_name=''):
    """
    get variable value from given dictionary, support short cut key

    Args:
        long_name(str): key name
        default_value: default value
        kwargs_dict(dict): given dictionary
    Kwargs:
        short_name(str)['']: short key name
        connect_name(str)['']: if has any other variable names let user catch the same behavior
    Returns:
        value: value from given kwargs
    """

    if long_name in kwargs_dict:
        val = kwargs_dict[long_name]
    elif short_name and short_name in kwargs_dict:
        val = kwargs_dict[short_name]
    elif connect_name and connect_name in kwargs_dict:
        val = kwargs_dict[connect_name]
    else:
        val = default_value

    return val
