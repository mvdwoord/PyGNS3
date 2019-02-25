import json

from pygns3.Compute import *
from pygns3.Project import *


class GNS3Controller:
    """
    Wrapper for the Controller API in GNS3. This is the central object which holds references to
    almost all other (collections of) objects in GNS3.
    """

    def __init__(self):

        # Set version attribute
        response = GNS3API.get_request('/version')
        self.version = response.json()['version']

        self.computes = []
        response = GNS3API.get_request(f'/computes')
        for p in response.json():
            self.computes.append(GNS3Compute(p['compute_id']))

        # TODO check empty projects corner case behaviour
        self.projects = []
        response = GNS3API.get_request(f'/projects')
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

        path = '/version'
        data = json.dumps({'version': version_string})

        response = GNS3API.post_request(path, data)
        return response.ok

    @staticmethod
    def debug():
        """Dump debug information to disk (debug directory in config directory)."""
        response = GNS3API.post_request('/debug', {})
        if response.status_code == 201:
            print('Debug information written to configuration directory')
        else:
            print(f'Failed to write debug information {response}')

    @staticmethod
    def shutdown():
        """Shutdown the local server"""
        response = GNS3API.post_request('/shutdown', {})
        if response.status_code == 201:
            print('Controller accepted the shutdown command')
        else:
            print(f'The server refused the command {response}')


def main():
    """Main entry point. Show some sane defaults."""
    try:
        GNS3API.load_configuration()
        try:
            project = GNS3Project.create('henktest', scene_height=500, scene_width=600)
            print(f'created project {project.name} with id: {project.project_id}')
        except ValueError as e:
            print(f'Failed to create project ({e})')
        print(project)
        print('Now trying to delete')
        project.delete()
        print('Now trynig to delete again')
        project.delete()
    except FileNotFoundError as e:
        print(str(e))


if __name__ == '__main__':
    main()
