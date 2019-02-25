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
