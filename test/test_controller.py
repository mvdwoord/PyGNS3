"""
Minimal test suite, mainly to setup and configure my workflow and figure out how to write
proper tests. A mock is used to be able to test offline, against a dictionary of cached API
responses. This dict is generated with some scripts in the tools folder of the project.

I should define a better test project file, to be able to import that and test against it. That
file can then be included in the test directory for distribution.
"""
import unittest
import json
from unittest import mock
from pygns3 import *
from test import mock_get

TEST_PROJECT_NAME = 'Basic 4 Routers'


def mocked_gns3api_get_request(path):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return json.loads(self.json_data)

        @staticmethod
        def ok():
            return True

    if path in mock_get.keys():
        return MockResponse(str(mock_get[path]), 201)
    else:
        return MockResponse(None, 404)


class TestController(unittest.TestCase):

    @classmethod
    @mock.patch('pygns3.GNS3API.get_request', side_effect=mocked_gns3api_get_request)
    def setUpClass(cls, mock_get):
        GNS3API.load_configuration()

        cls.compute = GNS3Compute('local')
        cls.controller = GNS3Controller()

    def test_compute(self):
        self.assertTrue(self.compute.connected == True)
        self.assertTrue((self.compute.version == '2.0.3'))


    @mock.patch('pygns3.GNS3API.get_request', side_effect=mocked_gns3api_get_request)
    def test_project_by_name(self, patch):
        test_project = GNS3Project.from_name(TEST_PROJECT_NAME)

        self.assertTrue(test_project.name == TEST_PROJECT_NAME)
        self.assertTrue(len(test_project.drawings) == 6)
        self.assertTrue(len(test_project.links) == 6)
        self.assertTrue(len(test_project.nodes) == 6)
        self.assertTrue(len(test_project.snapshots) == 1)
