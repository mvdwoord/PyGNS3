from pygns3.Struct import Struct


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
        setting_items = [f'    {k:{max_key_width + 1}} {v}' for k, v in self._drawing.items()]
        settings = '\n'.join(setting_items) + '\n'
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


class GNS3Image:
    """An image available on a Compute node for a given emulator"""

    # TODO would also be easier if you could request an image by id. Check with devs.
    def __init__(self, image):
        self.image = image
        self.__dict__.update(Struct(**image).__dict__)

    def __str__(self):
        max_key_width = max(map(len, self.image.keys()))
        return 'GNS3Image settings:\n' + '\n'.join(
            [f'    {k:{max_key_width}} {v}' for k, v in self.image.items()]) + '\n'

    def __repr__(self):
        return f'GNS3Image({self.image})'
