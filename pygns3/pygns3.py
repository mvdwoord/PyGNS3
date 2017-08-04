import json
import platform
from pathlib import Path
from configparser import ConfigParser
from requests import get, post
from requests.auth import HTTPBasicAuth


def gns3_server_conf(section='Server'):
    """
    The GNS3 Server (/Controller) is configured through the gns3_server.conf file.
    GNS3 searches various locations depending on the platform. These locations are listed in the documentation
            DOCUMENTATION   /   GNS3 SERVER CONFIGURATION FILE
            http://docs.gns3.com/1f6uXq05vukccKdMCHhdki5MXFhV8vcwuGwiRvXMQvM0/
    :return:
        GNS3 Configuration (type tbd)
    """
    platform_filelocations = {
        'Darwin': [
            str(Path.home()) + "/.config/GNS3/gns3_server.conf",
            "./gns3_server.conf"
        ]
        # TODO add Linux/Windows file locations and test.
    }
    system_platform = platform.system()
    if system_platform not in platform_filelocations.keys():
        raise OSError

    # TODO verify behaviour ConfigParser vs GNS3 (i.e. does it merge files or is there precedence (presidents?)
    parser = ConfigParser()
    found = parser.read(platform_filelocations[system_platform])
    if found and section in parser.sections():
        return dict(parser.items(section))
    else:
        for candidate in platform_filelocations[system_platform]:
            print(candidate)
        raise FileNotFoundError


class GNS3Controller:
    """
    Wrapper for the Controller API in GNS3
    """
    def __init__(self, conf=gns3_server_conf()):
        """
        Takes a dict holding the [Server] section from the gns3_server.conf file
        :type conf: dict
        """
        self._configuration = conf
        self._host = conf['host']
        self._port = conf['port']
        self._user = conf['user']
        self._password = conf['password']
        self._credentials = HTTPBasicAuth(self._user, self._password)
        try:
            response = get('http://{}:{}/v2/version'.format(self._host, self._port), auth=self._credentials)
            if response.ok:
                self._version = response.json()
                self.version = self._version['version']
        except:
            raise

        try:
            response = get('http://{}:{}/v2/computes'.format(self._host, self._port), auth=self._credentials)
            if response.ok:
                self.computes = response.json()

        except:
            raise

        # TODO check empty projects behaviour
        self._projects = []
        try:
            response = get('http://{}:{}/v2/projects'.format(self._host, self._port), auth=self._credentials)
            if response.ok:
                self._projects = response.json()
        except:
            raise

    def assert_version(self, version_string: str):
        """Checks if the server is running version"""

        url = 'http://{}:{}/v2/version'.format(self._host, self._port)
        post_data = json.dumps({'version': version_string})

        try:
            response = post(url, data=post_data, auth=self._credentials)
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
    Host    {}:{}
    Version {}
    Running {} Computes""".format(self._host,
                                  self._port,
                                  self._version['version'],
                                  len(self.computes))
        for compute in self.computes:
            pretty_str += """
        {}""".format(compute['name'])

        pretty_str += """
        
Projects folder {}""".format(self._configuration['projects_path'])
        for project in self._projects:
            pretty_str += """
    {}""".format(project['name'])

        return pretty_str


if __name__ == '__main__':
    try:
        controller = GNS3Controller()

    except FileNotFoundError:
        print("No valid configuration file found.")
        exit(1)

    print(controller)
