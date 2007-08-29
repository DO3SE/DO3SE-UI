import wx
from tools import _verbose

class FloatCtrl(wx.TextCtrl):
    def __init__(self):
        p = wx.PreTextCtrl()
        self.PostCreate(p)

        self.default = 0.0
        self.min = None
        self.max = None

        self.Bind(wx.EVT_TEXT, self.OnChange)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

        self.SetValue(str(self.default))

    def OnChange(self, evt):
        """Validate input value whenever it changes.

        Check that the input value can be converted to a floating-point number
        and that it's within range if a range is specified.
        """
        if not self.GetValue():
            self.floatvalue = self.default
        else:
            try:
                # Try to turn the input string into a floating-point value
                self.floatvalue = float(self.GetValue())

                # --- This stuff only happend on success ---
                # Check if the value is in range if a range is set
                if ((not self.min is None) and (self.floatvalue < self.min)) \
                        or ((not self.max is None) and (self.floatvalue > self.max)):
                    self.OnValidationFailed()
                else:
                    self.OnValidationSuccess()
            except ValueError:
                self.OnValidationFailed()
    
    def OnKillFocus(self, evt):
        """Range check value and update display.

        If a range has been set, clip the value to be within that range and then
        update the display to match the most recent valid value.
        """
        if not self.min is None:
            self.floatvalue = max(self.min, self.floatvalue)
        if not self.max is None:
            self.floatvalue = min(self.max, self.floatvalue)
        self.ChangeValue(self.floatvalue)
        self.OnChange(None)

    def OnValidationSuccess(self):
        self.valid = True
        self.SetBackgroundColour(wx.NullColour)
        self.Refresh()

    def OnValidationFailed(self):
        self.valid = False
        self.SetBackgroundColour(wx.Colour(255, 200, 200))
        self.Refresh()

    def GetFloat(self):
        return self.floatvalue

    def SetValue(self, value):
        self.floatvalue = float(value)
        wx.TextCtrl.SetValue(self, str(value))

    def ChangeValue(self, value):
        self.floatvalue = float(value)
        wx.TextCtrl.ChangeValue(self, str(value))

    def IsValid(self):
        return self.valid

    def SetRange(self, *args):
        if len(args) == 1:
            self.min = args[0][0]
            self.max = args[0][1]
        elif len(args) == 2:
            self.min = args[0]
            self.max = args[1]
        else:
            raise ValueError("SetRange requires 2 arguments or a 2-item tuple")

        assert self.min < self.max

    def SetMin(self, value):
        self.min = value
        self.Validate()

    def SetMax(self, value):
        self.max = value
        self.Validate()

    def SetDefault(self, value):
        self.default = value
        self.Validate()

