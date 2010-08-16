import wx

import model
import wxext
from util.ordereddict import OrderedDict


class Field:
    """Abstract base class for fields.

    Most of the UI consists of fields with labels, where the field is a single
    user-editable widget.  A correctly initialised :class:`Field` instance will
    have :attr:`label`, :attr:`field` and :attr:`other` widgets, corresponding
    to the 3 columns of :class:`FieldGroup`.  The different types of fields
    subclass this class; all arguments not handled by the constructor are passed
    through to :meth:`create_ui` which should be implemented in the subclass.

    :param parent:  Parent :class:`wx.Window` for widgets
    :param name:    Name of the field, to be used in field label
    """

    def __init__(self, parent, name, *args, **kwargs):
        self.parent = parent

        self.label = wx.StaticText(parent, label=name)
        self.field = None
        self.other = None

        self.create_ui(parent, *args, **kwargs)

    def create_ui(self, parent, *args, **kwargs):
        """Create other widgets for the field.
        
        The arguments accepted beyond *parent* are specific to each subclass of
        :class:`Field`.
        """
        raise NotImplementedError

    def get_value(self):
        """Get field value."""
        return self.field.GetValue()

    def set_value(self, value):
        """Set field value."""
        self.field.SetValue(value)


class TextField(Field):
    """Field using :class:`wx.TextCtrl`."""

    def create_ui(self, parent, initial=''):
        """Create :class:`wx.TextCtrl` instance with optional initial value."""
        self.field = wx.TextCtrl(parent)
        self.field.SetValue(initial)


class SpinField(Field):
    """Field using :class:`wx.SpinCtrl`."""

    def create_ui(self, parent, min=0, max=100, initial=0):
        """Create :class:`wx.SpinCtrl` instance with specified parameters."""
        self.field = wx.SpinCtrl(parent, min=min, max=max, initial=initial)


class FloatSpinField(Field):
    """Field using :class:`FloatSpin`."""

    def create_ui(self, parent, min=0, max=1, initial=0, step=0.1, digits=2):
        """Create :class:`FloatSpin` instance with specified parameters."""
        self.field = wxext.FloatSpin(parent, min_val=min, max_val=max, value=initial,
                                     increment=step, digits=digits)

    def get_value(self):
        """Get field value as a float."""
        return float(self.field.GetValue())


class ChoiceField(Field):
    """Field for choosing options using :class:`wx.Choice`."""

    def create_ui(self, parent, choices, default, choice_string=lambda x: x['name']):
        """Create :class:`wx.Choice` instance.

        Allow a user to choose between keys of the *choices* mapping, using the
        *choice_string* function to determing the choice string to present to
        the user for each choice.  To ensure consistent item ordering, *choices*
        should be an :class:`OrderedDict` instance; choices will be displayed in
        the order they are added to it.

        .. note::
            Values returned by *choice_string* must be unique within the field.
        """
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

    Fields are arranged in groups to make the UI less cluttered.  Each group of
    fields corresponds to a page on a :class:`wx.Treebook` (or something else
    implementing the same book API); this class extends :class:`wx.Panel` so
    it can be used as a book page directly.  :class:`OrderedDict` is also
    extended by this class so that fields are accessible via ``group[key]``.

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

    Most groups of fields are simply a list user-editable entries with labels,
    and this class is for those cases.  Either by specifying *fields* and/or by
    repeated calls to :meth:`add`, a list of fields are built up.  The fields
    are displayed in a grid format, with each row being ``field.label``,
    ``field.field`` and ``field.other``.

    :param fc:      :class:`FieldCollection` this group belongs to; used by
                    field groups which depend on fields in other groups
    :param parent:  :class:`wx.Window` parent (usually the book control)
    :param fields:  Iterable of ``(key, class, args, kwargs)`` tuples
                    representing fields
    """

    def __init__(self, fc, parent, fields=()):
        FieldGroup.__init__(self, fc, parent)

        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.sizer = wx.FlexGridSizer(cols=3, vgap=5, hgap=5)
        self.GetSizer().Add(self.sizer, 0, wx.EXPAND|wx.ALL, 5)

        for key, cls, args, kwargs in fields:
            self.add(key, cls, *args, **kwargs)

    def add(self, key, cls, *args, **kwargs):
        """Create a new field in the group.

        An instance of *cls* is created, passing all following arguments to
        the constructor (with *self*, the field group, as the first argument),
        and associated with *key*.
        """
        self[key] = cls(self, *args, **kwargs)
        self.sizer.Add(self[key].label, 0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(self[key].field, 0, wx.ALIGN_CENTER_VERTICAL)
        if self[key].other is None:
            self.sizer.AddSpacer(0)
        else:
            self.sizer.Add(self[key].other, 0, wx.ALIGN_CENTER_VERTICAL)


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
    + The field's value becomes a ``(value, disabled)`` pair.
    """
    class DisableableCls(cls):
        def create_ui(self, parent, *args, **kwargs):
            cls.create_ui(self, parent, *args, **kwargs)
            self.other = wx.CheckBox(parent, label=chklabel, style=wx.CHK_2STATE)
            self.other.Bind(wx.EVT_CHECKBOX, self.OnCheckbox_disable)

        def OnCheckbox_disable(self, evt):
            self.field.Enable(not self.other.IsChecked())

        def get_value(self):
            return (cls.get_value(self), self.other.GetValue())

        def set_value(self, value):
            cls.set_value(self, value[0])
            self.other.SetValue(value[1])

    return DisableableCls


_parameters_ui = (
    ('format', 'Input data format', SimpleFieldGroup, (), {}),
    ('siteloc', 'Location properties', SimpleFieldGroup, (), {'fields': (
        ('lat', FloatSpinField, ('Latitude (degrees North)', -90, 90, 50, 0.1, 3), {}),
        ('lon', FloatSpinField, ('Longitude (degrees East)', -180, 180, 0, 0.1, 3), {}),
        ('elev', SpinField, ('Elevation (m.a.s.l.)', -100, 5000, 0), {}),
        ('soil_tex', ChoiceField, ('Soil texture', model.soil_class_map, model.default_soil_class), {}),
        ('rsoil', SpinField, ('Rsoil', 1, 1000, 200), {}),
    )}),
    ('meas', 'Measurement data', SimpleFieldGroup, (), {'fields': (
        ('o3zr', SpinField, ('O3 measurement height (m)', 1, 200, 25), {}),
        ('o3_h', disableable(FloatSpinField, 'Same as target canopy'),
            ('O3 measurement canopy height (m)', 0.1, 100, 25, 0.1, 1), {}),
        ('uzr', SpinField, ('Wind speed measurement height (m)', 1, 200, 25), {}),
        ('u_h', disableable(FloatSpinField, 'Same as target canopy'),
            ('Wind speed measurement canopy height (m)', 0.1, 100, 25, 0.1, 1), {}),
        ('d_meas', FloatSpinField, ('Soil water measurement depth (m)', 0.1, 2, 0.5, 0.1, 1), {}),
    )}),
    ('vegchar', 'Vegetation characteristics', SimpleFieldGroup, (), {'fields': (
        ('h', FloatSpinField, ('Canopy height (h, m)', 0.1, 100, 25, 0.1, 1), {}),
        ('root', FloatSpinField, ('Root depth (root, m)', 0.1, 10, 1.2, 0.1, 1), {}),
        ('lm', FloatSpinField, ('Leaf dimension (Lm, m)', 0.01, 1, 0.05, 0.01, 2), {}),
        ('albedo', FloatSpinField, ('Albedo', 0.01, 0.99, 0.12, 0.01, 2), {}),
        ('gmax', SpinField, ('gmax', 1, 10000, 148), {}),
        ('gmorph', FloatSpinField, ('gmorph', 0.01, 1, 1, 0.01, 2), {}),
        ('fmin', FloatSpinField, ('fmin', 0.01, 0.99, 0.13, 0.01, 2), {}),
        ('rext', SpinField, ('External plant cuticle resistance (Rext, s/m)', 0, 20000, 2500), {}),
        ('y', FloatSpinField, ('Threshold Y for AFstY (nmol/m2/s)', 0.1, 100, 1.6, 0.1, 1), {}),
    )}),
    ('vegenv', 'Environmental response', SimpleFieldGroup, (), {'fields': (
        ('f_lightfac', FloatSpinField, ('light_a', 0.001, 0.999, 0.006, 0.001, 3), {}),
        ('t_min', SpinField, (u'Minimum temperature (T_min, \u00b0C)', -10, 100, 0), {}),
        ('t_opt', SpinField, (u'Optimum temperature (T_opt, \u00b0C)', -10, 100, 21), {}),
        ('t_max', SpinField, (u'Maximum temperature (T_max, \u00b0C)', -10, 100, 35), {}),
        ('vpd_max', FloatSpinField, ('VPD for max. g (VPD_max, kPa)', 0, 100, 1, 0.01, 2), {}),
        ('vpd_min', FloatSpinField, ('VPD for min. g (VPD_min, kPa)', 0, 100, 3.25, 0.01, 2), {}),
        ('vpd_crit', FloatSpinField, ('Critical daily VPD sum (VPD_crit, kPa)', 0, 1000, 1000, 1, 1), {}),
        ('swp_min', FloatSpinField, ('SWP for min. g (SWP_min, ???)', -6, 0, -1.25, 0.01, 2), {}),
        ('swp_max', FloatSpinField, ('SWP for max. g (SWP_max, ???)', -6, 0, -0.05, 0.01, 2), {}),
    )}),
    ('modelopts', 'Model options', SimpleFieldGroup, (), {'fields': (
        ('fo3', ChoiceField, ('fO3 calculation', model.fO3_calc_map, model.default_fO3_calc), {}),
        ('fxwp', ChoiceField, ('Soil water influence on Gsto', model.fXWP_calc_map, model.default_fXWP_calc), {}),
        ('lwp', ChoiceField, ('LWP calculation', model.LWP_calc_map, model.default_LWP_calc), {}),
        ('fswp', ChoiceField, ('fSWP calculation', model.fSWP_calc_map, model.default_fSWP_calc), {}),
    )}),
    ('unsorted', 'UNSORTED', SimpleFieldGroup, (), {'fields': (
        ('sgs', SpinField, ('Start of growing season (SGS, day of year)', 1, 365, 121), {}),
        ('egs', SpinField, ('End of growing season (EGS, day of year)', 1, 365, 273), {}),

        ('lai_a', FloatSpinField, ('LAI at SGS (LAI_a, m2/m2)', 0, 20, 0, 0.1, 1), {}),
        ('lai_b', FloatSpinField, ('First mid-season LAI (LAI_b, m2/m2)', 0, 20, 4, 0.1, 1), {}),
        ('lai_c', FloatSpinField, ('Second mid-season LAI (LAI_c, m2/m2)', 0, 20, 4, 0.1, 1), {}),
        ('lai_d', FloatSpinField, ('LAI at EGS (LAI_d, m2/m2)', 0, 20, 0, 0.1, 1), {}),
        ('lai_1', SpinField, ('Period from LAI_a to LAI_b (LAI_1, days)', 1, 100, 30), {}),
        ('lai_2', SpinField, ('Period from LAI_c to LAI_d (LAI_2, days)', 1, 100, 30), {}),
        ('sai', ChoiceField, ('SAI calculation', model.SAI_calc_map, model.default_SAI_calc), {}),

        ('fphen_a', FloatSpinField, ('Fphen at SGS (fphen_a)', 0, 1, 0, 0.1, 1), {}),
        ('fphen_b', FloatSpinField, ('First mid-season Fphen (fphen_b)', 0, 1, 1, 0.1, 1), {}),
        ('fphen_c', FloatSpinField, ('Second mid-season Fphen (fphen_c)', 0, 1, 1, 0.1, 1), {}),
        ('fphen_d', FloatSpinField, ('Third mid-season Fphen (fphen_d)', 0, 1, 1, 0.1, 1), {}),
        ('fphen_e', FloatSpinField, ('Fphen at EGS (fphen_e)', 0, 1, 0, 0.1, 1), {}),
        ('fphen_1', SpinField, ('Period from fphen_a to fphen_b (fphen_1, days)', 0, 200, 15), {}),
        ('fphen_lima', SpinField, ('Start of SWP limitation (fphen_limA, day of year)', 0, 365, 0), {}),
        ('fphen_2', SpinField, ('Period from fphen_b to fphen_c (fphen_2, days)', 0, 200, 1), {}),
        ('fphen_3', SpinField, ('Period from fphen_c to fphen_d (fphen_3, days)', 0, 200, 1), {}),
        ('fphen_limb', SpinField, ('End of SWP limitation (fphen_limB, day of year)', 0, 365, 0), {}),
        ('fphen_4', SpinField, ('Period from fphen_d to fphen_e (fphen_4, days)', 0, 200, 20), {}),

        ('leaf_fphen', ChoiceField, ('Leaf fphen calculation', model.leaf_fphen_calc_map, model.default_leaf_fphen_calc), {}),
        ('astart', SpinField, ('Start of O3 accumulation (Astart, day of year)', 1, 365, 153), {}),
        ('aend', SpinField, ('End of O3 accumulation (Aend, day of year)', 1, 365, 208), {}),
        ('leaf_fphen_a', FloatSpinField, ('Leaf fphen at Astart (leaf_fphen_a)', 0, 1, 0, 0.1, 1), {}),
        ('leaf_fphen_b', FloatSpinField, ('Leaf fphen mid-season (leaf_fphen_b)', 0, 1, 1, 0.1, 1), {}),
        ('leaf_fphen_c', FloatSpinField, ('Leaf fphen at Aend (leaf_fphen_c)', 0, 1, 0, 0.1, 1), {}),
        ('leaf_fphen_1', SpinField, ('Period from leaf_fphen_a to leaf_fphen_b (days)', 0, 300, 15), {}),
        ('leaf_fphen_2', SpinField, ('Period from leaf_fphen_b to leaf_fphen_c (days)', 0, 300, 30), {}),
    )}),
)


def create_parameters_ui(parent):
    fc = FieldCollection(parent, _parameters_ui)
    return fc
