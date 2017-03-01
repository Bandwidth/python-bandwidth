import unittest

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
