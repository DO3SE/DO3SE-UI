import wx
import wx.lib.plot

import wxext
import model
from fields import *
import graphs


class ParameterGroup(SimpleFieldGroup):
    PARAMETERS = model.parameters_by_group(None)

    def __init__(self, *args, **kwargs):
        kwargs['fields'] = self.PARAMETERS
        SimpleFieldGroup.__init__(self, *args, **kwargs)


class PreviewCanvasMixin:
    def __init__(self):
        self.preview = wx.lib.plot.PlotCanvas(self)
        self.preview.SetEnableTitle(False)
        self.preview.SetEnableLegend(False)
        self.preview.SetSizeHints(minW=-1, minH=150, maxH=200)
        self.GetSizer().Add(self.preview, 1, wx.EXPAND|wx.ALL, 5)

        self.Bind(EVT_VALUE_CHANGED, self.update_preview)

    def update_preview(self, evt):
        raise NotImplementedError

    def set_values(self, values):
        ParameterGroup.set_values(self, values)
        self.update_preview(None)


class InputFormatParams(FieldGroup):
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
    PARAMETERS = model.parameters_by_group('siteloc')


class MeasurementParams(ParameterGroup):
    PARAMETERS = model.parameters_by_group('meas')


class VegCharParams(ParameterGroup):
    PARAMETERS = model.parameters_by_group('vegchar')


class VegEnvParams(ParameterGroup):
    PARAMETERS = model.parameters_by_group('vegenv')


class ModelOptionsParams(ParameterGroup):
    PARAMETERS = model.parameters_by_group('modelopts')


class SeasonParams(ParameterGroup, PreviewCanvasMixin):
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
        enabled = self['leaf_fphen'].get_value() != 'copy'
        for field in self.itervalues():
            if field is not self['leaf_fphen']:
                field.field.Enable(enabled)
