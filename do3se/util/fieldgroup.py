class Field:
    """
    Create a field from an arbitrary object.

    The Field class contains an arbitrary object along with a getter and setter.
    The getter and setter should be set either by supplying them as arguments to
    the constructor or by overriding the methods directly:

    >>> f = Field(foo)
    >>> f.get = lambda: foo.GetValue()
    >>> f.set = lambda value: foo.SetValue(value)

    Overriding them in subclasses for specific types of fields is also possible.
    :attr:`obj` is a reference to the wrapped object, for situations where the
    original object is needed.

    This class implements the "class decorator" pattern, so in most cases all
    attribute access (excluding :attr:`obj`, :meth:`get` and :meth:`set`) will
    pass through to the contained object.
    
    .. note::
        
        wxPython will agressively check that an object is a ``wx.Widget``
        instance, and therefore it is necessary to pass :attr:`obj` to wxPython
        functions.
    """

    def __init__(self, obj, getter=None, setter=None):
        """
        Store the object, and the getter and setter if supplied.
        """
        self._obj = obj
        if getter: self.get = getter
        if setter: self.set = setter

    def __getattr__(self, name):
        """
        Pass all attribute access (other than :attr:`obj`/:meth:`get`/:meth:`set`)
        through to the contained object.
        """
        return getattr(self.obj, name)

    @property
    def obj(self):
        """
        Expose contained object as a read-only property.
        """
        return self._obj

    def get(self):
        """
        Get the field value.

        This should be replaced either in a subclass or by assigning it to some function.
        """
        raise NotImplementedError

    def set(self, value):
        """
        Set the field value.

        This should be replaced either in a subclass or by assigning it to some function.
        """
        raise NotImplementedError



class FieldGroup:
    """
    A group of named :class:`Field` objects.
    """

    def __init__(self):
        """
        Constructor

        Create a dict to hold the fields.
        """
        self._fields = dict()

    
    def add(self, name, field):
        """
        Add a field to the group.
        """
        self._fields[name] = field


    def remove(self, name):
        """
        Remove a field from the group.
        """
        if name in self._fields: del self._fields[name]


    def get_values(self):
        """
        Get the values of all fields as a dict.
        """
        return dict( (name, f.get()) for name, f in self._fields.iteritems() )

    
    def set_values(self, values):
        """
        Set the values of all fields which exist and have a new value supplied.
        """
        for name, value in values.iteritems():
            if name in self._fields:
                self._fields[name].set(value)


    def __getitem__(self, name):
        """
        Implement read-only access to the field dict.
        """
        return self._fields[name]


class wxField(Field):
    """
    Generic wxPython field.
    
    Getter and setter use ``obj.GetValue`` and ``obj.SetValue`` respectively.
    """
    def get(self):
        return self.obj.GetValue()

    def set(self, value):
        self.obj.SetValue(value)


class wxFloatField(wxField):
    """
    Same as :class:`wxField`, but with an explicit cast to float on :meth:`get`.
    """
    def get(self):
        return float(self.obj.GetValue())
