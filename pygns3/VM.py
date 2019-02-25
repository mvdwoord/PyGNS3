import json
import platform
from configparser import ConfigParser
from pathlib import Path
from requests import delete, get, post
from requests.auth import HTTPBasicAuth
import os
import sys
from pygns3.API import *
from pygns3.Struct import Struct
class GNS3VM:
    """Holds information on the GNS3 VM"""

    # TODO figure out what happens if the GNS3 VM is not configured / other issues
    def __init__(self):
        response = GNS3API.get_request(f'/gns3vm')
        if response.ok:
            self._response = response.json()
            self.__dict__.update(Struct(**self._response).__dict__)

        self.engines = []
        response = GNS3API.get_request(f'/gns3vm/engines')
        if response.ok:
            self._engines = response.json()
            for e in self._engines:
                self.engines.append(GNS3VMEngine(e))

    def __str__(self):
        max_key_width = max(map(len, self._response.keys()))
        return 'GNS3VM settings:\n' + '\n'.join(
            [f'    {k:{max_key_width}} {v}' for k, v in self._response.items()]) + '\n'

    def __repr__(self):
        return f'GNS3VM()'


class GNS3VMEngine:
    """Holds information on the GNS3 VM Engine"""

    # TODO Ask why GNS3VMEngine is not in API with an id.
    # e.g. /gns3vm/engines/{engine_id}  Like most other objects.
    # TODO figure out what happens if the GNS3 VM is not configured / other issues
    def __init__(self, engine_info):
        self.engine_id = None
        self._engine_info = engine_info
        self.__dict__.update(Struct(**engine_info).__dict__)

        self.vms = []
        response = GNS3API.get_request(f'/gns3vm/engines/{self.engine_id}/vms')
        if response.ok:
            self._vms = response.json()
            for vm in self._vms:
                self.vms.append(vm['vmname'])
        self._engine_info.update({'vms': self.vms})

    def __str__(self):
        max_key_width = max(map(len, self._engine_info.keys()))
        return 'GNS3VMEngine settings:\n' + '\n'.join(
            [f'    {k:{max_key_width}} {v}' for k, v in self._engine_info.items()]) + '\n'

    # Bit of a hack, should clean up later, but built from dict which is botched on __init__
    def __repr__(self):
        original_info = self._engine_info
        del original_info['vms']
        return f'GNS3VMEngine({original_info})'


