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

class Dataset:
    def __init__(self, filename, fields, trim=1):
        """Constructor

        Initialise the Dataset object and load the data from the file.
        
        filename:   The path to the file to load
        fields:     Fields contained in the file, to be used as dict keys
        trim:       The number of lines to trim from the beginning of the file
        """
        self.filename = filename

        # Open the file
        file = open(self.filename)
        # Skip the trimmed lines
        for n in xrange(0,trim): file.next()
        # Load all of the data
        logging.debug("Input data format: %s" % (",".join(fields)))
        self.input = list(csv.DictReader(file, fieldnames = fields, 
            quoting=csv.QUOTE_NONNUMERIC))
        # Close the file
        file.close()

        logging.info("Loaded %d lines from '%s'" % (len(self.input), self.filename))
        #logging.debug(self.input)

    def run(self, siteparams, vegparams):
        # Setup parameters
        
        # Do vegetation parameters first, as some site parameters depend on this
        dose.params_veg.derive_d_zo()
        # ...
        util.setattrs(dose.params_site, siteparams)

        # Initialise the module
        logging.info("Initialising DOSE Fortran model")
        dose.run.init(int(siteparams['u_h_copy']), int(siteparams['o3_h_copy']))

        self.results = []
        # Iterate through dataset
        logging.info("Running calculations ...")
        for row in self.input:
            util.setattrs(dose.inputs, row)
            dose.inputs.derive_ustar_uh()
            dose.run.do_calcs(
                    dose.phenology.calc_sai_simple,
                    dose.r.calc_ra_simple,
                    dose.evapotranspiration.calc_aet,
                    dose.evapotranspiration.calc_pet,
                    dose.irradiance.calc_rn
            )
            self.results.append(util.getattrs_f(dose.variables, 
                ['ftemp', 'fvpd', 'pet', 'aet', 'ei', 'flight', 'leaf_flight', 
                    'rn', 'lai', 'sai', 'fphen', 'leaf_fphen', 'ra', 'rb', 
                    'rsur', 'rinc', 'rsto', 'rgs', 'gsto', 'gsto_pet', 'pwp', 
                    'asw', 'sn_star', 'sn', 'per_vol', 'smd', 'swp', 'wc', 
                    'precip', 'rsto_pet', 'fswp', 'o3_ppb', 'o3_nmol_m3', 'vd', 
                    'ftot', 'fst', 'afsty', 'ot40', 'aot40']
            ))

        logging.info("Got %d results" % len(self.results))


    def save(self, filename, fields, headers=False):
        logging.info("Writing data to '%s' ..." % filename)
        logging.debug("Output data format: %s" % (",".join(fields)))

        file = open(filename, "w")
        w = csv.DictWriter(file, fieldnames=fields, extrasaction='ignore',
                quoting=csv.QUOTE_NONNUMERIC)
        if headers:
            w.writerow(dict(zip(fields, fields)))
        w.writerows(self.results)
        file.close()
        logging.info("Wrote %d records" % len(self.results))
        

if __name__ == '__main__':
    d = Dataset(
            'notes/sample_hourly_noLAI.csv',
            ['mm', 'mdd', 'dd', 'hr', 'ts_c', 'vpd', 'uh_zr', 'precip', 'p',
                'o3_ppb_zr', 'hd', 'r', 'par'],
            2
    )

    d.run()

    d.save('dataset-test.csv', [
        #'rn',
        'ra',
        'rb',
        'rsur',
        'rinc',
        'rsto',
        #'gsto',
        'rgs',
        'vd',
        #'o3_ppb',
        #'o3_nmol_m3',
        #'fst',
        #'afsty',
        #'ftot',
        #'ot40',
        #'aot40',
        #'aet',
        #'swp',
        #'per_vol',
        #'smd', 
        ], headers=True)

