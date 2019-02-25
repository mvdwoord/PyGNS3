from pygns3.Nodes import *


class GNS3Link:
    """A link between two GNS3Node objects"""

    def __init__(self, link):
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
    def create(cls):
        """ creates a new link object"""
        # TODO implement create link
        pass

    def delete(self):
        """Deletes a link"""
        # TODO implement delete link
        pass
