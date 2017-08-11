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
            # TODO manual input option?
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
            for candidate in platform_file_locations[system_platform]:
                print(candidate)
            raise FileNotFoundError('No Valid Configuration File Found')


class GNS3Controller:
    """
    Wrapper for the Controller API in GNS3. This is the central object which holds references to almost all other
    (collections of) objects in GNS3.
    """
    def __init__(self):

        try:
            response = get(f'{GNS3API.base}/v2/version', auth=GNS3API.cred)
            if response.ok:
                self.version = response.json()['version']
        except:
            raise
        self.computes = []
        try:
            response = get(f'{GNS3API.base}/v2/computes', auth=GNS3API.cred)
            if response.ok:
                self._computes = response.json()
                for p in self._computes:
                    self.computes.append(GNS3Compute(p['compute_id']))

        except:
            raise

        # TODO check empty projects behaviour
        self.projects = []
        try:
            response = get(f'{GNS3API.base}/v2/projects', auth=GNS3API.cred)
            if response.ok:
                self._projects = response.json()
                for p in self._projects:
                    self.projects.append(GNS3Project(p['project_id']))
        except:
            raise

    # noinspection PyMethodMayBeStatic
    def assert_version(self, version_string: str):
        """Checks if the server is running version corresponding to 'version_string'"""

        url = f'{GNS3API.base}/v2/version'
        post_data = json.dumps({'version': version_string})

        try:
            response = post(url, data=post_data, auth=GNS3API.cred)
            print("Response code: {}".format(response.status_code))
            if response.ok:
                return True
            else:
                return False
        except:
            raise

    def __str__(self):
        pretty_str = (f"\n"
                      f"GNS3 Controller API endpoint\n"
                      f"    Host    {GNS3API.base}\n"
                      f"    Version {self.version}\n"
                      f"    Running {len(self.computes)} Computes")

        return pretty_str + "\n"


class GNS3Project:
    def __init__(self, project_id):
        self.id = project_id
        try:
            response = get(f'{GNS3API.base}/v2/projects/{self.id}', auth=GNS3API.cred)
            if response.ok:
                self._response = response.json()
                self.__dict__.update(Struct(**self._response).__dict__)

        except:
            raise

    def __str__(self):
        return "GNS3Project settings:\n" + "\n".join([f'    {k}: {v}' for k, v in self._response.items()]) + "\n"


class GNS3Compute:
    def __init__(self, compute_id):
        self.id = compute_id
        self.connected = False
        try:
            response = get(f'{GNS3API.base}/v2/computes/{self.id}', auth=GNS3API.cred)
            if response.ok:
                self._response = response.json()
                if self._response['connected']:
                    self._response.update(self._response['capabilities'])
                del self._response['capabilities']

                self.__dict__.update(Struct(**self._response).__dict__)

        except:
            raise

    def images(self, emulator):
        images = []
        if self.connected:
            try:
                response = get(f'{GNS3API.base}/v2/computes/{self.id}/{emulator}/images', auth=GNS3API.cred)
                if response.ok:
                    for image in response.json():
                        images.append(GNS3Image(image))
            except:
                raise
        return images

    def __str__(self):
        return "GNS3Compute settings:\n" + "\n".join([f'    {k}: {v}' for k, v in self._response.items()]) + "\n"


class GNS3VM:
    """Holds information on the GNS3 VM"""
    # TODO figure out what happens if the GNS3 VM is not configured / other issues
    def __init__(self):
        try:
            response = get(f'{GNS3API.base}/v2/gns3vm', auth=GNS3API.cred)
            if response.ok:
                self._response = response.json()
                self.__dict__.update(Struct(**self._response).__dict__)
        except:
            raise

        self.engines = []
        try:
            response = get(f'{GNS3API.base}/v2/gns3vm/engines', auth=GNS3API.cred)
            if response.ok:
                self._engines = response.json()
                for e in self._engines:
                    self.engines.append(GNS3VMEngine(e))
        except:
            raise

    def __str__(self):
        return "GNS3VM settings:\n" + "\n".join([f'    {k}: {v}' for k, v in self._response.items()]) + "\n"


class GNS3VMEngine:
    """Holds information on the GNS3 VM"""
    # TODO figure out what happens if the GNS3 VM is not configured / other issues
    def __init__(self, engine_info):

        self.__dict__.update(Struct(**engine_info).__dict__)

        self.vms = []
        try:
            response = get(f'{GNS3API.base}/v2/gns3vm/engines/{self.engine_id}/vms', auth=GNS3API.cred)
            if response.ok:
                self._vms = response.json()
                for vm in self._vms:
                    self.vms.append(vm['vmname'])
        except:
            raise


class GNS3Image:
    def __init__(self, image):
        self.__dict__.update(Struct(**image).__dict__)


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


