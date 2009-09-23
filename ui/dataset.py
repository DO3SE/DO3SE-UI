################################################################################
# Data set handler
#
# This is the class responsible for loading input data, running the model, and 
# saving the results.
#
# TODO: Add parameters to the run() method
################################################################################

import csv
import wx

from app import logging, app
import util
import dose

class InvalidFieldCountError:
    def __init__(self):
        wx.MessageBox("Number of fields in the input file does not match the number of fields selected!", 
                app.title, wx.OK|wx.ICON_ERROR, app.toplevel)

class InsufficientTrimError:
    def __init__(self):
        wx.MessageBox("Some of the data was the wrong type - is the number of lines to trim from the input set correctly?",
                app.title, wx.OK|wx.ICON_ERROR, app.toplevel)

class Dataset:
    def __init__(self, filename, fields, trim, siteparams, vegparams):
        """Constructor

        Initialise the Dataset object and load the data from the file.
        
        filename:   The path to the file to load
        fields:     Fields contained in the file, to be used as dict keys
        trim:       The number of lines to trim from the beginning of the file
        siteparams: Site parameters
        vegparams:  Vegetation parameters
        """
        self.filename = filename
        self.siteparams = siteparams
        self.vegparams = vegparams

        # Set up default procedures
        self.sai = dose.phenology.calc_sai_simple
        self.leaf_fphen = dose.leaf_fphen_calc_map[dose.default_leaf_fphen_calc]['func']
        self.ra = dose.r.calc_ra_simple
        self.rn = dose.irradiance.calc_rn
        # Calculation between PAR and R
        def f(): pass
        self.par_r = f

        # Open the file
        file = open(self.filename)
        # Skip the trimmed lines
        for n in xrange(0,trim): file.next()
        # Load all of the data
        logging.debug("Input data format: %s" % (",".join(fields)))
        try:
            self.input = list(csv.DictReader(file, fieldnames = fields, 
                quoting=csv.QUOTE_NONNUMERIC))
        except ValueError:
            # ValueError here usually means the headers didn't get trimmed
            raise InsufficientTrimError()

        # Close the file
        file.close()

        logging.info("Loaded %d lines from '%s'" % (len(self.input), self.filename))

    def run(self):
        skippedrows = 0

        # Copy parameters (to avoid breaking whatever else might be using them)
        vegparams = self.vegparams.copy()
        siteparams = self.siteparams.copy()
        # Replace soil_tex (if it exists) with soil parameters
        siteparams.update(dose.soil_class_map[siteparams.pop('soil_tex', dose.default_soil_class)]['data'])
        # Handle leaf_fphen
        self.leaf_fphen = dose.leaf_fphen_calc_map[vegparams.pop('leaf_fphen', dose.default_leaf_fphen_calc)]['func']

        # Setup parameters
        
        # Do vegetation parameters first, as some site parameters depend on this
        util.setattrs(dose.params_veg, vegparams)
        dose.params_veg.derive_d_zo()
        util.setattrs(dose.params_site, siteparams)

        # Initialise the module
        logging.info("Initialising DOSE Fortran model")
        dose.run.init(int(self.siteparams['u_h_copy']), int(self.siteparams['o3_h_copy']))

        self.results = []
        # Iterate through dataset
        logging.info("Running calculations ...")
        for row in self.input:
            # Skip rows that are missing values
            if '' in row.values():
                skippedrows += 1
                continue
            # Catch TypeError - usually caused by some attributes being None 
            # because there weren't enough fields in the input
            # TODO: Handle this differently?
            try: util.setattrs(dose.inputs, row)
            except TypeError: raise InvalidFieldCountError()

            self.par_r()
            dose.inputs.derive_ustar_uh()
            dose.run.do_calcs(self.sai, self.leaf_fphen, self.ra, self.rn)
            self.results.append(dose.extract_outputs())

        logging.info("Got %d results" % len(self.results))
        return (len(self.results), skippedrows)


    def save(self, filename, fields, headers=False):
        logging.info("Writing data to '%s' ..." % filename)
        logging.debug("Output data format: %s" % (",".join(fields)))

        file = open(filename, "wb")
        w = csv.DictWriter(file, fieldnames=fields, extrasaction='ignore',
                quoting=csv.QUOTE_NONNUMERIC)
        if headers:
            w.writerow(dict( (f, dose.output_field_map[f]['short']) for f in fields ))
        w.writerows(self.results)
        file.close()
        logging.info("Wrote %d records" % len(self.results))
