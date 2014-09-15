import six
import re
from dateutil import parser
from datetime import datetime

ALL_CAPITAL = re.compile(r'(.)([A-Z][a-z]+)')
CASE_SWITCH = re.compile(r'([a-z0-9])([A-Z])')
UNDERSCORES = re.compile(r'[a-z]_[a-z]{0,1}')


def underscoreToCamel(match):
    groups = match.group()
    if len(groups) == 2:
        # underscoreToCamel('from_') -> 'from'
        return groups[0]
    return groups[0] + groups[2].upper()


def camelize(value):
    return UNDERSCORES.sub(underscoreToCamel, value)


def underscorize(value):
    partial_result = ALL_CAPITAL.sub(r'\1_\2', value)
    return CASE_SWITCH.sub(r'\1_\2', partial_result).lower()


def make_camel(*args):
    return [camelize(a) for a in args]


def make_underscore(*args):
    return list(map(underscorize, args))


def prepare_json(dct):
    keys = make_camel(*dct.keys())
    return dict(zip(keys, dct.values()))


def unpack_json_dct(dct):
    keys = make_underscore(*dct.keys())
    return dict(zip(keys, dct.values()))


def drop_empty(data):
    return {k: v for k, v in six.iteritems(data) if v is not None}


# alternative tools

def to_api(data):
    """
    :param data: dictionary {'max_digits': 1}
    :return: {'maxDigits': 1}
    """
    assert isinstance(data, dict), 'Wrong type'
    data = drop_empty(data)
    for k, v in six.iteritems(data):
        if isinstance(v, datetime):
            data[k] = v.isoformat()
    api_data = {camelize(k): v for k, v in six.iteritems(data)}
    return api_data


def from_api(data):
    """
    :param data: {'maxDigits': 1}
    :return: {'max_digits': 1}
    """
    assert isinstance(data, dict), 'Wrong type'
    app_data = {underscorize(k): v for k, v in six.iteritems(data)}
    for k, v in six.iteritems(app_data):
        if 'time' in k.lower():
            app_data[k] = parser.parse(v)
    return app_data
