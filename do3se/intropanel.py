# coding: utf-8

import wx
from wx.html import HtmlWindow

_intro_text = u"""
<p>
DO<sub>3</sub>SE (Deposition of Ozone for Stomatal Exchange) is a dry deposition
model designed to estimate the total and stomatal deposition (or flux) of ozone
(O<sub>3</sub>) to selected European land-cover types and plant species.
DO<sub>3</sub>SE has been developed to estimate the risk of O<sub>3</sub> damage
to European vegetation and is capable of providing flux-modelling estimates
according to UNECE LRTAP (Long-Range Transboundary Air Pollution) methodologies
for effects-based risk assessment.  An almost identical version of
DO<sub>3</sub>SE has been embedded in the EMEP photochemical model to provide
estimates of total O<sub>3</sub> deposition and O<sub>3</sub> risk providing an
opportunity to formulate effects-based O<sub>3 precursor emission
reduction strategies for Europe.
</p>

<p align="center">
<img src="resources/resistance.png" />
</p>

<p>
DO<sub>3</sub>SE assumes that the key resistances to O<sub>3</sub> deposition
from an O<sub>3</sub> concentration (C<sub>O3</sub>) at some reference height in
the atmosphere to the ground surface are: the aerodynamic resistance
(R<sub>a</sub>), the quasi-laminar sub-layer resistance (R<sub>b</sub>) above
the canopy, and the surface resistance (R<sub>sur</sub>).  R<sub>sur</sub>
comprises two resistance paths in series; the stomatal and non-stomatal
resistance.  The latter represents within canopy aerodynamic resistance
(R<sub>inc</sub>) and subsequent soil resistance to decomposition at the soil
surface (R<sub>soil</sub>) which encompasses features such as leaf litter and
ground vegetation under forest canopies; as well as resistance to adsorption to
the external plant parts (R<sub>ext</sub>) including cuticle, bark etc.  The
stomatal resistance term (R<sub>sto</sub>) determines the resistance to
O3 uptake by the vegetation and hence is relevant for risk assessment
since it is via the stomates that O<sub>3</sub> enters and causes damage to
vegetation.
</p>

<p>
This interfaced version of the model (DO3SE_INTv1.0) is provided for users to
estimate total and stomatal O3 flux on a site-specific basis
according to local meteorological and O3 concentration data.
Default parameterisation is provided for certain cover-types and species though
users have the option of using their own local parameterisation.  The model
provides estimates of key deposition parameters including: total deposition
(F<sub>tot</sub>), deposition velocity (V<sub>g</sub>), stomatal conductance
(g<sub>sto</sub>) and accumulated leaf-level stomtal flux above a threshold
(AFstY).
</p>

<p>
Full referenced documentation of the DO<sub>3</sub>SE model and a DO3SE_INTv1.0
user manual is provided with this model interface.
</p>

<p>
<b>For any comments or queries please contact either Patrick Büker
(pb25@york.ac.uk) or Lisa Emberson (l.emberson@york.ac.uk).</b>
</p>

<h5>Acknowledgements</h5>
<p>
The development of this interface has been made possible through funding
provided by the UK Department of Environment, Food and Rural Affairs (Defra) and
through institutional support provided to the Stockholm Environment Institute
from the Swedish International Development Agency (Sida).
</p>
"""

class IntroPanel(wx.Panel):
    def __init__(self, app, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        html = HtmlWindow(self)
        s.Add(html, 1, wx.EXPAND)

        html.SetPage(_intro_text)
