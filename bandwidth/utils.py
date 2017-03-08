import os
import copy
import string
import six
import re
from six.moves import configparser

from dateutil import parser
from datetime import datetime, date

ALL_CAPITAL = re.compile(r'(.)([A-Z][a-z]+)')
CASE_SWITCH = re.compile(r'([a-z0-9])([A-Z])')
UNDERSCORES = re.compile(r'[a-z]_[a-z]{0,1}')

time_fields = frozenset(
    ['time', 'completed_time', 'created_time', 'activated_time',
     'start_time', 'active_time', 'end_time', 'created', 'updated',
     'added_time'])


def underscoreToCamel(match):
    groups = match.group()
    if len(groups) == 2:
        # underscoreToCamel('from_') -> 'from'
        return groups[0]
    return groups[0] + groups[2].upper()


def camelize(value):
    return UNDERSCORES.sub(underscoreToCamel, value)


def toTag(value):
    temp = camelize(value)
    ret_val = temp[0].upper() + temp[1:]

    return ret_val


def underscorize(value):
    partial_result = ALL_CAPITAL.sub(r'\1_\2', value)
    return CASE_SWITCH.sub(r'\1_\2', partial_result).lower()


def drop_empty(data):
    return {k: v for k, v in six.iteritems(data) if v is not None}


# alternative tools

def to_api(data):
    """
    :param data: dictionary {'max_digits': 1}
    :return: {'maxDigits': 1}
    """
    if not data:
        return {}
    assert isinstance(data, dict), 'Wrong type'
    data = drop_empty(data)
    for k, v in six.iteritems(data):
        if isinstance(v, (datetime, date)):
            data[k] = v.isoformat()
    api_data = {camelize(k): to_api(v) if isinstance(v,
                                                     dict) else v for k,
                v in six.iteritems(data)}
    return api_data


def from_api(data):
    """
    :param data: {'maxDigits': 1}
    :return: {'max_digits': 1}
    """
    assert isinstance(data, dict), 'Wrong type'
    app_data = {underscorize(k): v for k, v in six.iteritems(data)}
    for k, v in six.iteritems(app_data):
        if k in time_fields:
            app_data[k] = parser.parse(v)
    return app_data


def enum(*vals, **enums):
    """
    Enum without third party libs and compatible with py2 and py3 versions.
    """
    enums.update(dict(zip(vals, vals)))
    return type('Enum', (), enums)


def get_location_id(response):
    location = response.headers['Location']
    return location.split('/')[-1]


def get_creds_from_file(config_path):
    cfg_parser = configparser.RawConfigParser()
    cfg_parser.read(config_path)
    user_id = cfg_parser.get('catapult', 'user_id')
    token = cfg_parser.get('catapult', 'token')
    secret = cfg_parser.get('catapult', 'secret')
    return user_id, token, secret


file_exists = os.path.isfile

# converts an etree to dict, useful to convert xml to dict


def etree2dict(tree, sub_node_name=None):
    if sub_node_name is not None:
        tree = tree.find(sub_node_name)

    root, contents = recursive_dict(tree)
    return {root: contents}


def recursive_dict(element):
    if 'list' in element.tag.lower() or 'completednumbers' in element.tag.lower() or (
            element.attrib and 'type' in element.attrib and element.attrib['type'] == "array"):
        return element.tag, [(dict(map(recursive_dict, child)) or getElementValue(child)) for child in element]
    else:
        return element.tag, dict(map(recursive_dict, element)) or getElementValue(element)


def getElementValue(element):
    if element.text:
        if element.attrib and 'type' in element.attrib:
            attr_type = element.attrib.get('type')
            if attr_type == 'integer':
                return int(element.text.strip())
            if attr_type == 'float':
                return float(element.text.strip())
            if attr_type == 'boolean':
                return element.text.lower().strip() == 'true'
            if attr_type == 'datetime':
                t = datetime.datetime(element.text.strip())
                return t.strftime('%Y-%m-%d %H%M%S %I')
        else:
            return element.text
    elif element.attrib:
        if 'nil' in element.attrib:
            return None
        else:
            return element.attrib
    else:
        return None


def etree_to_simple_list(tree, sub_node_name=None):
    if sub_node_name is not None:
        tree = tree.find(sub_node_name)

    list = []
    for child in tree:
        root, contents = recursive_dict(child)
        list.append({root: contents})

    return list


def xml_to_dict(root, ):
    pass


def remove_key_from_dict(dict, key=''):
    """
    removes a key from a dict
    Args:
        dict: dictionary
        key: name of key to remove

    Returns: a copy of the dictionary withou the key

    """
    d = copy.deepcopy(dict)
    if key in d:
        del d[key]

    return d


def print_dict(dict):
    for k, v in dict.items():
        print 'key:{0}, value:{0}'.format(k, v)
