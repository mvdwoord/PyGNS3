import json
import platform
from configparser import ConfigParser
from pathlib import Path
from requests import delete, get, post
from requests.auth import HTTPBasicAuth
import os
import sys
class GNS3API:
    """
    Global object which is dynamically populated with the configuration file.
    Explicitly used attributes are defined to avoid unresolved references in code inspection.
    """
    base = None
    cred = None
    host = None
    password = None
    port = None
    projects_path = None
    protocol = None
    user = None
    config_file_found = False
    SUPPRESSED, DEBUG = 'SUPPRESSED, DEBUG'.split(', ')
    console_log_level = SUPPRESSED

    @staticmethod
    def set_console_log_level(level='DEBUG'):
        GNS3API.console_log_level = level

    @staticmethod
    def load_configuration(section='Server'):
        """
        The GNS3 Server (/Controller) is configured through the gns3_server.conf file.
        GNS3 searches various locations depending on the platform. These locations are listed in the
        documentation.

        DOCUMENTATION   /   GNS3 SERVER CONFIGURATION FILE
        http://docs.gns3.com/1f6uXq05vukccKdMCHhdki5MXFhV8vcwuGwiRvXMQvM0/
        """

        # TODO: Add all possible configuration files for each operating system.
        platform_file_locations = {

            'Windows': [
                os.path.join(os.getenv('APPDATA'), 'GNS3', 'gns3_server.ini'),
            ],
            'Linux': [
                os.path.join(str(Path.home()), '.config', 'GNS3', 'gns3_server.conf'),
            ],
            'Darwin': [
                os.path.join(str(Path.home()), '.config', 'GNS3', 'gns3_server.conf'),
            ]
        }

        config_file_location = ''
        system_platform = platform.system()
        if system_platform in platform_file_locations.keys() and '--custom-config' not in sys.argv:
            for potential_location in platform_file_locations[system_platform]:
                if os.path.isfile(potential_location):
                    config_file_location = potential_location
                    break

        while not os.path.isfile(config_file_location):
            try:
                conf_arg_ind = sys.argv.index('--custom-config')
                try:
                    next_arg = sys.argv[conf_arg_ind + 1]
                    if next_arg[0] == '-':
                        raise IndexError
                    config_file_location = next_arg
                except IndexError:
                    config_file_location = str(input(f"Please enter the config file location.\n"))
            except ValueError:
                config_file_location = str(input(
                    f"There is no default config file location for your operating "
                    f"system ({system_platform}).\nPlease enter the configuration file location manually.\n"
                    f"Example: /home/<YourUserName>/.config/GNS3/GNS3.conf\nIf you see this repeatedly you're "
                    f"entering an invalid Path.\n"))

        # TODO verify behaviour ConfigParser vs GNS3 (i.e. does it merge or is there precedence?)
        parser = ConfigParser()
        found = parser.read(config_file_location)
        if found and section in parser.sections():
            for k, v in dict(parser.items(section)).items():
                setattr(GNS3API, k, v)

            GNS3API.cred = HTTPBasicAuth(GNS3API.user, GNS3API.password)
            GNS3API.base = f'{GNS3API.protocol}://{GNS3API.host}:{str(GNS3API.port)}/v2'
        else:
            raise Exception(f'An error occurred. The error might be related to an invalid configuration file.\n')

    @staticmethod
    def delete_request(path):
        """performs a DELETE request to `path`"""
        url = f'{GNS3API.base}{path}'
        try:
            response = delete(url, auth=GNS3API.cred)
        except Exception as e:
            raise Exception(f'GNS3API DELETE Error at URL: {url}') from e

        return response

    @staticmethod
    def get_request(path):
        """performs a GET request to `path`"""
        url = f'{GNS3API.base}{path}'
        # This is still not completely right. Trying to figure out how to best deal with all
        # possible exceptions
        # Invalid path can be actual invalid path (404) or a 404 from GNS3 for an object not found.
        # The latter returns json with a description of the error. Codes differ (409 and others?)
        # TODO Improve Exception handling in get_request()
        try:
            response = get(url, auth=GNS3API.cred)
            return response
        except Exception as e:
            raise Exception(f'GNS3API GET Error at URL: {url}') from e

    @staticmethod
    def post_request(path, data={}):
        """performs a POST request to `path`"""

        url = f'{GNS3API.base}{path}'
        # TODO Improve Exception handling in post_request()
        try:
            response = post(url, data=data, auth=GNS3API.cred)
        except Exception as e:
            raise Exception(f'GNS3API POST Error {e, e.args} at URL: {url}')

        return response


