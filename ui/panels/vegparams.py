# TODO: Load defaults from the F model

import wx

from .. import wxext
from ..FloatSpin import FloatSpin
from ..app import logging, app

class VegParams(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.fields = dict()

        # Outer sizer
        sMain = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sMain)

        self.presets = wxext.PresetChooser(self)
        self.presets.SetPresets(app.config['preset.veg'])
        self.presets.getvalues = self.getvalues
        self.presets.setvalues = self.setvalues
        def f():
            app.config['preset.veg'] = self.presets.GetPresets()
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
        self.fields['h'] = wx.SpinCtrl(p, min=1, max=100, initial=25)
        s.Add(self.fields['h'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Root depth (m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['root'] = FloatSpin(p, value=1.2, min_val=0.01, 
                increment=0.1, digits=1)
        s.Add(self.fields['root'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Min. Leaf Area Index (m^2/m^2)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['lai_min'] = FloatSpin(p, value=0.0, min_val=0,
                increment=0.1, digits=1)
        s.Add(self.fields['lai_min'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Max. Leaf Area Index (m^2/m^2)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['lai_max'] = FloatSpin(p, value=4.0, min_val=0,
                increment=0.1, digits=1)
        s.Add(self.fields['lai_max'], 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Leaf dimension (Lm, m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['lm'] = FloatSpin(p, min_val=0.01, value=0.05, increment=0.01, digits=2)
        s.Add(self.fields['lm'], 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Albedo"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['albedo'] = FloatSpin(p, min_val=0.01, value=0.12, max_val=0.99, 
                increment=0.01, digits=2)
        s.Add(self.fields['albedo'], 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="External plant cuticle resistance (Rext, s/m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['rext'] = wx.SpinCtrl(p, min=0, max=20000, initial=2500)
        s.Add(self.fields['rext'], 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="light_a"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['f_lightfac'] = FloatSpin(p, min_val=0.001, value=0.006, max_val=0.999, 
                increment=0.001, digits=3)
        s.Add(self.fields['f_lightfac'], 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="gmax"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['gmax'] = wx.SpinCtrl(p, min=1, initial=148, max=10000)
        s.Add(self.fields['gmax'], 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="gmin"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['fmin'] = FloatSpin(p, min_val=0.01, value=0.13, max_val=0.99, 
                increment=0.01, digits=2)
        s.Add(self.fields['fmin'], 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Threshold Y for AFstY (nmol/m^2/s)"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['y'] = FloatSpin(p, min_val=0.1, value=1.6, max_val=100.0,
                increment=0.1, digits=1)
        s.Add(self.fields['y'], 0, wx.ALIGN_RIGHT)

        # Growing season
        p, s = makepage("Season")

        s.Add(wx.StaticText(p, label="Start (SGS, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['sgs'] = wx.SpinCtrl(p, min=1, max=365, initial=121)
        s.Add(self.fields['sgs'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="End (EGS, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['egs'] = wx.SpinCtrl(p, min=1, max=365, initial=273)
        s.Add(self.fields['egs'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Upper leaf start (Astart, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['astart'] = wx.SpinCtrl(p, min=1, max=365, initial=121)
        s.Add(self.fields['astart'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Upper leaf end (Aend, day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['aend'] = wx.SpinCtrl(p, min=1, max=365, initial=273)
        s.Add(self.fields['aend'], 0, wx.ALIGN_RIGHT)

        # TODO: Limit these based on the growing season?
        s.Add(wx.StaticText(p, label="Period from min. LAI to max. LAI (days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['ls'] = wx.SpinCtrl(p, min=1, max=100, initial=30)
        s.Add(self.fields['ls'], 0, wx.ALIGN_RIGHT)

        s.Add(wx.StaticText(p, label="Period from max. LAI to min. LAI (days)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['le'] = wx.SpinCtrl(p, min=1, max=100, initial=30)
        s.Add(self.fields['le'], 0, wx.ALIGN_RIGHT)

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
        self.fields['t_min'] = wx.SpinCtrl(p, min=-10, max=100, initial=0)
        s.Add(self.fields['t_min'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Optimum temperature (Celcius)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['t_opt'] = wx.SpinCtrl(p, min=-10, max=100, initial=21)
        s.Add(self.fields['t_opt'])
        
        s.Add(wx.StaticText(p, label="Maximum temperature (Celcius)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['t_max'] = wx.SpinCtrl(p, min=-10, max=100, initial=35)
        s.Add(self.fields['t_max'], 0, wx.ALIGN_RIGHT)
        
        # TODO: min/max values for VPD
        s.Add(wx.StaticText(p, label="VPD for minimum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['vpd_min'] = FloatSpin(p, value=3.25, increment=0.01, digits=2)
        s.Add(self.fields['vpd_min'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="VPD for maximum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['vpd_max'] = FloatSpin(p, value=1.0, increment=0.01, digits=2)
        s.Add(self.fields['vpd_max'], 0, wx.ALIGN_RIGHT)
        
        # TODO: min/max for SWP
        s.Add(wx.StaticText(p, label="SWP for minimum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['swp_min'] = FloatSpin(p, value=-1.25, increment=0.01, digits=2)
        s.Add(self.fields['swp_min'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="SWP for maximum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['swp_max'] = FloatSpin(p, value=-0.05, increment=0.01, digits=2)
        s.Add(self.fields['swp_max'], 0, wx.ALIGN_RIGHT)

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
        self.fields['fphen_a'] = FloatSpin(p, value=0.0, increment=0.1, 
                min_val=0.0, max_val=1.0, digits=1)
        s.Add(self.fields['fphen_a'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Fphen at Astart"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['fphen_b'] = FloatSpin(p, value=0.0, increment=0.1, 
                min_val=0.0, max_val=1.0, digits=1)
        s.Add(self.fields['fphen_b'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Fphen at middle of season"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['fphen_c'] = FloatSpin(p, value=1.0, increment=0.1, 
                min_val=0.0, max_val=1.0, digits=1)
        s.Add(self.fields['fphen_c'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Fphen at Aend and EGS"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['fphen_d'] = FloatSpin(p, value=0.0, increment=0.1, 
                min_val=0.0, max_val=1.0, digits=1)
        s.Add(self.fields['fphen_d'], 0, wx.ALIGN_RIGHT)
        
        # TODO: Put some constraints on these
        s.Add(wx.StaticText(p, label="Period from Astart to mid-season Fphen"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['fphens'] = wx.SpinCtrl(p, min=1, initial=15)
        s.Add(self.fields['fphens'], 0, wx.ALIGN_RIGHT)
        
        s.Add(wx.StaticText(p, label="Period from mid-season to EGS Fphen"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['fphene'] = wx.SpinCtrl(p, min=1, initial=20)
        s.Add(self.fields['fphene'], 0, wx.ALIGN_RIGHT)


    def getvalues(self):
        return {
                'h': float(self.fields['h'].GetValue()),
                'root': float(self.fields['root'].GetValue()),
                'lai_min': float(self.fields['lai_min'].GetValue()),
                'lai_max': float(self.fields['lai_max'].GetValue()),
                'lm': float(self.fields['lm'].GetValue()),
                'albedo': float(self.fields['albedo'].GetValue()),
                'rext': float(self.fields['rext'].GetValue()),
                'sgs': float(self.fields['sgs'].GetValue()),
                'egs': float(self.fields['egs'].GetValue()),
                'astart': float(self.fields['astart'].GetValue()),
                'aend': float(self.fields['aend'].GetValue()),
                'ls': float(self.fields['ls'].GetValue()),
                'le': float(self.fields['le'].GetValue()),
                't_min': float(self.fields['t_min'].GetValue()),
                't_opt': float(self.fields['t_opt'].GetValue()),
                't_max': float(self.fields['t_max'].GetValue()),
                'vpd_min': float(self.fields['vpd_min'].GetValue()),
                'vpd_max': float(self.fields['vpd_max'].GetValue()),
                'swp_min': float(self.fields['swp_min'].GetValue()),
                'swp_max': float(self.fields['swp_max'].GetValue()),
                'fphen_a': float(self.fields['fphen_a'].GetValue()),
                'fphen_b': float(self.fields['fphen_b'].GetValue()),
                'fphen_c': float(self.fields['fphen_c'].GetValue()),
                'fphen_d': float(self.fields['fphen_d'].GetValue()),
                'fphens': float(self.fields['fphens'].GetValue()),
                'fphene': float(self.fields['fphene'].GetValue()),
                'f_lightfac': float(self.fields['f_lightfac'].GetValue()),
                'gmax': float(self.fields['gmax'].GetValue()),
                'fmin': float(self.fields['fmin'].GetValue()),
                'y': float(self.fields['y'].GetValue()),
        }

    def setvalues(self, v):
        self.fields['h'].SetValue(v['h'])
        self.fields['root'].SetValue(v['root'])
        self.fields['lai_min'].SetValue(v['lai_min'])
        self.fields['lai_max'].SetValue(v['lai_max'])
        self.fields['lm'].SetValue(v['lm'])
        self.fields['albedo'].SetValue(v['albedo'])
        self.fields['rext'].SetValue(v['rext'])
        self.fields['sgs'].SetValue(v['sgs'])
        self.fields['egs'].SetValue(v['egs'])
        self.fields['astart'].SetValue(v['astart'])
        self.fields['aend'].SetValue(v['aend'])
        self.fields['ls'].SetValue(v['ls'])
        self.fields['le'].SetValue(v['le'])
        self.fields['t_min'].SetValue(v['t_min'])
        self.fields['t_opt'].SetValue(v['t_opt'])
        self.fields['t_max'].SetValue(v['t_max'])
        self.fields['vpd_min'].SetValue(v['vpd_min'])
        self.fields['vpd_max'].SetValue(v['vpd_max'])
        self.fields['swp_min'].SetValue(v['swp_min'])
        self.fields['swp_max'].SetValue(v['swp_max'])
        self.fields['fphen_a'].SetValue(v['fphen_a'])
        self.fields['fphen_b'].SetValue(v['fphen_b'])
        self.fields['fphen_c'].SetValue(v['fphen_c'])
        self.fields['fphen_d'].SetValue(v['fphen_d'])
        self.fields['fphens'].SetValue(v['fphens'])
        self.fields['fphene'].SetValue(v['fphene'])
        self.fields['f_lightfac'].SetValue(v['f_lightfac'])
        self.fields['gmax'].SetValue(v['gmax'])
        self.fields['fmin'].SetValue(v['fmin'])
        self.fields['y'].SetValue(v['y'])
