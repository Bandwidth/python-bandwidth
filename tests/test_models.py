import unittest


class ModelsTest(unittest.TestCase):

    @unittest.expectedFailure
    def test_some(self):
        self.assertEqual(1, 2)

