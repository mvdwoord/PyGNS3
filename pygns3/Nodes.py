from telnetlib import Telnet

from pygns3.API import *
from pygns3.Struct import Struct


class GNS3Node:
    """Represents a node in a GNS3Project"""

    def __init__(self, node):
        self.name = None
        self._node = node
        self.project_id = node['project_id']
        self.node_id = node['node_id']
        self.__dict__.update(Struct(**node).__dict__)
        self.properties = GNS3NodeProperties(self._node['properties'])
        self.ports = [GNS3NodePort(p) for p in node['ports']]

        self.command_line = self._node['command_line']
        self.compute_id = None
        self.console = None
        self.console_host = self._node['console']
        self.console_type = self._node['console_type']
        self.first_port_name = self._node['first_port_name']
        self.node_type = self._node['node_type']
        self.status = self._node['status']

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
        """Return a GNS3Node object from project- and node id"""
        response = GNS3API.get_request(f'/projects/{project_id}/nodes/{node_id}').json()
        return cls(response)

    def port_name(self, adapter_number, port_number):
        """Return a port name (e.g. f0/0) given its adapter number/port number"""
        for port in self.ports:
            if (port.adapter_number == adapter_number) & (port.port_number == port_number):
                return port.short_name

        return 'Unknown'

    def start(self):
        GNS3API.post_request(f'/projects/{self.project_id}/nodes/{self.node_id}/start')
        if GNS3API.console_log_level == GNS3API.DEBUG:
            print(f'Node started. NodeID: {self.node_id}')
        self.status = 'started'

    def stop(self):
        GNS3API.post_request(f'/projects/{self.project_id}/nodes/{self.node_id}/stop')
        if GNS3API.console_log_level == GNS3API.DEBUG:
            print(f'Node stopped. NodeID: {self.node_id}')
        self.status = 'stopped'

    def toggle(self):
        if self.status == 'stopped':
            self.start()
        elif self.status == 'started':
            self.stop()
        else:
            raise NotImplementedError('Node.toggle has faced an invalid status, '
                                      'that it has not yet been implemented to handle')

    def execute(self, command):
        print(f'The command is: {command}')
        print(f'host: {self.console_host}')

        host = GNS3API.host
        port = self.console_host
        print(f'{host} {port}')
        conn = Telnet(host=host, port=port)
        conn.write(command)
        resp = conn.read_all()

        print(resp)

    def link_to(self, other):
        GNS3Link.create(node_a=self, node_b=other)

    def __add__(self, other):
        self.link_to(other)


class GNS3NodePort:
    """A port on a GNS3Node."""

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
        setting_items = [f'    {k:{max_key_width + 1}} {v}' for k, v in self._node_port.items()]
        settings = '\n'.join(setting_items) + '\n'
        return 'GNSNodePort:\n' + settings


class GNS3NodeProperties:
    """Property section of a GNS3Node settings"""

    def __init__(self, node_properties):
        self._node_properties = node_properties
        if GNS3API.console_log_level == GNS3API.DEBUG:
            print(Struct(**node_properties).__dict__)
        self.__dict__.update(Struct(**node_properties).__dict__)

    def __repr__(self):
        return f'GNS3NodeProperties({self._node_properties})'

    def __str__(self):
        max_key_width = max(map(len, self._node_properties.keys()))
        items = [f'    {k:{max_key_width + 1}} {v}' for k, v in self._node_properties.items()]
        settings = '\n'.join(items) + '\n'
        return 'GNSNodeProperties:\n' + settings + ''


class GNS3Link:
    """A link between two GNS3Node objects"""
    link_counter = 0

    def __init__(self, link):
        GNS3Link.link_counter += 1
        # raise AssertionError
        # print([n['node_id'] for n in link['nodes']])
        # raise AssertionError

        self._link = link
        self.project_id = link['project_id']
        self.link_id = link['link_id']
        self._nodes = link['nodes']
        # Instantiate GNS3Node objects to look up the pretty name of the ports
        # TODO review this mess (too-many-instance-attributes)
        self.from_node = GNS3Node.from_id(self.project_id, self._nodes[0]['node_id'])
        self.to_node = GNS3Node.from_id(self.project_id, self._nodes[1]['node_id'])
        self.from_adapter_number = self._nodes[0]['adapter_number']
        self.to_adapter_number = self._nodes[1]['adapter_number']
        self.from_port_number = self._nodes[0]['port_number']
        self.to_port_number = self._nodes[1]['port_number']
        self.from_port_name = self.from_node.port_name(self.from_adapter_number,
                                                       self.from_port_number)
        self.to_port_name = self.to_node.port_name(self.to_adapter_number,
                                                   self.to_port_number)
        self.__dict__.update(Struct(**link).__dict__)

    def __repr__(self):
        return f'GNS3link({self.project_id}, {self.link_id})'

    def __str__(self):
        max_key_width = max(map(len, self._link.keys()))
        link_settings = {k: v for (k, v) in self._link.items() if k != 'nodes'}
        setting_items = [f'    {k:{max_key_width + 1}} {v}' for k, v in link_settings.items()]
        settings = '\n'.join(setting_items) + '\n'
        from_port = f'{self.from_node.name} ({self.from_port_name})'
        to_port = f'{self.to_node.name} ({self.to_port_name})'
        return (f'GNS3Link settings:\n{settings}'
                f'    {"from":{max_key_width + 1}} {from_port}\n'
                f'    {"to":{max_key_width + 1}} {to_port}\n')

    @classmethod
    def create(cls, node_a, node_b):
        """ creates a new link object"""
        # TODO implement create link
        pass

        class NoFreePortsError(Exception):
            pass

        raise NoFreePortsError

    def delete(self):
        """Deletes a link"""
        # TODO implement delete link
        pass
