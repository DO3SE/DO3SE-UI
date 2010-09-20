import csv
import logging
_log = logging.getLogger('do3se.dataset')
from itertools import ifilter, groupby

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


def generate_thermal_time(data):
    """Generate daily average and thermal time data.

    Daily average and thermal time values can be calculated from hourly
    temperature values.  This function fills in the ``t_avg`` and ``t_sum``
    input values for each row.
    """
    t_sum = 0.0
    for dd, _day in groupby(data, lambda x: x['dd']):
        day = list(_day)
        t_avg = sum(map(lambda x: x['ts_c'], day)) / len(day)
        if t_avg > 0.0:
            t_sum += t_avg
        for row in day:
            row['t_avg'] = t_avg
            row['t_sum'] = t_sum


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
        SGS_EGS = model.SGS_EGS_calcs[self.params.pop('sgs_egs_calc', model.default_SGS_EGS_calc)]
        self.switchboard['sgs_egs_method'] = SGS_EGS['func']

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
        
        # Generate data for fields not supplied (if possible)
        if 't_avg' not in input_fields or 't_sum' not in input_fields:
            _log.info('Generating values for T_avg and T_sum')
            generate_thermal_time(self.input)

    def season_from_thermal_time(self):
        """Get SGS/EGS based on thermal time.

        SGS is defined as the first day ``T_avg`` is above 0 degrees.  EGS is
        the day that ``T_sum`` exceeds 1775.  The result is returned as a
        ``(sgs, egs)`` pair.
        """
        sgs = -1
        egs = -1
        for row in self.input:
            if row['t_avg'] > 0.0:
                sgs = row['dd']
                break
        for row in self.input:
            if row['t_sum'] > 1775:
                egs = row['dd']
                break
        return (sgs, egs)

    def run(self, progressbar=None, progress_interval=100):
        """Run the DO3SE model with this dataset.

        If a :class:`wx.Gauge` is supplied as the *progressbar* argument, it
        will have it's range set to the number of input rows, and will be
        updated every *progress_interval* rows.

        Returns a :class:`Resultset` object with the model run results.
        """
        skippedrows = 0

        # Initialise function switchboard
        util.setattrs(model.switchboard, self.switchboard)
        # Load parameters
        util.setattrs(model.parameters, self.params)

        # Initialise the model
        _log.info("Initialising DOSE Fortran model")
        model.run.initialise()

        # Initialise progress bar
        if progressbar is not None:
            progressbar.SetRange(len(self.input))
            progressbar.SetValue(0)
        prog_counter = progress_interval

        results = []
        # Iterate through dataset
        _log.info("Running calculations ...")
        for row in self.input:
            if progressbar is not None:
                prog_counter -= 1
                if prog_counter == 0:
                    prog_counter = progress_interval
                    progressbar.SetValue(progressbar.GetValue() + progress_interval)

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
            results.append(model.extract_outputs())

        if progressbar is not None:
            progressbar.SetValue(0)

        _log.info("Got %d results" % len(results))
        return Resultset(results, skippedrows, self.params)


class Resultset:
    """Results data from a model run.

    Contains the model run results as :attr:`data`, the number of rows skipped
    as :attr:`skipped`, the (modified) parameters used for the model run as
    :attr:`params`, and provides the ability to :meth:`save` the results to a
    file.
    """
    def __init__(self, data, skipped, params):
        self.data = data
        self.skipped = skipped
        self.params = params

    def save(self, outfile, fields, headers=False, period=None):
        """Save results to a CSV file.

        Save the result columns specified in *fields* to *outfile* in CSV
        format.  If *headers* is True, the first row consists of the short
        field description for each row (from :mod:`do3se.model.output_fields`).
        If a pair is supplied as the *period* argument, it is treated as an
        (inclusive) day range for which results should be output, otherwise
        all rows are written.
        """
        _log.debug("Output data format: %s" % (",".join(fields)))

        w = csv.DictWriter(outfile, fieldnames=fields, extrasaction='ignore',
                quoting=csv.QUOTE_NONNUMERIC)

        if headers:
            w.writerow(dict( (f, model.output_fields[f]['short']) for f in fields ))
        
        if period is None:
            w.writerows(self.data)
            _log.info('Wrote all %d rows' % (len(self.data),))
        else:
            start, end = period
            w.writerows(ifilter(lambda r: r['dd'] >= start and r['dd'] <= end, self.data))
            _log.info('Wrote rows from dd=%d to dd=%d' % (start, end))
