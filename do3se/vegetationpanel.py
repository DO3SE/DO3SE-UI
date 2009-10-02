# TODO: Load defaults from the F model

import wx
from wx.lib import plot
from wx.lib import scrolledpanel

import wxext
import model
from util.fieldgroup import Field, FieldGroup, wxField, wxFloatField

class LeafFphenField(Field):
    def __init__(self, parent):
        obj = wx.Choice(parent)
        for x in model.leaf_fphen_calcs:
            obj.Append(x['name'], x['id'])
        Field.__init__(self, obj)

    def get(self):
        return self.obj.GetClientData(self.obj.GetSelection())

    def set(self, value):
        self.obj.SetStringSelection(model.leaf_fphen_calc_map[value]['name'])


class fO3Field(Field):
    def __init__(self, parent):
        obj = wx.Choice(parent)
        for x in model.fO3_calcs:
            obj.Append(x['name'], x['id'])
        Field.__init__(self, obj)

    def get(self):
        return self.obj.GetClientData(self.obj.GetSelection())

    def set(self, value):
        self.obj.SetStringSelection(model.fO3_calc_map[value]['name'])


class SAIField(Field):
    def __init__(self, parent):
        obj = wx.Choice(parent)
        for x in model.SAI_calcs:
            obj.Append(x['name'], x['id'])
        Field.__init__(self, obj)

    def get(self):
        return self.obj.GetClientData(self.obj.GetSelection())

    def set(self, value):
        self.obj.SetStringSelection(model.SAI_calc_map[value]['name'])


class VegetationPanel(wx.Panel):
    def __init__(self, app, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.fields = FieldGroup()

        # Outer sizer
        sMain = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sMain)

        self.presets = wxext.PresetChooser(self)
        self.presets.SetPresets(app.config['veg_params'])
        self.presets.getvalues = self.getvalues
        self.presets.setvalues = self.setvalues
        def f():
            app.config['veg_params'] = self.presets.GetPresets()
            app.config.sync()
        self.presets.post_update = f
        sMain.Add(self.presets, 0, wx.ALL|wx.EXPAND, 6)

 
        # Notebook containing parameter groups
        nb = wx.Notebook(self)
        sMain.Add(nb, 1, wx.EXPAND|wx.ALL, 6)

        # Helper function for creating notebook pages
        #
        # Returns (panel, sizer) tuple
        def makepage(label, cols=2, growablecols=[0]):
            p = wx.Panel(nb)
            p.SetSizer(wx.BoxSizer(wx.VERTICAL))
            p2 = wx.Panel(p)
            p.GetSizer().Add(p2, 1, wx.EXPAND|wx.ALL, 6)
            s = wx.FlexGridSizer(cols=cols, vgap=6, hgap=6)
            for c in growablecols: s.AddGrowableCol(c)
            p2.SetSizer(s)
            nb.AddPage(p, label)
            return (p2, s)

        
        # Characteristics
        p, s = makepage("Characteristics")
        
        s.Add(wx.StaticText(p, label="Canopy height (m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('h', wxFloatField(wxext.FloatSpin(p,
                min_val=1.0, max_val=100.0, value=25.0, increment=1.0, digits=1)))
        s.Add(self.fields['h'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Root depth (m)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('root', wxFloatField(wxext.FloatSpin(p,
                value=1.2, min_val=0.01, increment=0.1, digits=1)))
        s.Add(self.fields['root'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Leaf dimension (Lm, m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('lm', wxFloatField(wxext.FloatSpin(p,
                min_val=0.01, value=0.05, increment=0.01, digits=2)))
        s.Add(self.fields['lm'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Albedo"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('albedo', wxFloatField(wxext.FloatSpin(p,
                min_val=0.01, value=0.12, max_val=0.99, increment=0.01, digits=2)))
        s.Add(self.fields['albedo'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="External plant cuticle resistance (Rext, s/m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('rext', wxFloatField(wx.SpinCtrl(p,
                min=0, max=20000, initial=2500)))
        s.Add(self.fields['rext'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="light_a"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('f_lightfac', wxFloatField(wxext.FloatSpin(p,
                min_val=0.001, value=0.006, max_val=0.999, increment=0.001, digits=3)))
        s.Add(self.fields['f_lightfac'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="gmax"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('gmax', wxFloatField(wx.SpinCtrl(p,
                min=1, initial=148, max=10000)))
        s.Add(self.fields['gmax'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="fmin"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fmin', wxFloatField(wxext.FloatSpin(p,
                min_val=0.01, value=0.13, max_val=0.99, increment=0.01, digits=2)))
        s.Add(self.fields['fmin'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Threshold Y for AFstY (nmol/m^2/s)"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('y', wxFloatField(wxext.FloatSpin(p,
                min_val=0.1, value=1.6, max_val=100.0, increment=0.1, digits=1)))
        s.Add(self.fields['y'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="fO3 calculation"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fo3', fO3Field(p))
        self.fields['fo3'].set(model.default_fO3_calc)
        s.Add(self.fields['fo3'].obj, 0, wx.ALIGN_RIGHT)


        # Phenology (fphen, LAI)
        p = scrolledpanel.ScrolledPanel(nb)
        nb.AddPage(p, "Phenology")
        _s = wx.BoxSizer(wx.HORIZONTAL)
        p.SetSizer(_s)
        s = wx.BoxSizer(wx.VERTICAL)
        _s.Add(s, 1, wx.EXPAND|wx.ALL, 6)

        # Growing season
        bs = wx.StaticBoxSizer(wx.StaticBox(p, label="Growing season"), wx.VERTICAL)
        s.Add(bs, 0, wx.EXPAND)
        s1 = wx.BoxSizer(wx.HORIZONTAL)
        bs.Add(s1, 1, wx.EXPAND|wx.ALL, 6)

        s1.Add(wx.StaticText(p, label="Start (SGS, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        s1.AddSpacer(6)
        self.fields.add('sgs', wxFloatField(wx.SpinCtrl(p,
                min=1, max=365, initial=121)))
        s1.Add(self.fields['sgs'].obj, 0, wx.ALIGN_RIGHT)

        s1.AddSpacer(12)
        s1.Add(wx.StaticText(p, label="End (EGS, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        s1.AddSpacer(6)
        self.fields.add('egs', wxFloatField(wx.SpinCtrl(p,
                min=1, max=365, initial=273)))
        s1.Add(self.fields['egs'].obj, 0, wx.ALIGN_RIGHT)

        # Maintain integrity on growing season
        def f(evt):
            if self.fields['sgs'].GetValue() > self.fields['egs'].GetValue():
                self.fields['sgs'].SetValue(self.fields['egs'].GetValue())
            evt.Skip()
        self.fields['sgs'].Bind(wx.EVT_SPINCTRL, f)
        def f(evt):
            if self.fields['egs'].GetValue() < self.fields['sgs'].GetValue():
                self.fields['egs'].SetValue(self.fields['sgs'].GetValue())
            evt.Skip()
        self.fields['egs'].Bind(wx.EVT_SPINCTRL, f)

        s.AddSpacer(6)

        # Leaf Area Index
        bs = wx.StaticBoxSizer(wx.StaticBox(p, label="Leaf Area Index"), wx.HORIZONTAL)
        s.Add(bs, 0, wx.EXPAND)
        s1 = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        s2 = wx.BoxSizer(wx.VERTICAL)
        bs.Add(s1, 0, wx.EXPAND|wx.ALL, 6)
        bs.Add(s2, 1, wx.EXPAND|wx.ALL, 6)

        s1.Add(wx.StaticText(p, label="LAI at SGS (LAI_a, m^2/m^2)"),
                0, wx. ALIGN_CENTER_VERTICAL)
        self.fields.add('lai_a', wxFloatField(wxext.FloatSpin(p,
                value=0.0, min_val=0, increment=0.1, digits=1)))
        s1.Add(self.fields['lai_a'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Second LAI point (LAI_b, m^2/m^2)"),
                0, wx. ALIGN_CENTER_VERTICAL)
        self.fields.add('lai_b', wxFloatField(wxext.FloatSpin(p,
                value=4.0, min_val=0, increment=0.1, digits=1)))
        s1.Add(self.fields['lai_b'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Third LAI point (LAI_c, m^2/m^2)"),
                0, wx. ALIGN_CENTER_VERTICAL)
        self.fields.add('lai_c', wxFloatField(wxext.FloatSpin(p,
                value=4.0, min_val=0, increment=0.1, digits=1)))
        s1.Add(self.fields['lai_c'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="LAI at EGS (LAI_d, m^2/m^2)"),
                0, wx. ALIGN_CENTER_VERTICAL)
        self.fields.add('lai_d', wxFloatField(wxext.FloatSpin(p,
                value=0.0, min_val=0, increment=0.1, digits=1)))
        s1.Add(self.fields['lai_d'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Period from LAI_a to LAI_b (LAI_1, days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('lai_1', wxFloatField(wx.SpinCtrl(p, min=0, max=100, initial=30)))
        s1.Add(self.fields['lai_1'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Period from LAI_c to LAI_d (LAI_2, days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('lai_2', wxFloatField(wx.SpinCtrl(p, min=0, max=100, initial=30)))
        s1.Add(self.fields['lai_2'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="SAI calculation"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('sai', SAIField(p))
        self.fields['sai'].set(model.default_SAI_calc)
        s1.Add(self.fields['sai'].obj, 0, wx.ALIGN_RIGHT)

        # LAI preview
        self.LAI_preview = plot.PlotCanvas(p)
        self.LAI_preview.SetEnableTitle(False)
        self.LAI_preview.SetFontSizeLegend(10)
        s2.Add(self.LAI_preview, 1, wx.EXPAND)
        # Hook LAI curve changes to redraw
        self.fields['sgs'].Bind(wx.EVT_SPINCTRL, self.redraw_LAI_preview)
        self.fields['egs'].Bind(wx.EVT_SPINCTRL, self.redraw_LAI_preview)
        self.fields['lai_a'].Bind(wx.EVT_SPINCTRL, self.redraw_LAI_preview)
        self.fields['lai_b'].Bind(wx.EVT_SPINCTRL, self.redraw_LAI_preview)
        self.fields['lai_c'].Bind(wx.EVT_SPINCTRL, self.redraw_LAI_preview)
        self.fields['lai_d'].Bind(wx.EVT_SPINCTRL, self.redraw_LAI_preview)
        self.fields['lai_1'].Bind(wx.EVT_SPINCTRL, self.redraw_LAI_preview)
        self.fields['lai_2'].Bind(wx.EVT_SPINCTRL, self.redraw_LAI_preview)

        # Fphen and leaf fphen
        s.AddSpacer(6)
        bs = wx.StaticBoxSizer(wx.StaticBox(p, label="Fphen and leaf fphen"), wx.VERTICAL)
        s.Add(bs, 0, wx.EXPAND)
        _s = wx.BoxSizer(wx.HORIZONTAL)
        bs.Add(_s, 0, wx.EXPAND)
        s1 = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        s2 = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        s3 = wx.BoxSizer(wx.VERTICAL)
        _s.Add(s1, 1, wx.EXPAND|wx.ALL, 6)
        _s.Add(s3, 1, wx.EXPAND)
        s3.Add(s2, 0, wx.EXPAND|wx.ALL, 6)

        s1.Add(wx.StaticText(p, label="Fphen at SGS (fphen_a)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_a', wxFloatField(wxext.FloatSpin(p,
                value=0.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s1.Add(self.fields['fphen_a'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="First mid-season Fphen (fphen_b)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_b', wxFloatField(wxext.FloatSpin(p,
                value=1.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s1.Add(self.fields['fphen_b'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Second mid-season Fphen (fphen_c)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_c', wxFloatField(wxext.FloatSpin(p,
                value=1.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s1.Add(self.fields['fphen_c'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Third mid-season Fphen (fphen_d)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_d', wxFloatField(wxext.FloatSpin(p,
                value=1.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s1.Add(self.fields['fphen_d'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Fphen at EGS (fphen_e)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_e', wxFloatField(wxext.FloatSpin(p,
                value=0.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s1.Add(self.fields['fphen_e'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Period from fphen_a to fphen_b (fphen_1, days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_1', wxFloatField(wx.SpinCtrl(p,
                initial=15, min=0)))
        s1.Add(self.fields['fphen_1'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Start of SWP limitation (fphen_limA, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_lima', wxFloatField(wx.SpinCtrl(p,
                initial=180, min=0, max=365)))
        s1.Add(self.fields['fphen_lima'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Period from fphen_b to fphen_c (fphen_2, days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_2', wxFloatField(wx.SpinCtrl(p,
                initial=1, min=0)))
        s1.Add(self.fields['fphen_2'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Period from fphen_c to fphen_d (fphen_3, days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_3', wxFloatField(wx.SpinCtrl(p,
                initial=1, min=0)))
        s1.Add(self.fields['fphen_3'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="End of SWP limitation (fphen_limB, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_limb', wxFloatField(wx.SpinCtrl(p,
                initial=220, min=0, max=365)))
        s1.Add(self.fields['fphen_limb'].obj, 0, wx.ALIGN_RIGHT)

        s1.Add(wx.StaticText(p, label="Period from fphen_d to fphen_e (fphen_4, days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_4', wxFloatField(wx.SpinCtrl(p,
                initial=20, min=0)))
        s1.Add(self.fields['fphen_4'].obj, 0, wx.ALIGN_RIGHT)

        s2.Add(wx.StaticText(p, label="Leaf fphen calculation"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('leaf_fphen', LeafFphenField(p))
        s2.Add(self.fields['leaf_fphen'].obj, 0, wx.ALIGN_RIGHT)
        self.fields['leaf_fphen'].set(model.default_leaf_fphen_calc)
        self.fields['leaf_fphen'].Bind(wx.EVT_CHOICE, self.On_leaf_fphen_EVT_CHOICE)
        self.fields['leaf_fphen'].Bind(wx.EVT_CHOICE, self.redraw_fphen_preview)

        s2.Add(wx.StaticText(p, label="O3 accumulation start (Astart, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('astart', wxFloatField(wx.SpinCtrl(p,
                min=1, max=365, initial=153)))
        s2.Add(self.fields['astart'].obj, 0, wx.ALIGN_RIGHT)

        s2.Add(wx.StaticText(p, label="O3 accumulation end (Aend, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('aend', wxFloatField(wx.SpinCtrl(p,
                min=1, max=365, initial=208)))
        s2.Add(self.fields['aend'].obj, 0, wx.ALIGN_RIGHT)

        # Maintain Astart/Aend integrity
        def f(evt):
            if self.fields['astart'].GetValue() > self.fields['aend'].GetValue():
                self.fields['astart'].SetValue(self.fields['aend'].GetValue())
            evt.Skip()
        self.fields['astart'].Bind(wx.EVT_SPINCTRL, f)
        def f(evt):
            if self.fields['aend'].GetValue() < self.fields['astart'].GetValue():
                self.fields['aend'].SetValue(self.fields['astart'].GetValue())
            evt.Skip()
        self.fields['aend'].Bind(wx.EVT_SPINCTRL, f)

        s2.Add(wx.StaticText(p, label="Leaf fphen at Astart (leaf_fphen_a)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('leaf_fphen_a', wxFloatField(wxext.FloatSpin(p,
                value=0.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s2.Add(self.fields['leaf_fphen_a'].obj, 0, wx.ALIGN_RIGHT)

        s2.Add(wx.StaticText(p, label="Leaf fphen mid-season (leaf_fphen_b)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('leaf_fphen_b', wxFloatField(wxext.FloatSpin(p,
                value=1.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s2.Add(self.fields['leaf_fphen_b'].obj, 0, wx.ALIGN_RIGHT)

        s2.Add(wx.StaticText(p, label="Leaf fphen at Aend (leaf_fphen_c)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('leaf_fphen_c', wxFloatField(wxext.FloatSpin(p,
                value=0.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s2.Add(self.fields['leaf_fphen_c'].obj, 0, wx.ALIGN_RIGHT)

        s2.Add(wx.StaticText(p, label="Period from leaf_fphen_a to leaf_fphen_b"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('leaf_fphen_1', wxFloatField(wx.SpinCtrl(p,
                initial=15, min=0)))
        s2.Add(self.fields['leaf_fphen_1'].obj, 0, wx.ALIGN_RIGHT)

        s2.Add(wx.StaticText(p, label="Period from leaf_fphen_b to leaf_fphen_c"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('leaf_fphen_2', wxFloatField(wx.SpinCtrl(p,
                initial=30, min=0)))
        s2.Add(self.fields['leaf_fphen_2'].obj, 0, wx.ALIGN_RIGHT)

        # fphen preview
        self.fphen_preview = plot.PlotCanvas(p)
        self.fphen_preview.SetEnableTitle(False)
        self.fphen_preview.SetFontSizeLegend(10)
        self.fphen_preview.SetEnableLegend(True)
        self.fphen_preview.SetSizeHints(minW=-1, minH=150)
        s3.Add(self.fphen_preview, 1, wx.EXPAND|wx.ALL, 6)
        # Hook curve changes to redraw
        self.fields['sgs'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['egs'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_a'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_b'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_c'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_d'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_e'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_1'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_lima'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_2'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_3'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_limb'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['fphen_4'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['astart'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['aend'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['leaf_fphen_a'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['leaf_fphen_b'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['leaf_fphen_c'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['leaf_fphen_1'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)
        self.fields['leaf_fphen_2'].Bind(wx.EVT_SPINCTRL, self.redraw_fphen_preview)

        p.SetupScrolling()


        # Environmental dependence
        p, s = makepage("Environment")
        
        s.Add(wx.StaticText(p, label="Minimum temperature (Celcius)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('t_min', wxFloatField(wx.SpinCtrl(p,
                min=-10, max=100, initial=0)))
        s.Add(self.fields['t_min'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Optimum temperature (Celcius)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('t_opt', wxFloatField(wx.SpinCtrl(p,
                min=-10, max=100, initial=21)))
        s.Add(self.fields['t_opt'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Maximum temperature (Celcius)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('t_max', wxFloatField(wx.SpinCtrl(p,
                min=-10, max=100, initial=35)))
        s.Add(self.fields['t_max'].obj, 0, wx.ALIGN_RIGHT)
        
        # TODO: min/max values for VPD
        s.Add(wx.StaticText(p, label="VPD for minimum growth (VPD_min, kPa)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('vpd_min', wxFloatField(wxext.FloatSpin(p,
                value=3.25, increment=0.01, digits=2)))
        s.Add(self.fields['vpd_min'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="VPD for maximum growth (VPD_max, kPa)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('vpd_max', wxFloatField(wxext.FloatSpin(p,
                value=1.0, increment=0.01, digits=2)))
        s.Add(self.fields['vpd_max'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Critical daily VPD sum (VPD_crit, kPa)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('vpd_crit', wxFloatField(wxext.FloatSpin(p,
                value=1000.0, min_val=0.0, max_val=1000.0, increment=1.0, digits=1)))
        s.Add(self.fields['vpd_crit'].obj, 0, wx.ALIGN_RIGHT)
        
        # TODO: min/max for SWP
        s.Add(wx.StaticText(p, label="SWP for minimum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('swp_min', wxFloatField(wxext.FloatSpin(p,
                value=-1.25, increment=0.01, digits=2)))
        s.Add(self.fields['swp_min'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="SWP for maximum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('swp_max', wxFloatField(wxext.FloatSpin(p,
                value=-0.05, increment=0.01, digits=2)))
        s.Add(self.fields['swp_max'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Enable fSWP?"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('enable_fswp', wxField(wx.CheckBox(p,
                label="", style=wx.ALIGN_RIGHT)))
        self.fields['enable_fswp'].set(1)
        s.Add(self.fields['enable_fswp'].obj, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

        # Maintain integrity on environmental dependence
        def f(evt):
            if self.fields['t_opt'].GetValue() < self.fields['t_min'].GetValue():
                self.fields['t_opt'].SetValue(self.fields['t_min'].GetValue())
            elif self.fields['t_opt'].GetValue() > self.fields['t_max'].GetValue():
                self.fields['t_opt'].SetValue(self.fields['t_max'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['t_opt'])
        def f(evt):
            if self.fields['t_min'].GetValue() > self.fields['t_opt'].GetValue():
                self.fields['t_min'].SetValue(self.fields['t_opt'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['t_min'])
        def f(evt):
            if self.fields['t_max'].GetValue() < self.fields['t_opt'].GetValue():
                self.fields['t_max'].SetValue(self.fields['t_opt'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['t_max'])


        # Fire events to make UI consistent
        self.redraw_LAI_preview(None)
        self.redraw_fphen_preview(None)
        self.On_leaf_fphen_EVT_CHOICE(None)


    def redraw_LAI_preview(self, evt):
        lai = plot.PolyLine(points=(
            (self.fields['sgs'].get(), self.fields['lai_a'].get()),
            (self.fields['sgs'].get() + self.fields['lai_1'].get(), self.fields['lai_b'].get()),
            (self.fields['egs'].get() - self.fields['lai_2'].get(), self.fields['lai_c'].get()),
            (self.fields['egs'].get(), self.fields['lai_d'].get())),
            colour='green',
            legend='LAI')

        gfx = plot.PlotGraphics((lai,), 'LAI function preview', 'Day of year (dd)', 'LAI')

        self.LAI_preview.Draw(graphics=gfx)

        if evt: evt.Skip()


    def redraw_fphen_preview(self, evt):
        v = self.fields.get_values()
        lines = list()

        fphen_points = list()
        fphen_points.append((v['sgs'], v['fphen_a']))
        fphen_points.append((v['sgs'] + v['fphen_1'], v['fphen_b']))
        if v['fphen_lima'] > 0.0:
            fphen_points.append((v['fphen_lima'], v['fphen_b']))
            fphen_points.append((v['fphen_lima'] + v['fphen_2'], v['fphen_c']))
        if v['fphen_limb'] > 0.0:
            fphen_points.append((v['fphen_limb'] - v['fphen_3'], v['fphen_c']))
            fphen_points.append((v['fphen_limb'], v['fphen_d']))
        fphen_points.append((v['egs'] - v['fphen_4'], v['fphen_d']))
        fphen_points.append((v['egs'], v['fphen_e']))

        fphen = plot.PolyLine(points=fphen_points, colour='green', legend='Fphen')

        lines.append(fphen)

        if v['leaf_fphen'] != 'copy':
            leaf_fphen = plot.PolyLine(points=(
                (v['astart'], v['leaf_fphen_a']),
                (v['astart'] + v['leaf_fphen_1'], v['leaf_fphen_b']),
                (v['aend'] - v['leaf_fphen_2'], v['leaf_fphen_b']),
                (v['aend'], v['leaf_fphen_c'])),
                colour='red',
                legend='leaf_fphen')
            lines.append(leaf_fphen)

        gfx = plot.PlotGraphics(lines, 'Fphen function preview', 'Day of year (dd)', 'Fphen')
        self.fphen_preview.Draw(graphics=gfx)

        if evt: evt.Skip()


    def On_leaf_fphen_EVT_CHOICE(self, evt):
        calc = self.fields['leaf_fphen'].get()
        for x in ('astart', 'aend', 'leaf_fphen_a', 'leaf_fphen_b', 
                  'leaf_fphen_c', 'leaf_fphen_1', 'leaf_fphen_2'):
            self.fields[x].Enable(calc != 'copy')

        if evt: evt.Skip()


    def getvalues(self):
        return self.fields.get_values()


    def setvalues(self, v):
        self.fields.set_values(v)

        # Fire events to make the UI consistent
        self.redraw_LAI_preview(None)
        self.redraw_fphen_preview(None)
        self.On_leaf_fphen_EVT_CHOICE(None)
