import json
import platform
from configparser import ConfigParser
from pathlib import Path
from requests import get, post
from requests.auth import HTTPBasicAuth

__all__ = ['GNS3Project', 'GNS3Controller']


class CONFIGURATION:
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
    user = None


def gns3_server_conf(section='Server'):
    """
    The GNS3 Server (/Controller) is configured through the gns3_server.conf file.
    GNS3 searches various locations depending on the platform. These locations are listed in the documentation
            DOCUMENTATION   /   GNS3 SERVER CONFIGURATION FILE
            http://docs.gns3.com/1f6uXq05vukccKdMCHhdki5MXFhV8vcwuGwiRvXMQvM0/
    :return:
        GNS3 Configuration as dict
    """
    platform_file_locations = {
        'Darwin': [
            str(Path.home()) + "/.config/GNS3/gns3_server.conf",
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
        return dict(parser.items(section))
    else:
        for candidate in platform_file_locations[system_platform]:
            print(candidate)
        raise FileNotFoundError('No Valid Configuration File Found')


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


class GNS3Controller:
    """
    Wrapper for the Controller API in GNS3
    """
    def __init__(self):
        """
        Initializes the GNS3Controller object
        """
        try:
            _configuration = gns3_server_conf()
            for k, v in _configuration.items():
                setattr(CONFIGURATION, k, v)
        except FileNotFoundError:
            print()

        CONFIGURATION.cred = HTTPBasicAuth(CONFIGURATION.user, CONFIGURATION.password)
        CONFIGURATION.base = 'http://{}:{}'.format(CONFIGURATION.host, str(CONFIGURATION.port))
        try:
            response = get('{}/v2/version'.format(CONFIGURATION.base), auth=CONFIGURATION.cred)
            if response.ok:
                self._version = response.json()
                self.version = self._version['version']
        except:
            raise

        try:
            response = get('{}/v2/computes'.format(CONFIGURATION.base), auth=CONFIGURATION.cred)
            if response.ok:
                self.computes = response.json()

        except:
            raise

        # TODO check empty projects behaviour
        self.projects = []
        try:
            response = get('{}/v2/projects'.format(CONFIGURATION.base), auth=CONFIGURATION.cred)
            if response.ok:
                self._projects = response.json()
                for p in self._projects:
                    self.projects.append(GNS3Project(p['project_id']))
        except:
            raise

    # noinspection PyMethodMayBeStatic
    def assert_version(self, version_string: str):
        """Checks if the server is running version corresponding to 'version_string'"""

        url = '{}/v2/version'.format(CONFIGURATION.base)
        post_data = json.dumps({'version': version_string})

        try:
            response = post(url, data=post_data, auth=CONFIGURATION.cred)
            print("Response code: {}".format(response.status_code))
            if response.ok:
                return True
            else:
                return False
        except:
            raise

    def __str__(self):
        """
        Not sure if there is a nicer / more pythonic way to do this.
        """
        pretty_str = """
GNS3 Controller API endpoint
    Host    {}
    Version {}
    Running {} Computes""".format(CONFIGURATION.base,
                                  self._version['version'],
                                  len(self.computes))
        for compute in self.computes:
            pretty_str += """
        {}""".format(compute['name'])

        pretty_str += """
        
Projects folder {}""".format(CONFIGURATION.projects_path)
        for project in self.projects:
            pretty_str += """
    {}""".format(project.name)

        return pretty_str


class GNS3Project:
    def __init__(self, project_id):
        self.id = project_id
        try:
            response = get('{}/v2/projects/{}'.format(CONFIGURATION.base, self.id), auth=CONFIGURATION.cred)
            if response.ok:
                self._response = response.json()
                self.__dict__.update(Struct(**self._response).__dict__)

        except:
            raise
    pass

if __name__ == '__main__':
    try:
        controller = GNS3Controller()
        print(controller)
    except FileNotFoundError:
        print("No valid configuration file found.")
        exit(1)


