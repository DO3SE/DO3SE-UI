"""
While the :mod:`~do3se.fields` module provides the generic framework for
handling groups of fields, in reality most groups of fields have some special
behaviour.  The classes in this module encapsulate that special behaviour.
"""
import wx
import wx.lib.plot

import wxext
import model
import fields
from fields import EVT_VALUE_CHANGED, validate
import graphs
import resources


class ParameterGroup(fields.SimpleFieldGroup):
    """Group of parameters using :class:`~do3se.fields.SimpleFieldGroup`.
    
    Most of the groups start with the :class:`~do3se.fields.SimpleFieldGroup`
    layout containing parameters taken from :data:`do3se.model.paramdefs`
    filtered by group.  This class abstracts that one step further by
    defining the fields to use as the class data attribute :attr:`PARAMETERS`.
    """
    #: Parameters to use in the field group.  (Empty since this is the base
    #: class, but provided as an example of how to get the correct value.)
    #: Subclasses should set this appropriately.
    PARAMETERS = model.parameters_by_group(None)

    def __init__(self, *args, **kwargs):
        kwargs['fields'] = self.PARAMETERS
        fields.SimpleFieldGroup.__init__(self, *args, **kwargs)


class ParameterGroupWithPreview(ParameterGroup):
    """A parameter group with a preview canvas.

    A canvas is added to the field group's top-level sizer, and made available
    as the :attr:`preview` attribute.

    By default, :data:`~do3se.fields.EVT_VALUE_CHANGED` is bound to
    :meth:`update_preview` so that any changes in the group cause the preview
    to be updated.  If a preview depends on any other events then those should
    also be bound to :meth:`update_preview`.  :meth:`update_preview` is also
    called after :meth:`set_values`.

    .. attribute:: preview
        
        A :class:`wx.lib.plot.PlotCanvas` instance to use as a preview canvas.
    """
    def __init__(self, *args, **kwargs):
        ParameterGroup.__init__(self, *args, **kwargs)

        self.preview = wx.lib.plot.PlotCanvas(self)
        self.preview.SetEnableTitle(False)
        self.preview.SetEnableLegend(False)
        self.preview.SetSizeHints(minW=400, minH=200, maxH=200)
        self.GetSizer().AddStretchSpacer(1)
        self.GetSizer().Add(self.preview, 0, wx.EXPAND|wx.ALL, 5)

        self.Bind(EVT_VALUE_CHANGED, self.update_preview)

    def update_preview(self, evt):
        """Redraw the preview (should be overridden in subclass)."""
        raise NotImplementedError

    def set_values(self, values):
        """Update the preview when values are set."""
        ParameterGroup.set_values(self, values)
        self.update_preview(None)


class InputFormatParams(fields.FieldGroup):
    """Data file input format parameter group."""
    def __init__(self, fc, parent):
        fields.FieldGroup.__init__(self, fc, parent)

        self.SetSizer(wx.BoxSizer(wx.VERTICAL))

        self.GetSizer().Add(wxext.AutowrapStaticText(self, label='Hourly input '
            'data must match the format described in "Selected fields".  Ensure '
            'both field order and units are correct for the data file.',
            style=wx.ST_NO_AUTORESIZE),
            flag=wx.EXPAND|wx.GROW|wx.ALL, border=5)

        self['input_fields'] = fields.ColumnsSelectField(self, model.input_fields)
        self.GetSizer().Add(self['input_fields'].field, 1, wx.EXPAND|wx.ALL, 5)

        self['input_trim'] = fields.SpinField(self, 0, 10, 0)
        s = wx.BoxSizer(wx.HORIZONTAL)
        self.GetSizer().Add(s, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        s.Add(wx.StaticText(self, label='Number of lines to trim from ' + \
                            'beginning of file (e.g. for column headers)'),
              0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        s.Add(self['input_trim'].field, 0, wx.EXPAND)


    def validate(self):
        """Ensure that required input fields are selected."""
        errors = []
        
        req = [k for k,v in model.input_fields.iteritems() if v['required']]
        cols = set(self['input_fields'].get_value())
        missing = [k for k in req if k not in cols]

        validate(errors, len(missing) == 0,
                 'Required input fields missing: ' + ', '.join(missing))

        validate(errors, 'par' in cols or 'r' in cols,
                 'Required input fields missing: supply at least PAR or R')

        return errors


class SiteLocationParams(ParameterGroup):
    """Site location parameters group."""
    PARAMETERS = model.parameters_by_group('siteloc')

    def validate(self):
        errors = []

        validate(errors, not self['co2_constant'].get_value()['disabled']
                         or 'co2' in self.fc['format']['input_fields'].get_value(),
                 '"Ambient CO2" input field required when "Use input" selected ' + \
                 'for CO2 concentration')

        return errors


class MeasurementParams(ParameterGroup):
    """Measurement location parameters group."""
    PARAMETERS = model.parameters_by_group('meas')

    def __init__(self, *args, **kwargs):
        ParameterGroup.__init__(self, *args, **kwargs)
        bmp = resources.OzoneTransfer.GetBitmap()
        self.GetSizer().Add(wx.StaticBitmap(self, wx.ID_ANY, bmp,
                                            size=(bmp.GetWidth(), bmp.GetHeight())))


class VegCharParams(ParameterGroup):
    """Vegetation characteristics parameters group."""
    PARAMETERS = model.parameters_by_group('vegchar')


class VegEnvParams(ParameterGroup):
    """Vegetation environmental response parameters group."""
    PARAMETERS = model.parameters_by_group('vegenv')

    def __init__(self, *args, **kwargs):
        ParameterGroup.__init__(self, *args, **kwargs)
        bmp = resources.Functions.GetBitmap()
        self.GetSizer().Add(wx.StaticBitmap(self, wx.ID_ANY, bmp,
                                            size=(bmp.GetWidth(), bmp.GetHeight())))

    def validate(self):
        errors = []

        t_min, t_opt, t_max = self.extract('t_min', 't_opt', 't_max')
        validate(errors, t_min < t_max, 'T_min must be less than T_max')
        validate(errors, t_opt > t_min, 'T_opt must be greater than T_min')
        validate(errors, t_opt < t_max, 'T_opt must be less than T_max')

        return errors


class ModelOptionsParams(ParameterGroup):
    """Model options group."""
    PARAMETERS = model.parameters_by_group('modelopts')

    def __init__(self, *args, **kwargs):
        ParameterGroup.__init__(self, *args, **kwargs)
        self.GetSizer().Add(wxext.AutowrapStaticText(self, label='N.B. fLWP, '
            'fSWP and fPAW are always calculated.  "Soil water influence on '
            'Gsto" only controls which is used in the Gsto calculation.  fPAW '
            'is calculated assuming an upper threshold of 50% of maximum PAW.',
            style=wx.ST_NO_AUTORESIZE),
            flag=wx.EXPAND|wx.GROW|wx.ALL, border=5)
        # The first draw of the label is incorrect if this isn't done on win32
        self.Layout()


    def validate(self):
        errors = []

        validate(errors, not self['tleaf'].get_value() == 'input' or
                         'tleaf' in self.fc['format']['input_fields'].get_value(),
                 'Leaf temperature input field required by "Use input" method')

        return errors


class SeasonParams(ParameterGroupWithPreview):
    """Season parameters group.

    Has a graph previewing the LAI function.
    """
    PARAMETERS = model.parameters_by_group('season')

    def __init__(self, *args, **kwargs):
        ParameterGroupWithPreview.__init__(self, *args, **kwargs)

        self['sgs_egs_calc'].field.Bind(EVT_VALUE_CHANGED, self.update_disabled)
        self['sgs_egs_calc'].field.Bind(EVT_VALUE_CHANGED, self.update_sgs_egs)
        self.fc['siteloc']['lat'].field.Bind(EVT_VALUE_CHANGED,
                                             self.update_sgs_egs)
        self.fc['siteloc']['elev'].field.Bind(EVT_VALUE_CHANGED,
                                              self.update_sgs_egs)

        self.update_disabled(None)
        self.update_sgs_egs(None)

    @wxext.autoeventskip
    def update_preview(self, evt):
        gfx = wx.lib.plot.PlotGraphics([graphs.lai_preview(self.fc)],
                                       'LAI preview',
                                       'Day of year (dd)',
                                       'Leaf Area Index')
        self.preview.Draw(graphics=gfx)

    @wxext.autoeventskip
    def update_disabled(self, evt):
        """Disable SGS/EGS inputs if they're not being used."""
        enabled = self['sgs_egs_calc'].get_value() == 'inputs'
        self['sgs'].field.Enable(enabled)
        self['egs'].field.Enable(enabled)

    @wxext.autoeventskip
    def update_sgs_egs(self, evt):
        """Keep SGS/EGS up to date when following latitude function."""
        if self['sgs_egs_calc'].get_value() == 'latitude':
            lat = self.fc['siteloc']['lat'].get_value()
            elev = self.fc['siteloc']['elev'].get_value()
            sgs, egs = model.phenology.latitude_sgs_egs(lat, elev)
            self['sgs'].set_value(sgs)
            self['egs'].set_value(egs)
            # Propagate changes, e.g. to preview graphs
            self['sgs'].OnChanged(None)
            self['egs'].OnChanged(None)

    def set_values(self, values):
        """Ensure the enabled/disabled states and SGS/EGS are updated."""
        ParameterGroupWithPreview.set_values(self, values)
        self.update_disabled(None)
        self.update_sgs_egs(None)

    def validate(self):
        errors = []

        sgs, egs, lai_1, lai_2 = self.extract('sgs', 'egs', 'lai_1', 'lai_2')

        validate(errors, sgs < egs, 'SGS must be before EGS')
        validate(errors, (sgs + lai_1) <= (egs - lai_2),
                 'SGS + LAI_1 cannot be later than EGS - LAI_2')

        return errors


class FphenParams(ParameterGroupWithPreview):
    """Canopy Fphen parameters group.

    Has a graph previewing the fphen function.  Also depends on ``sgs`` and
    ``egs`` from the season parameters group.
    """
    PARAMETERS = model.parameters_by_group('fphen')

    def __init__(self, *args, **kwargs):
        ParameterGroupWithPreview.__init__(self, *args, **kwargs)
        
        # TODO: This will need to happen somewhere else if the panels are in
        # a different order...
        self.fc['season']['sgs'].field.Bind(EVT_VALUE_CHANGED, self.update_preview)
        self.fc['season']['egs'].field.Bind(EVT_VALUE_CHANGED, self.update_preview)

    @wxext.autoeventskip
    def update_preview(self, evt):
        gfx = wx.lib.plot.PlotGraphics([graphs.fphen_preview(self.fc)],
                                       'Fphen preview',
                                       'Day of year (dd)',
                                       'Fphen')
        self.preview.Draw(graphics=gfx)

    def validate(self):
        errors = []

        sgs, egs = self.fc['season'].extract('sgs', 'egs')
        fphen_1, fphen_2, fphen_3, fphen_4 = self.extract('fphen_1', 'fphen_2',
                                                          'fphen_3', 'fphen_4')
        fphen_a, fphen_b, fphen_c = self.extract('fphen_a', 'fphen_b', 'fphen_c')
        fphen_d, fphen_e = self.extract('fphen_d', 'fphen_e')
        fphen_lima, fphen_limb = self.extract('fphen_lima', 'fphen_limb')

        validate(errors, (sgs + fphen_1) <= (egs - fphen_4),
                'SGS + fphen_1 cannot be later than EGS - fphen_4')

        if fphen_lima > 0 or fphen_limb > 0:
            validate(errors, fphen_lima > (sgs + fphen_1),
                    'fphen_limA must be after SGS + fphen_1')
            validate(errors, fphen_limb > fphen_lima,
                    'fphen_limB must be after fphen_limA')
            validate(errors, fphen_limb < (egs - fphen_4),
                    'fphen_limB must be before EGS - fphen_4')

        return errors


class LeafFphenParams(ParameterGroupWithPreview):
    """Leaf fphen parameters group.

    Has a graph previewing the leaf fphen function.  Also depends on ``sgs`` and
    ``egs`` from the season parameters group, plus everything in the Fphen group
    (since it might be following the canopy fphen calculation).
    """
    PARAMETERS = model.parameters_by_group('leaf_fphen')

    def __init__(self, *args, **kwargs):
        ParameterGroupWithPreview.__init__(self, *args, **kwargs)

        # TODO: This will need to happen somewhere else if the panels are in
        # a different order...
        self.fc['season']['sgs'].field.Bind(EVT_VALUE_CHANGED, self.update_preview)
        self.fc['season']['egs'].field.Bind(EVT_VALUE_CHANGED, self.update_preview)
        # Might be following Fphen instead of leaf_fphen
        self.fc['fphen'].Bind(EVT_VALUE_CHANGED, self.update_preview)

        self['leaf_fphen'].field.Bind(EVT_VALUE_CHANGED, self.update_disabled)
        self.update_disabled(None)

    def set_values(self, values):
        """Ensure the enabled/disabled state gets updated when values are set."""
        ParameterGroupWithPreview.set_values(self, values)
        self.update_disabled(None)
        
    @wxext.autoeventskip
    def update_preview(self, evt):
        gfx = wx.lib.plot.PlotGraphics([graphs.leaf_fphen_preview(self.fc)],
                                       'Leaf fphen preview',
                                       'Day of year (dd)',
                                       'leaf_fphen')
        self.preview.Draw(graphics=gfx)

    @wxext.autoeventskip
    def update_disabled(self, evt):
        """Disable input fields when following canopy Fphen."""
        enabled = self['leaf_fphen'].get_value() == 'fixedday'
        for field in self.itervalues():
            if field is not self['leaf_fphen']:
                field.field.Enable(enabled)
        # Hide preview graph if not using a graphable method
        self.preview.Show(enabled)
        self.preview.GetContainingSizer().Layout()

    def validate(self):
        errors = []

        validate(errors, not self['leaf_fphen'].get_value() == 'input' or
                         'leaf_fphen_input' in self.fc['format']['input_fields'].get_value(),
                 'Leaf fphen input field required by "Use input" leaf fphen method')

        return errors
