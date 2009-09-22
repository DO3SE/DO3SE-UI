# TODO: Load defaults from the F model

import wx

from .. import wxext
from ..FloatSpin import FloatSpin
from ..app import logging, app
from ..fieldgroup import Field, FieldGroup, wxField, wxFloatField

class VegParams(wx.Panel):
    def __init__(self, *args, **kwargs):
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
        sVegParams = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sVegParams.AddGrowableCol(0)
        sVegParams.AddGrowableCol(1)
        sMain.Add(sVegParams, 0, wx.ALL|wx.EXPAND, 6)

 
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
        self.fields.add('h', wxFloatField(wx.SpinCtrl(p, min=1, max=100, initial=25)))
        s.Add(self.fields['h'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Root depth (m)"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('root', wxFloatField(FloatSpin(p,
                value=1.2, min_val=0.01, increment=0.1, digits=1)))
        s.Add(self.fields['root'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Min. Leaf Area Index (m^2/m^2)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('lai_min', wxFloatField(FloatSpin(p,
                value=0.0, min_val=0, increment=0.1, digits=1)))
        s.Add(self.fields['lai_min'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Max. Leaf Area Index (m^2/m^2)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('lai_max', wxFloatField(FloatSpin(p,
                value=4.0, min_val=0, increment=0.1, digits=1)))
        s.Add(self.fields['lai_max'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Leaf dimension (Lm, m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('lm', wxFloatField(FloatSpin(p,
                min_val=0.01, value=0.05, increment=0.01, digits=2)))
        s.Add(self.fields['lm'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Albedo"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('albedo', wxFloatField(FloatSpin(p,
                min_val=0.01, value=0.12, max_val=0.99, increment=0.01, digits=2)))
        s.Add(self.fields['albedo'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="External plant cuticle resistance (Rext, s/m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('rext', wxFloatField(wx.SpinCtrl(p,
                min=0, max=20000, initial=2500)))
        s.Add(self.fields['rext'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="light_a"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('f_lightfac', wxFloatField(FloatSpin(p,
                min_val=0.001, value=0.006, max_val=0.999, increment=0.001, digits=3)))
        s.Add(self.fields['f_lightfac'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="gmax"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('gmax', wxFloatField(wx.SpinCtrl(p,
                min=1, initial=148, max=10000)))
        s.Add(self.fields['gmax'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="fmin"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fmin', wxFloatField(FloatSpin(p,
                min_val=0.01, value=0.13, max_val=0.99, increment=0.01, digits=2)))
        s.Add(self.fields['fmin'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Threshold Y for AFstY (nmol/m^2/s)"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('y', wxFloatField(FloatSpin(p,
                min_val=0.1, value=1.6, max_val=100.0, increment=0.1, digits=1)))
        s.Add(self.fields['y'].obj, 0, wx.ALIGN_RIGHT)

        # Growing season
        p, s = makepage("Season")

        s.Add(wx.StaticText(p, label="Start (SGS, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('sgs', wxFloatField(wx.SpinCtrl(p,
                min=1, max=365, initial=121)))
        s.Add(self.fields['sgs'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="End (EGS, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('egs', wxFloatField(wx.SpinCtrl(p,
                min=1, max=365, initial=273)))
        s.Add(self.fields['egs'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Upper leaf start (Astart, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('astart', wxFloatField(wx.SpinCtrl(p,
                min=1, max=365, initial=121)))
        s.Add(self.fields['astart'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Upper leaf end (Aend, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('aend', wxFloatField(wx.SpinCtrl(p,
                min=1, max=365, initial=273)))
        s.Add(self.fields['aend'].obj, 0, wx.ALIGN_RIGHT)

        # TODO: Limit these based on the growing season?
        s.Add(wx.StaticText(p, label="Period from min. LAI to max. LAI (days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('ls', wxFloatField(wx.SpinCtrl(p, min=1, max=100, initial=30)))
        s.Add(self.fields['ls'].obj, 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Period from max. LAI to min. LAI (days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('le', wxFloatField(wx.SpinCtrl(p, min=1, max=100, initial=30)))
        s.Add(self.fields['le'].obj, 0, wx.ALIGN_RIGHT)

        # Maintain integrity on growing season
        def f(evt):
            if self.fields['sgs'].GetValue() > self.fields['egs'].GetValue():
                self.fields['sgs'].SetValue(self.fields['egs'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['sgs'])
        def f(evt):
            if self.fields['egs'].GetValue() < self.fields['sgs'].GetValue():
                self.fields['egs'].SetValue(self.fields['sgs'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['egs'])
        def f(evt):
            if self.fields['astart'].GetValue() > self.fields['aend'].GetValue():
                self.fields['astart'].SetValue(self.fields['aend'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['astart'])
        def f(evt):
            if self.fields['aend'].GetValue() < self.fields['astart'].GetValue():
                self.fields['aend'].SetValue(self.fields['astart'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['aend'])


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
        s.Add(wx.StaticText(p, label="VPD for minimum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('vpd_min', wxFloatField(FloatSpin(p,
                value=3.25, increment=0.01, digits=2)))
        s.Add(self.fields['vpd_min'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="VPD for maximum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('vpd_max', wxFloatField(FloatSpin(p,
                value=1.0, increment=0.01, digits=2)))
        s.Add(self.fields['vpd_max'].obj, 0, wx.ALIGN_RIGHT)
        
        # TODO: min/max for SWP
        s.Add(wx.StaticText(p, label="SWP for minimum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('swp_min', wxFloatField(FloatSpin(p,
                value=-1.25, increment=0.01, digits=2)))
        s.Add(self.fields['swp_min'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="SWP for maximum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('swp_max', wxFloatField(FloatSpin(p,
                value=-0.05, increment=0.01, digits=2)))
        s.Add(self.fields['swp_max'].obj, 0, wx.ALIGN_RIGHT)

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
        

        # Fphen parameters
        p, s = makepage("Fphen")

        s.Add(wx.StaticText(p, label="Fphen at SGS"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_a', wxFloatField(FloatSpin(p,
                value=0.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s.Add(self.fields['fphen_a'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Fphen at Astart"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_b', wxFloatField(FloatSpin(p,
                value=0.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s.Add(self.fields['fphen_b'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Fphen at middle of season"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_c', wxFloatField(FloatSpin(p,
                value=1.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s.Add(self.fields['fphen_c'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Fphen at Aend and EGS"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphen_d', wxFloatField(FloatSpin(p,
                value=0.0, increment=0.1, min_val=0.0, max_val=1.0, digits=1)))
        s.Add(self.fields['fphen_d'].obj, 0, wx.ALIGN_RIGHT)
        
        # TODO: Put some constraints on these
        s.Add(wx.StaticText(p, label="Period from Astart to mid-season Fphen"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphens', wxFloatField(wx.SpinCtrl(p, min=1, initial=15)))
        s.Add(self.fields['fphens'].obj, 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Period from mid-season to EGS Fphen"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('fphene', wxFloatField(wx.SpinCtrl(p, min=1, initial=20)))
        s.Add(self.fields['fphene'].obj, 0, wx.ALIGN_RIGHT)


    def getvalues(self):
        return self.fields.get_values()


    def setvalues(self, v):
        return self.fields.set_values(v)
