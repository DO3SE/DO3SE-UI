"""
While the :mod:`~do3se.fields` module provides the generic framework for
handling groups of fields, in reality most groups of fields have some special
behaviour.  The classes in this module encapsulate that special behaviour.
"""
import wx
import wx.lib.plot

import wxext
import model
from fields import *
import graphs


class ParameterGroup(SimpleFieldGroup):
    """Group of parameters using :class:`~do3se.fields.SimpleFieldGroup`.
    
    Most of the groups start with the :class:`~do3se.fields.SimpleFieldGroup`
    layout containing parameters taken from :data:`do3se.model.parameters`
    filtered by group.  This class abstracts that one step further by
    defining the fields to use as the class data attribute :attr:`PARAMETERS`.
    """
    #: Parameters to use in the field group.  (Empty since this is the base
    #: class, but provided as an example of how to get the correct value.)
    #: Subclasses should set this appropriately.
    PARAMETERS = model.parameters_by_group(None)

    def __init__(self, *args, **kwargs):
        kwargs['fields'] = self.PARAMETERS
        SimpleFieldGroup.__init__(self, *args, **kwargs)


class PreviewCanvasMixin:
    """Add a preview canvas to a field group.

    A canvas is added to the field group's top-level sizer, and made available
    as the :attr:`preview` attribute.

    By default, :data:`~do3se.fields.EVT_VALUE_CHANGED` is bound to
    :meth:`update_preview` so that any changes in the group cause the preview
    to be updated.  If a preview depends on any other events then those should
    also be bound to :meth:`update_preview`.

    .. attribute:: preview
        
        A :class:`wx.lib.plot.PlotCanvas` instance to use as a preview canvas.
    """
    def __init__(self):
        self.preview = wx.lib.plot.PlotCanvas(self)
        self.preview.SetEnableTitle(False)
        self.preview.SetEnableLegend(False)
        self.preview.SetSizeHints(minW=-1, minH=150, maxH=200)
        self.GetSizer().Add(self.preview, 1, wx.EXPAND|wx.ALL, 5)

        self.Bind(EVT_VALUE_CHANGED, self.update_preview)

    def update_preview(self, evt):
        """Redraw the preview (should be overridden in subclass)."""
        raise NotImplementedError

    def set_values(self, values):
        """Update the preview when values are set."""
        ParameterGroup.set_values(self, values)
        self.update_preview(None)


class InputFormatParams(FieldGroup):
    """Data file input format parameter group."""
    def __init__(self, fc, parent):
        FieldGroup.__init__(self, fc, parent)

        self.SetSizer(wx.BoxSizer(wx.VERTICAL))

        self.input_fields = wxext.ListSelectCtrl(self)
        self.input_fields.SetAvailable([(v['long'], k) for k,v in model.input_fields.iteritems()])
        self.GetSizer().Add(self.input_fields, 1, wx.EXPAND|wx.ALL, 5)

        self.input_trim = SpinField(self, 0, 10, 0)
        s = wx.BoxSizer(wx.HORIZONTAL)
        self.GetSizer().Add(s, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        s.Add(wx.StaticText(self, label='Number of lines to trim from ' + \
                            'beginning of file (e.g. for column headers'),
              0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        s.Add(self.input_trim.field, 0, wx.EXPAND)

    def get_values(self):
        return OrderedDict((('input_fields', [b for a,b in self.input_fields.GetSelectionWithData()]),
                            ('input_trim', self.input_trim.get_value())))

    def set_values(self, values):
        if 'input_fields' in values:
            self.input_fields.SetSelection([model.input_fields[x]['long'] for x in values['input_fields']])
        if 'input_trim' in values:
            self.input_trim.set_value(values['input_trim'])


class SiteLocationParams(ParameterGroup):
    """Site location parameters group."""
    PARAMETERS = model.parameters_by_group('siteloc')


class MeasurementParams(ParameterGroup):
    """Measurement location parameters group."""
    PARAMETERS = model.parameters_by_group('meas')


class VegCharParams(ParameterGroup):
    """Vegetation characteristics parameters group."""
    PARAMETERS = model.parameters_by_group('vegchar')


class VegEnvParams(ParameterGroup):
    """Vegetation environmental response parameters group."""
    PARAMETERS = model.parameters_by_group('vegenv')

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


class SeasonParams(ParameterGroup, PreviewCanvasMixin):
    """Season parameters group.

    Has a graph previewing the LAI function.
    """
    PARAMETERS = model.parameters_by_group('season')

    def __init__(self, *args, **kwargs):
        ParameterGroup.__init__(self, *args, **kwargs)
        PreviewCanvasMixin.__init__(self)

    @wxext.autoeventskip
    def update_preview(self, evt):
        gfx = wx.lib.plot.PlotGraphics([graphs.lai_preview(self.fc)],
                                       'LAI preview',
                                       'Day of year (dd)',
                                       'Leaf Area Index')
        self.preview.Draw(graphics=gfx)


class FphenParams(ParameterGroup, PreviewCanvasMixin):
    """Canopy Fphen parameters group.

    Has a graph previewing the fphen function.  Also depends on ``sgs`` and
    ``egs`` from the season parameters group.
    """
    PARAMETERS = model.parameters_by_group('fphen')

    def __init__(self, *args, **kwargs):
        ParameterGroup.__init__(self, *args, **kwargs)
        PreviewCanvasMixin.__init__(self)
        
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


class LeafFphenParams(ParameterGroup, PreviewCanvasMixin):
    """Leaf fphen parameters group.

    Has a graph previewing the leaf fphen function.  Also depends on ``sgs`` and
    ``egs`` from the season parameters group, plus everything in the Fphen group
    (since it might be following the canopy fphen calculation).
    """
    PARAMETERS = model.parameters_by_group('leaf_fphen')

    def __init__(self, *args, **kwargs):
        ParameterGroup.__init__(self, *args, **kwargs)
        PreviewCanvasMixin.__init__(self)

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
        ParameterGroup.set_values(self, values)
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
        enabled = self['leaf_fphen'].get_value() != 'copy'
        for field in self.itervalues():
            if field is not self['leaf_fphen']:
                field.field.Enable(enabled)
