import unittest
import six
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch
import tests.json.camel_test_values
from tests.json.camel_test_values import before_array_dict
from tests.json.camel_test_values import after_array_dict
from bandwidth.convert_camel import convert_object_to_snake_case


class ConvertCamelTests(unittest.TestCase):

    def test_conversion(self):
        """
        convert_object_to_snake_case() should successfully transform a nested list
        """
        new_dict = convert_object_to_snake_case(before_array_dict)
        self.assertEqual(new_dict, after_array_dict)

    def test_default_case(self):
        """
        convert_object_to_snake_case() should return same object if not string, list, dict
        """
        my_value = convert_object_to_snake_case(True)
        self.assertEqual(my_value, True)

    def test_string_case(self):
        """
        convert_object_to_snake_case() should snake a string
        """
        my_value = convert_object_to_snake_case("helloWorld")
        self.assertEqual("hello_world", my_value)

    def test_dict_case(self):
        """
        convert_object_to_snake_case() should snake a dict
        """
        my_value = convert_object_to_snake_case({"helloWorld": "goodByeWorld"})
        self.assertEqual(my_value, {"hello_world": "goodByeWorld"})
