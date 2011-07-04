"""Graph creation functions.

Functions for creating various graphs using the wxPython plotting library.
"""
import wx
import wx.lib.plot


def lai_preview(fc, colour='green', label='LAI'):
    """Create LAI preview graph."""
    sgs = fc['season']['sgs'].get_value()
    egs = fc['season']['egs'].get_value()
    lai_a = fc['season']['lai_a'].get_value()
    lai_b = fc['season']['lai_b'].get_value()
    lai_c = fc['season']['lai_c'].get_value()
    lai_d = fc['season']['lai_d'].get_value()
    lai_1 = fc['season']['lai_1'].get_value()
    lai_2 = fc['season']['lai_2'].get_value()

    wrap_point = lai_a - (lai_a - lai_d) * sgs / (sgs + 365 - egs)

    points = [(1, wrap_point),
              (sgs, lai_a),
              (sgs + lai_1, lai_b),
              (egs - lai_2, lai_c),
              (egs, lai_d),
              (365, wrap_point)]

    return wx.lib.plot.PolyLine(points=points,
                                colour=colour,
                                legend=label)


def fphen_preview(fc, colour='green', label='Fphen'):
    """Create Fphen preview graph."""
    sgs = fc['season']['sgs'].get_value()
    egs = fc['season']['egs'].get_value()
    fphen_a = fc['fphen']['fphen_a'].get_value()
    fphen_b = fc['fphen']['fphen_b'].get_value()
    fphen_c = fc['fphen']['fphen_c'].get_value()
    fphen_d = fc['fphen']['fphen_d'].get_value()
    fphen_e = fc['fphen']['fphen_e'].get_value()
    fphen_lima = fc['fphen']['fphen_lima'].get_value()
    fphen_limb = fc['fphen']['fphen_limb'].get_value()
    fphen_1 = fc['fphen']['fphen_1'].get_value()
    fphen_2 = fc['fphen']['fphen_2'].get_value()
    fphen_3 = fc['fphen']['fphen_3'].get_value()
    fphen_4 = fc['fphen']['fphen_4'].get_value()

    points = [(sgs, fphen_a),
              (sgs + fphen_1, fphen_b)]
    if fphen_lima > 0:
        points += [(fphen_lima, fphen_b),
                   (fphen_lima + fphen_2, fphen_c)]
    if fphen_limb > 0:
        points += [(fphen_limb - fphen_3, fphen_c),
                   (fphen_limb, fphen_d)]
    points += [(egs - fphen_4, fphen_d),
               (egs, fphen_e)]

    return wx.lib.plot.PolyLine(points=points,
                                colour=colour,
                                legend=label)


def leaf_fphen_preview(fc, colour='green', label='leaf_fphen'):
    """Create leaf_fphen preview graph.

    Creates a preview graph for the leaf_fphen fixed-day method.
    """
    astart = fc['leaf_fphen']['astart'].get_value()
    aend = fc['leaf_fphen']['aend'].get_value()
    leaf_fphen_a = fc['leaf_fphen']['leaf_fphen_a'].get_value()
    leaf_fphen_b = fc['leaf_fphen']['leaf_fphen_b'].get_value()
    leaf_fphen_c = fc['leaf_fphen']['leaf_fphen_c'].get_value()
    leaf_fphen_1 = fc['leaf_fphen']['leaf_fphen_1'].get_value()
    leaf_fphen_2 = fc['leaf_fphen']['leaf_fphen_2'].get_value()

    points = [(astart, leaf_fphen_a),
              (astart + leaf_fphen_1, leaf_fphen_b),
              (aend - leaf_fphen_2, leaf_fphen_b),
              (aend, leaf_fphen_c)]

    return wx.lib.plot.PolyLine(points=points,
                                colour=colour,
                                legend=label)
