import csv, copy, exceptions
import wx

import dose
from tools import _verbose
from resultswindow import ResultsWindow

class InputFileError(exceptions.Exception):
    pass

class InputFile:
    def __init__(self, path):
        """Only store the path to the file here.
        """
        self.path = path
        self.fields = None
        self.data = None
        
    def __iter__(self):
        """Allow 'for row in myinputfile:' constructs.
        """
        if not self.data:
            raise InputFileError("Data not yet loaded")
        else:
            return iter(self.data)

    def SetFields(self, fields):
        """Set the field order for the CSV.
        """
        self.fields = fields

    def GetFields(self):
        """Retrieve the CSV field order.
        """
        return self.fields

    def Load(self):
        """Load the data from the CSV file.
        """

        if not self.fields:
            raise InputFileError("Field order not yet set")

        file = open(self.path)

        self.linecount = 0
        self.data = []
        
        r = csv.DictReader(file, fieldnames = self.fields)

        for l in r:
            self.linecount = self.linecount + 1
            self.data.append({'lineno': self.linecount, 'data': copy.deepcopy(l)})

        file.close()

        _verbose("Loaded %s lines from %s" % (self.linecount, self.path))


class DatasetInvalidFieldset(exceptions.Exception):
    pass

class Dataset:
    def __init__(self, site_params, veg_params, output_fields):
        self.site = site_params
        self.veg = veg_params
        self.output_fields = output_fields

    def SetInputFile(self, path, fields):
        self.file = InputFile(path)
        self.file.SetFields(fields)
        self.file.Load()

    def Run(self, parent):
        # TODO: Check the fieldset
        
        dose.SetVegParams(self.veg)
        dose.params_veg.derive_d_zo()
        dose.SetSiteParams(self.site)
        dose.params_site.derive_windspeed_d_zo()
        dose.params_site.derive_o3_d_zo()

        results = []

        pd = wx.ProgressDialog('DOSE - running', 'Running calculations on input data...', 
                self.file.linecount, parent, wx.PD_APP_MODAL | wx.PD_REMAINING_TIME)

        pd.Show()

        for line in self.file:
            #print line
            dose.SetInputValues(line['data'])
            dose.inputs.derive_ustar_uh()
            dose.run.do_calcs(
                    dose.phenology.calc_sai_simple,
                    dose.r.calc_ra_simple,
                    dose.evapotranspiration.calc_aet,
                    dose.evapotranspiration.calc_pet,
                    dose.irradiance.calc_rn)
            results.append(dose.variables.__dict__)
            pd.Update(line['lineno'])

        self.results = results
        print "\n".join([",".join([str(r[k]) for k in self.output_fields]) for r in results])


    def SaveAs(self, filename):
        pass

