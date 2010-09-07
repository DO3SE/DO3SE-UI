import wx

import wxext
from util import OrderedDict


class Field:
    """Abstract base class for fields.

    The :class:`Field` class and its descendants expose a consistent
    :meth:`get_value`/:meth:`set_value` interface across various types of input
    controls.  A :class:`Field` object should have :attr:`field` and
    :attr:`other` attributes which may either be None or some :class:`wx.Widget`
    that is a child of *parent*.
    """
    def __init__(self, parent):
        self.parent = parent
        self.field = None
        self.other = None

    def get_value(self):
        """Get the field value (assuming a simple wx control)."""
        return self.field.GetValue()

    def set_value(self, value):
        """Set the field value (assuming a simple wx control)."""
        self.field.SetValue(value)


class TextField(Field):
    """Field using :class:`wx.TextCtrl`."""
    def __init__(self, parent, initial=''):
        Field.__init__(self, parent)

        self.field = wx.TextCtrl(parent)
        self.field.SetValue(initial)


class SpinField(Field):
    """Field using :class:`wx.SpinCtrl`."""
    def __init__(self, parent, min=0, max=100, initial=0):
        Field.__init__(self, parent)

        self.field = wx.SpinCtrl(parent, min=min, max=max, initial=initial)


class FloatSpinField(Field):
    """Field using :class:`FloatSpin`."""
    def __init__(self, parent, min=0, max=1, initial=0, step=0.1, digits=2):
        Field.__init__(self, parent)

        self.field = wxext.FloatSpin(parent, min_val=min, max_val=max, value=initial,
                                     increment=step, digits=digits)

    def get_value(self):
        """Get field value as a float."""
        return float(self.field.GetValue())


class ChoiceField(Field):
    """Field for choosing options using :class:`wx.Choice`.

    Allow a user to choose between keys of the *choices* mapping, using the
    *choice_string* function to determing the choice string to present to
    the user for each choice.  To ensure consistent item ordering, *choices*
    should be an :class:`OrderedDict` instance; choices will be displayed in
    the order they are added to it.

    .. note::
        Values returned by *choice_string* must be unique within the field.
    """
    def __init__(self, parent, choices, default, choice_string=lambda x: x['name']):
        Field.__init__(self, parent)

        self.choices = choices
        self._choice_string = choice_string

        self.field = wx.Choice(parent)
        for key, choice in self.choices.iteritems():
            # Use wx.Choice's "clientdata" field for each choice so it is simple
            # to retrieve the key corresponding to the selected choice.
            self.field.Append(self._choice_string(choice), key)

        self.set_value(default)

    def get_value(self):
        """Get the value corresponding to the selected choice."""
        return self.field.GetClientData(self.field.GetSelection())

    def set_value(self, key):
        """Set the selected choice to be that corresponding to *key*."""
        self.field.SetStringSelection(self._choice_string(self.choices[key]))


class FieldGroup(OrderedDict, wx.Panel):
    """Base class for groups of fields.

    Fields are arranged into logical groups.  This class provides a way to
    get/set the values of the whole group of fields at once.  Each group
    corresponds to a page on a book control (e.g. :class:`wx.Treebook`), so
    this class extends :class:`wx.Panel` so it can be added to the book control
    directly.

    :class:`OrderedDict` is also extended so that fields can be added and
    accessed via the dictionary interface (e.g. ``group[key].get_value()``).

    Any concrete subclass of :class:`FieldGroup` should add fields to itself
    via the dict API.  Alternatively, :meth:`get_values` and :meth:`set_values`
    should be overloaded for the desired internal functionality while keeping
    the same external behaviour.

    :param fc:      :class:`FieldCollection` this group belongs to; used by
                    field groups which depend on fields in other groups
    :param parent:  :class:`wx.Window` parent (usually the book control)
    """

    def __init__(self, fc, parent):
        OrderedDict.__init__(self)
        wx.Panel.__init__(self, parent)

        self.fc = fc

    def get_values(self):
        """Return field group as :class:`OrderedDict` of values."""
        return OrderedDict((k, v.get_value()) for k,v in self.iteritems())

    def set_values(self, values):
        """Update field group with :class:`OrderedDict` of values.
        
        .. note::
            Values for keys which do not exist in the group ar ignored,
            rather than raising errors; values for other groups may be present
            in *values*.
        """
        for k,v in values.iteritems():
            if k in self:
                self[k].set_value(v)


class SimpleFieldGroup(FieldGroup):
    """Simple group of fields in a grid.

    Most groups of fields are simply a list of user-editable entries with
    labels, and this class is for those cases.  Either by specifying *fields*
    and/or by repeated calls to :meth:`add`, a list of fields is built up.
    The fields in question are field definitions from
    :data:`do3se.model.fields`, and are displayed in a grid format with each row
    containing a label (from ``field['name']``) and the :attr:`field` and
    :attr:`other` attributes of an instance of ``field['cls']``.

    :param fc:      :class:`FieldCollection` this group belongs to; used by
                    field groups which depend on fields in other groups
    :param parent:  :class:`wx.Window` parent (usually the book control)
    :param fields:  Iterable of field definitions
    """
    def __init__(self, fc, parent, fields=()):
        FieldGroup.__init__(self, fc, parent)

        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.sizer = wx.FlexGridSizer(cols=3, vgap=5, hgap=5)
        self.GetSizer().Add(self.sizer, 0, wx.EXPAND|wx.ALL, 5)

        for field in fields:
            self.add(field)

    def add(self, field):
        """Create a new field in the group."""
        self[field['variable']] = field['cls'](self, *field['args'])
        self.sizer.Add(wx.StaticText(self, label=field['name']),
                       0, wx.ALIGN_CENTER_VERTICAL)
        self._add_widget_or_spacer(self[field['variable']].field)
        self._add_widget_or_spacer(self[field['variable']].other)

    def _add_widget_or_spacer(self, widget):
        if widget is None:
            self.sizer.AddSpacer(0)
        else:
            self.sizer.Add(widget, 0, wx.ALIGN_CENTER_VERTICAL)


class FieldCollection(OrderedDict):
    """Collection of fields, split into field groups.

    Provides an interface to get and set the values of all fields, while the
    fields themselves are broken up into groups for UI purposes.  Groups can be
    added through the *groups* argument and/or through repeated calls to
    :meth:`add_group`.  Groups are stored as an :class:`OrderedDict`, so they
    can be accessed with ``collection[groupkey]``, and fields with
    ``collection[groupkey][fieldkey]``.

    :param treebook:    The :class:`wx.Treebook` that contains the field groups
    :param groups:      Iterable of ``(key, name, class, args, kwargs)`` tuples
                        representing field groups
    """

    def __init__(self, treebook, groups=()):
        OrderedDict.__init__(self)
        self.treebook = treebook

        for key, name, cls, args, kwargs in groups:
            self.add_group(key, name, cls, *args, **kwargs)

    def add_group(self, key, name, cls, *args, **kwargs):
        """Create a new field group.
        
        An instance of *cls* is created, passing all following arguments to the
        constructor (with *self* and the parent treebook passed first), and 
        associated with *key*.
        """
        self[key] = cls(self, self.treebook, *args, **kwargs)
        self.treebook.AddPage(self[key], name)
        return self[key]

    def get_values(self):
        """Get the values of all fields, across all groups, as an :class:`OrderedDict`."""
        values = OrderedDict()
        for group in self.itervalues():
            values.update(group.get_values())
        return values

    def set_values(self, values):
        """Set the values of all fields from an :class:`OrderedDict`.

        All groups get given *values*, so groups should ignore values for fields
        they do not contain.
        """
        for group in self.itervalues():
            group.set_values(values)


def disableable(cls, chklabel='Disabled?'):
    """Class decorator creating a new class with an added "disable" checkbox.

    This decorator creates a new class which inherits from *cls*, making the
    following changes:

    + ``field.other`` becomes a checkbox with *chklabel* as it's label,
    + The field's value becomes a dict with ``value`` and ``disabled`` keys.
    """
    class DisableableCls(cls):
        def __init__(self, parent, *args, **kwargs):
            cls.__init__(self, parent, *args, **kwargs)
            self.other = wx.CheckBox(parent, label=chklabel, style=wx.CHK_2STATE)
            self.other.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_disable)

        @wxext.autoeventskip
        def OnCheckbox_disable(self, evt):
            self.field.Enable(not self.other.IsChecked())

        def get_value(self):
            return dict(value=cls.get_value(self), disabled=self.other.GetValue())

        def set_value(self, value):
            cls.set_value(self, value['value'])
            self.other.SetValue(value['disabled'])

    return DisableableCls
