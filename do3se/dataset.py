import csv
import logging

import util
import model

class InvalidFieldCountError(Exception):
    """Mismatch between specified field count and data column count."""
    pass


class InsufficientTrimError(Exception):
    """Not enough lines trimmed from beginning of data.

    This exception occurs when invalid data was found when attempting to read
    from a CSV file.  This is usually due to headers being present because not
    enough lines were trimmed from the beginning.
    """
    pass


class RequiredFieldError(Exception):
    """One or more required fields missing from input format."""
    def __init__(self, fields):
        self.fields = fields


class Dataset:
    """Load and process dataset.

    This class is responsible for loading input data, running the model over
    it, storing the results, and saving them to a file.

    :param infile:      A file-like object to read from
    :param fields:      Names of the fields/columns in the input file
    :param trim:        Number of lines to trim from beginning of file, to
                        skip the existing column headers
    :param siteparams:  Site parameters
    :param vegparams:   Vegetation parameters
    """
    def __init__(self, infile, fields, trim, siteparams, vegparams):
        """Initialise the Dataset object and load the data from the file."""
        self.siteparams = siteparams.copy()
        self.vegparams = vegparams.copy()

        # Check required fields are present
        required = (x['variable'] for x in model.input_fields if x['required'])
        for f in required:
            if not f in fields:
                raise RequiredFieldError([f])
        
        # Handle PAR/Global radiation input/derivation
        if 'par' in fields and 'r' in fields:
            self.r_par_method = model.switchboard.r_par_use_inputs
        elif 'par' in fields:
            self.r_par_method = model.switchboard.r_par_derive_r
        elif 'r' in fields:
            self.r_par_method = model.switchboard.r_par_derive_par
        else:
            raise RequiredFieldError(['par', 'r'])

        # Calculate net radiation if not supplied
        if 'rn' in fields:
            self.rn_method = model.switchboard.rn_use_input
        else:
            self.rn_method = model.switchboard.rn_calculate

        # Other switchable procedures
        fO3 = model.fO3_calc_map[self.vegparams.pop('fo3', model.default_fO3_calc)]
        logging.debug('fO3 calculation: "%(name)s" (%(id)s)' % fO3)
        self.fo3_method = fO3['func']
        SAI = model.SAI_calc_map[self.vegparams.pop('sai', model.default_SAI_calc)]
        logging.debug('SAI calculation: "%(name)s" (%(id)s)' % SAI)
        self.sai_method = SAI['func']
        leaf_fphen = model.leaf_fphen_calc_map[
                self.vegparams.pop('leaf_fphen', model.default_leaf_fphen_calc)]
        logging.debug('leaf_fphen calculation: "%(name)s" (%(id)s)' % leaf_fphen)
        self.leaf_fphen_method = leaf_fphen['func']
        # TODO: switchable with heat flux calculation?
        self.ra_method = model.switchboard.ra_simple
        fXWP = model.fXWP_calc_map[self.vegparams.pop('fxwp', model.default_fXWP_calc)]
        self.fxwp_method = fXWP['func']

        # Soil parameters from soil type
        soil = model.soil_class_map[self.siteparams.pop('soil_tex',
                                                        model.default_soil_class)]
        self.siteparams.update(soil['data'])

        if self.siteparams['u_h_copy']:
            self.siteparams['u_h'] = self.vegparams['h']
        if self.siteparams['o3_h_copy']:
            self.siteparams['o3_h'] = self.vegparams['h']

        # Skip the trimmed lines
        for n in xrange(0,trim): infile.next()
        # Load all of the data
        logging.debug("Input data format: %s" % (",".join(fields)))
        try:
            self.input = list(csv.DictReader(infile, fieldnames = fields, 
                quoting=csv.QUOTE_NONNUMERIC))
        except ValueError:
            # ValueError here usually means the headers didn't get trimmed
            raise InsufficientTrimError()

        logging.info("Loaded %d data rows" % len(self.input))

    def run(self):
        """Run the DO3SE model with this dataset.

        :returns:   2-tuple of ``(result_count, skipped_row_count)``
        """
        skippedrows = 0

        # Load parameters into F model
        util.setattrs(model.params_veg, self.vegparams)
        util.setattrs(model.params_site, self.siteparams)

        # Initialise the model
        logging.info("Initialising DOSE Fortran model")
        model.run.initialise()

        # Setup function switchboard
        model.switchboard.sai_method = self.sai_method
        model.switchboard.rn_method = self.rn_method
        model.switchboard.leaf_fphen_method = self.leaf_fphen_method
        model.switchboard.ra_method = self.ra_method
        model.switchboard.fo3_method = self.fo3_method
        model.switchboard.fxwp_method = self.fxwp_method
        model.switchboard.r_par_method = self.r_par_method

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
            try:
                util.setattrs(model.inputs, row)
            except TypeError:
                raise InvalidFieldCountError()

            model.run.calculate_row()
            self.results.append(model.extract_outputs())

        logging.info("Got %d results" % len(self.results))
        return (len(self.results), skippedrows)


    def save(self, outfile, fields, headers=False, period=None):
        """Save the results to a CSV file according to the output format.

        :param outfile:     The file to save results to
        :param fields:      Identifiers of fields to include in output, in order
        :param headers:     Include field headers in output?
        :param period:      Day range, inclusive, to include rows for: ``(start, end)``
        """
        logging.debug("Output data format: %s" % (",".join(fields)))

        w = csv.DictWriter(outfile, fieldnames=fields, extrasaction='ignore',
                quoting=csv.QUOTE_NONNUMERIC)

        if headers:
            w.writerow(dict( (f, model.output_field_map[f]['short']) for f in fields ))
        
        count = 0
        if period:
            for r in self.results:
                if r['dd'] >= period[0] and r['dd'] <= period[1]:
                    w.writerow(r)
                    count += 1
        else:
            w.writerows(self.results)
            count = len(self.results)
        
        logging.info("Wrote %d records" % (count,))
