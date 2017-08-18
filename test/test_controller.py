import unittest
import json
from unittest import mock
from pygns3 import *
from test import mock_get
"""Minimal test suite, mainly to setup and configure my workflow
"""


def mocked_gns3api_get_request(path):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return json.loads(self.json_data)

        def ok(self):
            return True

    if path in mock_get.keys():
        return MockResponse(str(mock_get[path]), 201)
    else:
        return MockResponse(None, 404)


class TestController(unittest.TestCase):
    @mock.patch('pygns3.GNS3API.get_request', side_effect=mocked_gns3api_get_request)
    def setUp(self, mock_get):
        GNS3API.load_configuration()

        self.compute = GNS3Compute('local')
        self.version = GNS3API.get_request('/v2/version').json()
        self.controller = GNS3Controller()

    def test_version(self):
        self.assertTrue(self.version['version'] == '2.0.3')

    def test_compute(self):
        print(self.version)
        self.assertTrue(self.compute.connected == True)

