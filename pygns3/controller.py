"""

"""
# TODO Create nice module docstring
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

    def __str__(self):
        max_key_width = max(map(len, self._response.keys()))
        return 'GNS3Compute settings:\n' + '\n'.join(
            [f'    {k:{max_key_width}} {v}' for k, v in self._response.items()]) + '\n'

    def __repr__(self):
        return f'GNS3Compute(\'{self.id}\')'

    def images(self, emulator):
        images = []
        if self.connected:
            response = GNS3API.get_request(f'/v2/computes/{self.id}/{emulator}/images')
            if response.ok:
                for i in response.json():
                    images.append(GNS3Image(i))

        return images


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

    def __repr__(self):
        return 'GNS3Controller()'

    def __str__(self):
        pretty_str = (f'\n'
                      f'GNS3 Controller API endpoint\n'
                      f'    Host    {GNS3API.base}\n'
                      f'    Version {self.version}\n'
                      f'    Found   {len(self.projects)} Projects\n'
                      f'    Running {len(self.computes)} Computes\n')
        return pretty_str

    @staticmethod
    def assert_version(version_string: str):
        """Checks if the server is running version corresponding to 'version_string'"""

        path = '/v2/version'
        data = json.dumps({'version': version_string})

        response = GNS3API.post_request(path, data)
        return response.ok

    @staticmethod
    def debug():
        """Dump debug information to disk (debug directory in config directory). Works only for local server"""
        response = GNS3API.post_request('/v2/debug', {})
        if response.status_code == 201:
            print('Debug information written to configuration directory')
        else:
            print(f'Failed to write debug information {response}')

    @staticmethod
    def shutdown():
        """Shutdown the local server"""
        response = GNS3API.post_request('/v2/shutdown', {})
        if response.status_code == 201:
            print('Controller accepted the shutdown command')
        else:
            print(f'The server refused the command {response}')


class GNS3Drawing:
    """An SVG object inside a project"""

    def __init__(self, drawing):
        self._drawing = drawing
        self.project_id = drawing['project_id']
        self.drawing_id = drawing['drawing_id']
        self.__dict__.update(Struct(**drawing).__dict__)

    def __repr__(self):
        return f'GNS3Drawing({self.project_id}, {self.drawing_id})'

    def __str__(self):
        max_key_width = max(map(len, self._drawing.keys()))
        settings = '\n'.join([f'    {k:{max_key_width + 1}} {v}' for k, v in self._drawing.items()]) + '\n'
        return 'GNS3Drawing:\n' + settings + ''

    @classmethod
    def create(cls):
        """ creates a new drawing object"""
        # TODO implement create drawing
        pass

    def delete(self):
        """Deletes a drawing"""
        # TODO implement delete drawing
        pass


class GNS3Link:
    """A link instance"""

    def __init__(self, link):
        self._link = link
        self.project_id = link['project_id']
        self.link_id = link['link_id']
        self._nodes = link['nodes']
        # Instantiate GNS3Node objects to look up the pretty name of the ports
        self.from_node = GNS3Node.from_id(self.project_id, self._nodes[0]['node_id'])
        self.to_node = GNS3Node.from_id(self.project_id, self._nodes[1]['node_id'])
        self.from_adapter_number = self._nodes[0]['adapter_number']
        self.to_adapter_number = self._nodes[1]['adapter_number']
        self.from_port_number = self._nodes[0]['port_number']
        self.to_port_number = self._nodes[1]['port_number']
        self.from_port_name = self.from_node.port_name(self.from_adapter_number, self.from_port_number)
        self.to_port_name = self.to_node.port_name(self.to_adapter_number, self.to_port_number)
        self.__dict__.update(Struct(**link).__dict__)

    def __repr__(self):
        return f'GNS3link({self.project_id}, {self.link_id})'

    def __str__(self):
        max_key_width = max(map(len, self._link.keys()))
        link_settings = {k: v for (k, v) in self._link.items() if k != 'nodes'}
        settings = '\n'.join([f'    {k:{max_key_width + 1}} {v}' for k, v in link_settings.items()]) + '\n'
        from_port = f'{self.from_node.name} ({self.from_port_name})'
        to_port = f'{self.to_node.name} ({self.to_port_name})'
        return (f'GNS3Link settings:\n{settings}'
                f'    {"from":{max_key_width + 1}} {from_port}\n'
                f'    {"to":{max_key_width + 1}} {to_port}\n')

    @classmethod
    def create(cls):
        """ creates a new link object"""
        # TODO implement create link
        pass

    def delete(self):
        """Deletes a link"""
        # TODO implement delete link
        pass


class GNS3Node:
    """Represents a node in a GNS3Project"""

    def __init__(self, node):
        self._node = node
        ports = node['ports']
        self.project_id = node['project_id']
        self.node_id = node['node_id']
        self.__dict__.update(Struct(**node).__dict__)
        self.properties = GNS3NodeProperties(self._node['properties'])
        self.ports = [GNS3NodePort(p) for p in ports]

    def __repr__(self):
        return f'GNS3Node({self._node})'

    def __str__(self):
        items = self._node
        items['ports'] = str(len(items['ports']))
        del items['properties']
        max_key_width = max(map(len, self._node.keys()))
        settings = '\n'.join([f'    {k:{max_key_width + 1}} {v}' for k, v in items.items()]) + '\n'
        return 'GNSNode settings:\n' + settings

    @classmethod
    def from_id(cls, project_id, node_id):
        response = GNS3API.get_request(f'/v2/projects/{project_id}/nodes/{node_id}').json()
        return cls(response)

    def port_name(self, adapter_number, port_number):
        for port in self.ports:
            if (port.adapter_number == adapter_number) & (port.port_number == port_number):
                return port.short_name

        return 'Unknown'


class GNS3NodePort:
    def __init__(self, node_port):
        self.adapter_number = None
        self.port_number = None
        self.short_name = None
        self._node_port = node_port
        self.__dict__.update(Struct(**node_port).__dict__)

    def __repr__(self):
        return f'GNS3NodePort({self._node_port})'

    def __str__(self):
        max_key_width = max(map(len, self._node_port.keys()))
        settings = '\n'.join([f'    {k:{max_key_width + 1}} {v}' for k, v in self._node_port.items()]) + '\n'
        return 'GNSNodePort:\n' + settings


class GNS3NodeProperties:
    def __init__(self, node_properties):
        self._node_properties = node_properties
        self.__dict__.update(Struct(**node_properties).__dict__)

    def __repr__(self):
        return f'GNS3NodeProperties({self._node_properties})'

    def __str__(self):
        max_key_width = max(map(len, self._node_properties.keys()))
        settings = '\n'.join([f'    {k:{max_key_width + 1}} {v}' for k, v in self._node_properties.items()]) + '\n'
        return 'GNSNodeProperties:\n' + settings + ''


class GNS3Project:
    def __init__(self, project_id):
        self.project_id = project_id
        self._load_settings()
        self._drawings = GNS3API.get_request(f'/v2/projects/{self.project_id}/drawings').json()
        self.drawings = [GNS3Drawing(d) for d in self._drawings]
        self._links = GNS3API.get_request(f'/v2/projects/{self.project_id}/links').json()
        self.links = [GNS3Link(l) for l in self._links]
        self._nodes = GNS3API.get_request(f'/v2/projects/{self.project_id}/nodes').json()
        self.nodes = [GNS3Node(n) for n in self._nodes]
        self._snapshots = GNS3API.get_request(f'/v2/projects/{self.project_id}/snapshots').json()
        self.snapshots = [GNS3Snapshot(s) for s in self._snapshots]

    def __repr__(self):
        return f'GNS3Project(\'{self.project_id}\')'

    def __str__(self):
        max_key_width = max(map(len, self._response.keys()))
        settings = '\n'.join([f'    {k:{max_key_width}} {v}' for k, v in self._response.items()]) + '\n'
        return ('GNS3Project settings:\n' + settings + ''
                                                       f'    drawings     {len(self.drawings)}\n'
                                                       f'    links        {len(self.links)}\n'
                                                       f'    nodes        {len(self.nodes)}\n'
                                                       f'    snapshots    {len(self.snapshots)}\n')

    def _load_settings(self):
        response = GNS3API.get_request(f'/v2/projects/{self.project_id}')
        if response.ok:
            self._response = response.json()
            self.__dict__.update(Struct(**self._response).__dict__)

    def add_drawing(self, drawing: GNS3Drawing):
        """adds a drawing to the project"""
        # TODO implement add_drawing
        pass

    def add_link(self, link: GNS3Link):
        """adds a link to the project"""
        # TODO implement add_link
        pass

    def add_snapshot(self, name):
        """Takes a snapshot of the project"""
        # TODO implement add_snapshot
        pass

    def close(self):
        """closes a project"""
        GNS3API.post_request(f'/v2/projects/{self.project_id}/close', data={})
        self._load_settings()

    def load(self, path):
        """loads a project (local only)"""
        # TODO this needs to be more robust / x-platform with libpath or something
        # TODO should this be a classmethod? probably yes. Investigate behaviour and check for its dual (unload)
        data = {"path": path}
        response = GNS3API.post_request(f'/v2/projects/load', data=data)
        if not response.ok:
            raise Exception('Unable to open project')

    def open(self):
        """opens a project"""
        GNS3API.post_request(f'/v2/projects/{self.project_id}/open', data={})
        self._load_settings()

    def start_all_nodes(self):
        GNS3API.post_request(f'/v2/projects/{self.project_id}/nodes/start', data={})
        self._load_settings()
        print('All nodes have been started.')

    def stop_all_nodes(self):
        GNS3API.post_request(f'/v2/projects/{self.project_id}/nodes/stop', data={})
        self._load_settings()
        print('All nodes have been stopped.')

    def suspend_all_nodes(self):
        GNS3API.post_request(f'/v2/projects/{self.project_id}/nodes/suspend', data={})
        self._load_settings()
        print('All nodes have been suspended.')

    # TODO Decide on naming functions which mimic keywords
    def import_project(self):
        """import a project"""
        # TODO Implement import_project function
        pass

    def export(self):
        """import a project"""
        # TODO Implement export function
        pass

    def duplicate(self):
        """import a project"""
        # TODO Implement duplicate function
        pass

    def get_file(self, file):
        """Get a file from a project. Beware you have warranty to be able to access only to file global to the
        project (for example README.txt) """
        # TODO Implement get_file function
        pass

    def write_file(self, file):
        """Write a file to a project"""
        # TODO Implement write_file function
        pass

    @classmethod
    def from_name(cls, name):
        """Returns a GNS3Project with `name`"""
        response = GNS3API.get_request('/v2/projects')
        all_projects = response.json()
        for p in all_projects:
            if p['name'] == name:
                return cls(p['project_id'])
        raise FileNotFoundError(f'No project found with name {name}')

        # TODO check out notifications and how to implement


class GNS3Snapshot:
    """Project snapshot"""

    def __init__(self, snapshot):
        self._snapshot = snapshot
        self.project_id = snapshot['project_id']
        self.snapshot_id = snapshot['snapshot_id']
        self.__dict__.update(Struct(**snapshot).__dict__)

    def __str__(self):
        max_key_width = max(map(len, self._snapshot.keys()))
        settings = '\n'.join([f'    {k:{max_key_width + 1}} {v}' for k, v in self._snapshot.items()]) + '\n'
        return 'GNS3Snapshot settings:\n' + settings + ''

    def __repr__(self):
        return f'GNS3Snapshot({self._snapshot})'


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
        max_key_width = max(map(len, self._response.keys()))
        return 'GNS3VM settings:\n' + '\n'.join(
            [f'    {k:{max_key_width}} {v}' for k, v in self._response.items()]) + '\n'

    def __repr__(self):
        return f'GNS3VM()'


class GNS3VMEngine:
    """Holds information on the GNS3 VM Engine"""

    # TODO Ask why GNS3VMEngine is not in API with an id.
    # e.g. /v2/gns3vm/engines/{engine_id}  Like most other objects.
    # TODO figure out what happens if the GNS3 VM is not configured / other issues
    def __init__(self, engine_info):

        self._engine_info = engine_info
        self.__dict__.update(Struct(**engine_info).__dict__)

        self.vms = []
        response = GNS3API.get_request(f'/v2/gns3vm/engines/{self.engine_id}/vms')
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


class GNS3Image:
    """An image available on a Compute node for a given emulator"""

    # TODO would also be easier and more consistent if you could request an image by id. Check with devs.
    def __init__(self, image):
        self.image = image
        self.__dict__.update(Struct(**image).__dict__)

    def __str__(self):
        max_key_width = max(map(len, self.image.keys()))
        return 'GNS3Image settings:\n' + '\n'.join(
            [f'    {k:{max_key_width}} {v}' for k, v in self.image.items()]) + '\n'

    def __repr__(self):
        return f'GNS3Image({self.image})'


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


def main():
    try:
        GNS3API.load_configuration()
        controller = GNS3Controller()
        print(controller)
    except FileNotFoundError as e:
        print(str(e))


if __name__ == '__main__':
    main()
