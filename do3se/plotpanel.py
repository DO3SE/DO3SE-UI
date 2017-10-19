import wx
from wx.lib.plot import PlotCanvas, PlotGraphics, PolyLine
from operator import itemgetter

class FirstPlot(PlotCanvas):
    def __init__(self, parent, id, size, data, data2, legend1='', legend2='', title='', x_axis='', y_axis=''):
        PlotCanvas.__init__(self, parent, id, style=wx.BORDER_NONE, size=(300,300))
        self.data = data
        self.data2 = data2
        y_scale1 = (min(self.data, key=itemgetter(1))[1] - 0.1, max(self.data, key=itemgetter(1))[1]+0.1)
        y_scale2 = (min(self.data2, key=itemgetter(1))[1] - 0.1, max(self.data2, key=itemgetter(1))[1]+0.1)
        y_scale = (min(y_scale1[0], y_scale2[0]), max(y_scale1[1], y_scale2[1]))
        line = PolyLine(self.data, legend=legend1, colour='green', width=1)
        line2 = PolyLine(self.data2, legend=legend2, colour='blue', width=1)
        gc = PlotGraphics([line, line2], title, x_axis, y_axis)
        self.Draw(gc, xAxis=(min(self.data, key=itemgetter(0))[0] - 1,  max(self.data, key=itemgetter(0))[0]+0.1), yAxis=y_scale)


class GenericPlot(PlotCanvas):
    def __init__(self, parent, id, size, data, legend='', line_colour='black', line_width=2, title='', x_axis='', y_axis=''):
        PlotCanvas.__init__(self, parent, id, style=wx.BORDER_NONE, size=(300,300))
        self.data = data
        y_scale = (min(self.data, key=itemgetter(1))[1] - 0.1, max(self.data, key=itemgetter(1))[1]+0.1)
        line = PolyLine(self.data, legend=legend, colour=line_colour, width=line_width)
        gc = PlotGraphics([line], title, x_axis, y_axis)
        self.Draw(gc, xAxis=(min(self.data, key=itemgetter(0))[0] - 1, max(self.data, key=itemgetter(0))[0]+0.1), yAxis=(y_scale))


class PlotPanel(wx.Panel):
    def __init__(self, app, parent, results):
        wx.Panel.__init__(self, parent)

        self.app = app
        self.results = results

        # Outer sizer
        s = wx.GridSizer(0,2,5,5)

        flight_data = []
        ftemp_data = []
        vpd_data = []
        precip_data = []

        for r in self.results.data:
            point = (r['dd'], r['flight'])
            flight_data.append(point)

        for r in self.results.data:
            point = (r['dd'], r['ftemp'])
            ftemp_data.append(point)

        for r in self.results.data:
            point = (r['dd'], r['fvpd'])
            vpd_data.append(point)

        for r in self.results.data:
            point = (r['dd'], r['fxwp'])
            precip_data.append(point)

        self.flight_canvas = GenericPlot(self, 0, (300, 300), flight_data,
                                    legend='', line_colour='blue', line_width=1,
                                    title='Irradiance effect (flight, fraction)', x_axis='Day of Year', y_axis='flight')
        # self.canvas.SetEnableLegend(True)
        self.flight_canvas.SetEnableHiRes(True)
        self.flight_canvas.SetEnableAntiAliasing(True)
        self.flight_canvas.SetFontSizeAxis(8)

        self.ftemp_canvas = GenericPlot(self, 0, (300, 300), ftemp_data,
                                    legend='', line_colour='blue', line_width=1,
                                    title='Temperature effect (ftemp, fraction)', x_axis='Day of Year', y_axis='ftemp')
        # self.canvas.SetEnableLegend(True)
        self.ftemp_canvas.SetEnableHiRes(True)
        self.ftemp_canvas.SetEnableAntiAliasing(True)
        self.ftemp_canvas.SetFontSizeAxis(8)

        self.vpd_canvas = GenericPlot(self, 0, (300, 300), vpd_data,
                                        legend='', line_colour='blue', line_width=1,
                                    title='f_VPD (fraction)', x_axis='Day of Year', y_axis='VPD')
        self.vpd_canvas.SetEnableHiRes(True)
        self.vpd_canvas.SetEnableAntiAliasing(True)
        self.vpd_canvas.SetFontSizeAxis(8)

        self.precip_canvas = GenericPlot(self, 0, (300, 300), precip_data, 
                                    legend='', line_colour='blue', line_width=1,
                                    title='f_SW, fraction', x_axis='Day of Year', y_axis='soil water effect on stomatal conductance')
        self.precip_canvas.SetEnableHiRes(True)
        self.precip_canvas.SetEnableAntiAliasing(True)
        self.precip_canvas.SetFontSizeAxis(8)

        s.Add(self.flight_canvas, 1, wx.EXPAND, 1)
        s.Add(self.ftemp_canvas, 1, wx.EXPAND, 1)
        s.Add(self.vpd_canvas, 1, wx.EXPAND, 1)
        s.Add(self.precip_canvas, 1, wx.EXPAND, 1)

        self.SetSizer(s)
        self.Layout()


class PlotPanel2(wx.Panel):
    def __init__(self, app, parent, results):
        wx.Panel.__init__(self, parent)

        self.app = app
        self.results = results

        # Outer sizer
        s = wx.GridSizer(0,2,5,5)

        lai_data = []
        fphen_data = []
        leaf_fphen_data = []
        tt_fphen_data = []
        tt_lai_data = []
        tt_leaf_fphen_data = []

        for r in self.results.data:
            point = (r['dd'], r['lai'])
            lai_data.append(point)

        for r in self.results.data:
            point = (r['dd'], r['fphen'])
            fphen_data.append(point)

        for r in self.results.data:
            point = (r['dd'], r['leaf_fphen'])
            leaf_fphen_data.append(point)

        for r in self.results.data:
            point = (r['td'], r['lai'])
            tt_lai_data.append(point)

        for r in self.results.data:
            point = (r['td'], r['fphen'])
            tt_fphen_data.append(point)

        for r in self.results.data:
            point = (r['td'], r['leaf_fphen'])
            tt_leaf_fphen_data.append(point)


# data, data2, legend1='', legend2='', title='', x_axis='', y_axis=''

        self.fphen_canvas = FirstPlot(self, 0, (300, 300), leaf_fphen_data, fphen_data,
                                      legend1='leaf_fphen', legend2='fphen', title='fphen/leaf_fphen',
                                      x_axis='Day of Year', y_axis='fraction')
        self.fphen_canvas.SetEnableLegend(True)
        self.fphen_canvas.SetEnableHiRes(True)
        self.fphen_canvas.SetEnableAntiAliasing(True)
        self.fphen_canvas.SetFontSizeAxis(8)

        self.tt_fphen_canvas = FirstPlot(self, 0, (300, 300), tt_leaf_fphen_data, tt_fphen_data,
                                      legend1='leaf_fphen', legend2='fphen', title='fphen/leaf_fphen',
                                      x_axis='Thermal Time', y_axis='fraction')
        self.tt_fphen_canvas.SetEnableLegend(True)
        self.tt_fphen_canvas.SetEnableHiRes(True)
        self.tt_fphen_canvas.SetEnableAntiAliasing(True)
        self.tt_fphen_canvas.SetFontSizeAxis(8)

        self.lai_canvas = GenericPlot(self, 0, (300, 300), lai_data,
                                        legend='', line_colour='green', line_width=1,
                                        title=u'LAI, m\u00b2/m\u00b2', x_axis='Day of Year', y_axis='LAI')
        self.lai_canvas.SetEnableHiRes(True)
        self.lai_canvas.SetEnableAntiAliasing(True)
        self.lai_canvas.SetFontSizeAxis(8)

        self.tt_lai_canvas = GenericPlot(self, 0, (300, 300), tt_lai_data,
                                        legend='', line_colour='green', line_width=1,
                                        title=u'LAI, m\u00b2/m\u00b2', x_axis='Thermal Time', y_axis='LAI')
        self.tt_lai_canvas.SetEnableHiRes(True)
        self.tt_lai_canvas.SetEnableAntiAliasing(True)
        self.tt_lai_canvas.SetFontSizeAxis(8)

        s.Add(self.fphen_canvas, 1, wx.EXPAND, 1)
        s.Add(self.lai_canvas, 1, wx.EXPAND, 1)
        s.Add(self.tt_fphen_canvas, 1, wx.EXPAND, 1)
        s.Add(self.tt_lai_canvas, 1, wx.EXPAND, 1)

        self.SetSizer(s)
        self.Layout()


class PlotPanel3(wx.Panel):
    def __init__(self, app, parent, results):
        wx.Panel.__init__(self, parent)

        self.app = app
        self.results = results

        # Outer sizer
        s = wx.GridSizer(0,2,5,5)

        ts_c_data = []
        vpd_data = []
        par_data = []
        precip_data = []


        for r in self.results.data:
            point = (r['dd'], r['ts_c'])
            ts_c_data.append(point)

        for r in self.results.data:
            point = (r['dd'], r['vpd'])
            vpd_data.append(point)

        for r in self.results.data:
            point = (r['td'], r['par'])
            par_data.append(point)

        for r in self.results.data:
            point = (r['td'], r['precip'])
            precip_data.append(point)

# data, data2, legend1='', legend2='', title='', x_axis='', y_axis=''

        self.par_canvas = GenericPlot(self, 0, (300, 300), par_data,
                                        legend='', line_colour='blue', line_width=1,
                                        title=u'PAR (umol/umol/m\u00b2/s)', x_axis='Day of Year', y_axis=u'PAR, umol/m\u00b2/s')

        self.par_canvas.SetEnableHiRes(True)
        self.par_canvas.SetEnableAntiAliasing(True)
        self.par_canvas.SetFontSizeAxis(8)

        self.vpd_canvas = GenericPlot(self, 0, (300, 300), vpd_data,
                                        legend='', line_colour='blue', line_width=1,
                                        title=u'VPD (kPa)', x_axis='Day of Year', y_axis='Vapour Pressure Deficit (VPD, kPa)')
        self.vpd_canvas.SetEnableHiRes(True)
        self.vpd_canvas.SetEnableAntiAliasing(True)
        self.vpd_canvas.SetFontSizeAxis(8)

        self.ts_c_canvas = GenericPlot(self, 0, (300, 300), ts_c_data,
                                        legend='', line_colour='blue', line_width=1,
                                        title=u'Temperature (C)', x_axis='Day of Year', y_axis='Temperature (C)')
        self.ts_c_canvas.SetEnableHiRes(True)
        self.ts_c_canvas.SetEnableAntiAliasing(True)
        self.ts_c_canvas.SetFontSizeAxis(8)

        self.precip_canvas = GenericPlot(self, 0, (300, 300), precip_data,
                                        legend='', line_colour='green', line_width=1,
                                        title=u'Precipitation (precip, mm)', x_axis='Day of Year', y_axis='precip (mm)')
        self.precip_canvas.SetEnableHiRes(True)
        self.precip_canvas.SetEnableAntiAliasing(True)
        self.precip_canvas.SetFontSizeAxis(8)

        s.Add(self.par_canvas, 1, wx.EXPAND, 1)
        s.Add(self.ts_c_canvas, 1, wx.EXPAND, 1)
        s.Add(self.vpd_canvas, 1, wx.EXPAND, 1)
        s.Add(self.precip_canvas, 1, wx.EXPAND, 1)

        self.SetSizer(s)
        self.Layout()


class PlotPanel4(wx.Panel):
    def __init__(self, app, parent, results):
        wx.Panel.__init__(self, parent)

        self.app = app
        self.results = results

        # Outer sizer
        s = wx.GridSizer(0,2,5,5)

        sn_data = []
        pody_data = []
        fst_data = []

        for r in self.results.data:
            point = (r['dd'], r['sn'])
            sn_data.append(point)

        for r in self.results.data:
            point = (r['dd'], r['afsty'])
            pody_data.append(point)

        for r in self.results.data:
            point = (r['dd'], r['fst'])
            fst_data.append(point)

        self.sn_canvas = GenericPlot(self, 0, (300, 300), sn_data,
                                        legend='', line_colour='green', line_width=1,
                                        title='Soil Water Content', x_axis='Day of Year', y_axis=u'Sn, m\u00b3/m\u00b3')
        self.sn_canvas.SetEnableHiRes(True)
        self.sn_canvas.SetEnableAntiAliasing(True)
        self.sn_canvas.SetFontSizeAxis(8)


        self.pody_canvas = GenericPlot(self, 0, (300, 300), pody_data,
                                        legend='', line_colour='blue', line_width=1,
                                        title='PODy, Y=%s' % self.results.params['y'], x_axis='Day of Year', y_axis=u'PODy, mmol/m\u00b2 PLA')
        self.pody_canvas.SetEnableHiRes(True)
        self.pody_canvas.SetEnableAntiAliasing(True)
        self.pody_canvas.SetFontSizeAxis(8)

        self.fst_canvas = GenericPlot(self, 0, (300, 300), fst_data,
                                        legend='', line_colour='blue', line_width=1,
                                        title=u'Stomatal O3 Flux (nmol/m\u00b2/s)', x_axis='Day of Year', y_axis=u'Fst, nmol/m\u00b2/s')
        self.fst_canvas.SetEnableHiRes(True)
        self.fst_canvas.SetEnableAntiAliasing(True)
        self.fst_canvas.SetFontSizeAxis(8)

        s.Add(self.sn_canvas, 1, wx.EXPAND, 1)
        s.Add(self.pody_canvas, 1, wx.EXPAND, 1)
        s.Add(self.fst_canvas, 1, wx.EXPAND, 1)

        self.SetSizer(s)
        self.Layout()