import unittest
import pygns3

"""
Minimal test suite, mainly to setup and configure my workflow"""


class TestController(unittest.TestCase):
    def setUp(self):
        self.controller = pygns3.GNS3Controller()
        self.version = self.controller.version

    def test_controller(self):
        self.assertTrue(self, type(self.controller) == pygns3.GNS3Controller)

    def test_assert_version(self):
        self.assertTrue(self, self.controller.assert_version(self.version))

# That's an AWFUL lot of 'self'
# TODO reduce narcisissm if possible
