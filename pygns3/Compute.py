import json
import platform
from configparser import ConfigParser
from pathlib import Path
from requests import delete, get, post
from requests.auth import HTTPBasicAuth
import os
import sys
from pygns3.API import *
from pygns3.Graphics import *
from pygns3.Struct import *

class GNS3Compute:
    """
    Compute endpoint which handles the actual simulation.
    """

    def __init__(self, compute_id):
        self.id = compute_id
        self.connected = False

        response = GNS3API.get_request(f'/computes/{self.id}')
        if response.ok:
            self._response = response.json()
            # Pulling up the capabilities one level, makes more sense to me for now
            if self._response['connected']:
                self._response.update(self._response['capabilities'])
            del self._response['capabilities']

            self.__dict__.update(Struct(**self._response).__dict__)

    def __str__(self):
        max_key_width = max(map(len, self._response.keys()))
        return 'GNS3Compute settings:\n' + '\n'.join(
            [f'    {k:{max_key_width}} {v}' for k, v in self._response.items()]) + '\n'

    def __repr__(self):
        return f'GNS3Compute(\'{self.id}\')'

    def images(self, emulator):
        """Return a list of available image files for the given emaulator."""
        images = []
        if self.connected:
            response = GNS3API.get_request(f'/computes/{self.id}/{emulator}/images')
            if response.ok:
                for i in response.json():
                    images.append(GNS3Image(i))

        return images


