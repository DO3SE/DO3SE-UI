class Field:
    """
    A simple getter/setter container class
    """

    def __init__(self, get, set):
        self.get = get
        self.set = set

    def get(self):
        raise NotImplementedError

    def set(self, value):
        raise NotImplementedError


class FieldGroup:
    """
    A group of named getter/setter pairs
    """
    def __init__(self):
        """
        Create a blank field map
        """
        self._fields = dict()

    def add_field(self, name, field):
        """
        Add a getter/setter pair
        """
        self._fields[name] = field

    def set_values(self, values):
        """
        Set the values of fields that exist and have a new value supplied
        """
        for name, value in values.iteritems():
            if name in self._fields:
                self._fields[name].set(value)

    def get_values(self):
        """
        Get the values of all fields as a dict - the output of this method is
        the same form as set_values expects as an input.
        """
        return dict( (name, field.get()) for name, field in self._fields.iteritems() )

