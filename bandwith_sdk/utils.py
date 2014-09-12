import re

ALL_CAPITAL = re.compile(r'(.)([A-Z][a-z]+)')
CASE_SWITCH = re.compile(r'([a-z0-9])([A-Z])')
UNDERSCORES = re.compile(r'[a-z]_[a-z]')


def make_camel(*args):
    def underscoreToCamel(match):
        return match.group()[0] + match.group()[2].upper()

    def camelize(value):
        return UNDERSCORES.sub(underscoreToCamel, value)
    return list(map(camelize, args))


def make_underscore(*args):
    def underscorize(value):
        partial_result = ALL_CAPITAL.sub(r'\1_\2', value)
        return CASE_SWITCH.sub(r'\1_\2', partial_result).lower()

    return list(map(underscorize, args))


def prepare_json(dct):
    keys = make_camel(*dct.keys())
    return dict(zip(keys, dct.values()))


def unpack_json_dct(dct):
    keys = make_underscore(*dct.keys())
    return dict(zip(keys, dct.values()))
