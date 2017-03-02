import re


def convert_string_to_snake_case(s):
    """
    Changes String to from camelCase to snake_case
    :param s: String to convert
    :rtype: String
    :rertuns: String converted to snake_case
    """
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    return a.sub(r'_\1', s).lower()


def convert_list_to_snake_case(a):
    """
    Iterates over a list and changes the key values
    from camelCase to snake_case
    :param a: List of dictionaries to convert
    :rtype: list
    :rertuns: list with each key converted to snake_case
    """
    new_arr = []
    for i in a:
        if isinstance(i, list):
            new_arr.append(convert_list_to_snake_case(i))
        elif isinstance(i, dict):
            new_arr.append(convert_dict_to_snake_case(i))
        else:
            new_arr.append(i)
    return new_arr


def convert_dict_to_snake_case(d):
    """
    Iterates over a dictionary and changes the key values
    from camelCase to snake_case
    :param d: Dictionary to convert
    :rtype: dict
    :rertuns: dictionary with each key converted to snake_case
    """
    out = {}
    for k in d:
        new_k = convert_string_to_snake_case(k)
        if isinstance(d[k], dict):
            out[new_k] = convert_dict_to_snake_case(d[k])
        elif isinstance(d[k], list):
            out[new_k] = convert_list_to_snake_case(d[k])
        else:
            out[new_k] = d[k]
    return out


def convert_object_to_snake_case(o):
    """
    Iterates over an object and changes the key values
    from camelCase to snake_case
    :param o: Dictionary or Array of dictionaries to convert
    :rtype: o
    :rertuns: Same type that was passed
    """
    if isinstance(o, list):
        return convert_list_to_snake_case(o)
    elif isinstance(o, dict):
        return convert_dict_to_snake_case(o)
    elif isinstance(o, str):
        return convert_string_to_snake_case(o)
    else:
        return o
