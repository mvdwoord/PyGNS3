import unittest
from pygns3 import *

"""
Minimal test suite, mainly to setup and configure my workflow"""


class TestController(unittest.TestCase):
    def setUp(self):
        GNS3API.load_configuration()
        self.controller = GNS3Controller()
        self.version = self.controller.version

    def test_controller(self):
        self.assertTrue(self, type(self.controller) == GNS3Controller)

    def test_assert_version(self):
        self.assertTrue(self, self.controller.assert_version(self.version))

# That's an AWFUL lot of 'self'
# TODO reduce narcisissm if possible
