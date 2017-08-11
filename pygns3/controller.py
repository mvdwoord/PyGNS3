import json
import platform
from configparser import ConfigParser
from pathlib import Path
from requests import get, post
from requests.auth import HTTPBasicAuth


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

    @staticmethod
    def load_configuration(section='Server'):
        """
        The GNS3 Server (/Controller) is configured through the gns3_server.conf file.
        GNS3 searches various locations depending on the platform. These locations are listed in the documentation
                DOCUMENTATION   /   GNS3 SERVER CONFIGURATION FILE
                http://docs.gns3.com/1f6uXq05vukccKdMCHhdki5MXFhV8vcwuGwiRvXMQvM0/
        """
        platform_file_locations = {
            'Darwin': [
                f"{str(Path.home())}/.config/GNS3/gns3_server.conf",
                "./gns3_server.conf"
            ]
            # TODO add Linux/Windows file locations and test.
        }
        system_platform = platform.system()
        if system_platform not in platform_file_locations.keys():
            # TODO manual input option? Perhaps additional argument in staticmethod?
            raise OSError('Operating system {} not supported')

        # TODO verify behaviour ConfigParser vs GNS3 (i.e. does it merge files or is there precedence (presidents?)
        parser = ConfigParser()
        found = parser.read(platform_file_locations[system_platform])
        if found and section in parser.sections():
            for k, v in dict(parser.items(section)).items():
                setattr(GNS3API, k, v)

            GNS3API.cred = HTTPBasicAuth(GNS3API.user, GNS3API.password)
            GNS3API.base = f'{GNS3API.protocol}://{GNS3API.host}:{str(GNS3API.port)}'
        else:
            print(f'Platform: {system_platform}\n'
                  'Looked for configuration files at these locations:\n')
            for candidate in platform_file_locations[system_platform]:
                print(f'  {candidate}')
            print('\n')
            raise FileNotFoundError('No Valid Configuration File Found')

    @staticmethod
    def get_request(path):
        """performs a GET request to `path`"""
        url = f'{GNS3API.base}{path}'
        # This is still not completely right. Trying to figure out how to best deal with all possible exceptions
        # Invalid path can be actual invalid path (404) or a 404 from GNS3 for an object not found.
        # The latter returns json with a description of the error. Codes differ (409 and others?)
        # TODO Improve Exception handling in get_request()
        try:
            response = get(url, auth=GNS3API.cred)
        except Exception as e:
            raise Exception(f'GNS3API GET Error at URL: {url}') from e

        return response

    @staticmethod
    def post_request(path, data):
        """performs a POST request to `path`"""

        url = f'{GNS3API.base}{path}'
        # TODO Improve Exception handling in post_request()
        try:
            response = post(url, data=data, auth=GNS3API.cred)
        except Exception as e:
            raise Exception(f'GNS3API POST Error {response.status_code} at URL: {url}') from e

        return response


class GNS3Controller:
    """
    Wrapper for the Controller API in GNS3. This is the central object which holds references to almost all other
    (collections of) objects in GNS3.
    """

    def __init__(self):

        # Set version attribute
        response = GNS3API.get_request('/v2/version')
        self.version = response.json()['version']

        self.computes = []
        response = GNS3API.get_request(f'/v2/computes')
        for p in response.json():
            self.computes.append(GNS3Compute(p['compute_id']))

        # TODO check empty projects corner case behaviour
        self.projects = []
        response = GNS3API.get_request(f'/v2/projects')
        for p in response.json():
            self.projects.append(GNS3Project(p['project_id']))

    @staticmethod
    def assert_version(version_string: str):
        """Checks if the server is running version corresponding to 'version_string'"""

        path = '/v2/version'
        data = json.dumps({'version': version_string})

        response = GNS3API.post_request(path, data)
        return response.ok

    def __str__(self):
        pretty_str = (f'\n'
                      f'GNS3 Controller API endpoint\n'
                      f'    Host    {GNS3API.base}\n'
                      f'    Version {self.version}\n'
                      f'    Running {len(self.computes)} Computes')
        return pretty_str + '\n'

    def __repr__(self):
        return 'GNS3Controller()'


class GNS3Project:
    def __init__(self, project_id):
        self.id = project_id
        response = GNS3API.get_request(f'/v2/projects/{self.id}')
        if response.ok:
            self._response = response.json()
            self.__dict__.update(Struct(**self._response).__dict__)

    def __str__(self):
        return 'GNS3Project settings:\n' + '\n'.join([f'    {k}: {v}' for k, v in self._response.items()]) + '\n'

    def __repr__(self):
        return f'GNS3Project(\'{self.id}\')'


class GNS3Compute:
    def __init__(self, compute_id):
        self.id = compute_id
        self.connected = False

        response = GNS3API.get_request(f'/v2/computes/{self.id}')
        if response.ok:
            self._response = response.json()
            # Pulling up the capabilities one level, makes more sense to me for now
            if self._response['connected']:
                self._response.update(self._response['capabilities'])
            del self._response['capabilities']

            self.__dict__.update(Struct(**self._response).__dict__)

    def images(self, emulator):
        images = []
        if self.connected:
            response = GNS3API.get_request(f'/v2/computes/{self.id}/{emulator}/images')
            if response.ok:
                for i in response.json():
                    images.append(GNS3Image(i))

        return images

    def __str__(self):
        return 'GNS3Compute settings:\n' + '\n'.join([f'    {k}: {v}' for k, v in self._response.items()]) + '\n'

    def __repr__(self):
        return f'GNS3Compute(\'{self.id}\')'


class GNS3VM:
    """Holds information on the GNS3 VM"""

    # TODO figure out what happens if the GNS3 VM is not configured / other issues
    def __init__(self):
        response = GNS3API.get_request(f'/v2/gns3vm')
        if response.ok:
            self._response = response.json()
            self.__dict__.update(Struct(**self._response).__dict__)

        self.engines = []
        response = GNS3API.get_request(f'/v2/gns3vm/engines')
        if response.ok:
            self._engines = response.json()
            for e in self._engines:
                self.engines.append(GNS3VMEngine(e))

    def __str__(self):
        return 'GNS3VM settings:\n' + '\n'.join([f'    {k}: {v}' for k, v in self._response.items()]) + '\n'

    def __repr__(self):
        return f'GNS3VM()'


class GNS3VMEngine:
    """Holds information on the GNS3 VM"""

    # TODO figure out what happens if the GNS3 VM is not configured / other issues
    def __init__(self, engine_info):

        self.__dict__.update(Struct(**engine_info).__dict__)

        self.vms = []
        response = GNS3API.get_request(f'/v2/gns3vm/engines/{self.engine_id}/vms')
        if response.ok:
            self._vms = response.json()
            for vm in self._vms:
                self.vms.append(vm['vmname'])

                # TODO Add __str__ and __repr__ for GNS3VMEngine


class GNS3Image:
    def __init__(self, image):
        self.__dict__.update(Struct(**image).__dict__)

        # TODO Add __str__ and __repr__ for GNS3Image


class Struct:
    """
    The Struct class is used to create a temporary nested object from json data. This allows
    for the dynamic import of attributes so whatever the underlying API spits out, you can use
    dot notation for accessing all (nested) members.
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)
        for k, v in self.__dict__.items():
            if isinstance(v, dict):
                setattr(self, k, Struct(**v))


if __name__ == '__main__':
    try:
        GNS3API.load_configuration()
        controller = GNS3Controller()
        print(controller)
        gns3vm = GNS3VM()
        print(gns3vm)
        print('Available Projects:')
        for project in controller.projects:
            print(f"    {project.name}")

        print('\nAvailable Computes:')
        for compute in controller.computes:
            print(f"    {compute.name}")

        local = GNS3Compute('local')
        print(f'\nAvailable Dynamips images on {local.name}:')
        for image in local.images('dynamips'):
            print(f"    {image.filename}")

    except FileNotFoundError:
        print("No valid configuration file found.")
        exit(1)
