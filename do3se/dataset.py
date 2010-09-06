import csv
import logging
_log = logging.getLogger('do3se.dataset')

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

    *parameters* is a dictionary-like object of parameter values, and will be
    modified by the constructor as "virtual" parameters are replaced with real
    parameters and control parameters are removed.
    """
    def __init__(self, infile, params):
        self.params = params
        self.switchboard = dict()

        # Extract parameters which control loading of data
        input_fields = self.params.pop('input_fields', [])
        input_trim = self.params.pop('input_trim', 0)

        # Check required fields are present
        required = [k for k,v in model.input_fields.iteritems() if v['required']]
        for f in required:
            if not f in input_fields:
                raise RequiredFieldError([f])
        
        # Handle PAR/Global radiation input/derivation
        if 'par' in input_fields and 'r' in input_fields:
            self.switchboard['r_par_method'] = model.switchboard.r_par_use_inputs
            _log.debug('R/PAR calculation: use inputs')
        elif 'par' in input_fields:
            self.switchboard['r_par_method'] = model.switchboard.r_par_derive_r
            _log.debug('R/PAR calculation: derive R')
        elif 'r' in input_fields:
            self.switchboard['r_par_method'] = model.switchboard.r_par_derive_par
            _log.debug('R/PAR calculation: derive PAR')
        else:
            raise RequiredFieldError(['par', 'r'])

        # Calculate net radiation if not supplied
        if 'rn' in input_fields:
            self.switchboard['rn_method'] = model.switchboard.rn_use_input
            _log.debug('Rn calculation: use input')
        else:
            self.switchboard['rn_method'] = model.switchboard.rn_calculate
            _log.debug('Rn calculation: calculate')

        # Other switchable procedures
        fO3 = model.fO3_calcs[self.params.pop('fo3', model.default_fO3_calc)]
        _log.debug('fO3 calculation: "%(name)s" (%(id)s)' % fO3)
        self.switchboard['fo3_method'] = fO3['func']
        SAI = model.SAI_calcs[self.params.pop('sai', model.default_SAI_calc)]
        _log.debug('SAI calculation: "%(name)s" (%(id)s)' % SAI)
        self.switchboard['sai_method'] = SAI['func']
        leaf_fphen = model.leaf_fphen_calcs[
                self.params.pop('leaf_fphen', model.default_leaf_fphen_calc)]
        _log.debug('leaf_fphen calculation: "%(name)s" (%(id)s)' % leaf_fphen)
        self.switchboard['leaf_fphen_method'] = leaf_fphen['func']
        # TODO: switchable with heat flux calculation?
        self.switchboard['ra_method'] = model.switchboard.ra_simple
        fXWP = model.fXWP_calcs[self.params.pop('fxwp', model.default_fXWP_calc)]
        self.switchboard['fxwp_method'] = fXWP['func']
        fSWP = model.fSWP_calcs[self.params.pop('fswp', model.default_fSWP_calc)]
        self.switchboard['fswp_method'] = fSWP['func']
        LWP = model.LWP_calcs[self.params.pop('lwp', model.default_LWP_calc)]
        self.switchboard['lwp_method'] = LWP['func']

        # Soil parameters from soil type
        soil = model.soil_classes[self.params.pop('soil_tex', model.default_soil_class)]
        self.params.update(soil['data'])

        # Use/copy measurement vegetation heights
        u_h = self.params.pop('u_h')
        self.params['u_h'] = self.params['h'] if u_h['disabled'] else u_h['value']
        o3_h = self.params.pop('o3_h')
        self.params['o3_h'] = self.params['h'] if o3_h['disabled'] else o3_h['value']

        # Skip the trimmed lines
        for n in xrange(0, input_trim): infile.next()
        # Load all of the data
        _log.debug("Input data format: %s" % (",".join(input_fields)))
        try:
            self.input = list(csv.DictReader(infile, fieldnames = input_fields, 
                quoting=csv.QUOTE_NONNUMERIC))
        except ValueError:
            # ValueError here usually means the headers didn't get trimmed
            raise InsufficientTrimError()

        _log.info("Loaded %d data rows" % len(self.input))

    def run(self):
        """Run the DO3SE model with this dataset.

        :returns:   2-tuple of ``(result_count, skipped_row_count)``
        """
        skippedrows = 0

        # Initialise function switchboard
        util.setattrs(model.switchboard, self.switchboard)
        # Load parameters
        util.setattrs(model.parameters, self.params)

        # Initialise the model
        _log.info("Initialising DOSE Fortran model")
        model.run.initialise()

        self.results = []
        # Iterate through dataset
        _log.info("Running calculations ...")
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

        _log.info("Got %d results" % len(self.results))
        return (len(self.results), skippedrows)


    def save(self, outfile, fields, headers=False, period=None):
        """Save the results to a CSV file according to the output format.

        :param outfile:     The file to save results to
        :param fields:      Identifiers of fields to include in output, in order
        :param headers:     Include field headers in output?
        :param period:      Day range, inclusive, to include rows for: ``(start, end)``
        """
        _log.debug("Output data format: %s" % (",".join(fields)))

        w = csv.DictWriter(outfile, fieldnames=fields, extrasaction='ignore',
                quoting=csv.QUOTE_NONNUMERIC)

        if headers:
            w.writerow(dict( (f, model.output_fields[f]['short']) for f in fields ))
        
        count = 0
        if period:
            for r in self.results:
                if r['dd'] >= period[0] and r['dd'] <= period[1]:
                    w.writerow(r)
                    count += 1
        else:
            w.writerows(self.results)
            count = len(self.results)
        
        _log.info("Wrote %d records" % (count,))
