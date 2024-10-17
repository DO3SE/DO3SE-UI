from do3se import model
from do3se import util
from typing import List
import csv
import logging
_log = logging.getLogger('do3se.dataset')
# from itertools import ifilter


class DatasetError(Exception):
    pass


class InvalidFieldCountError(DatasetError):
    """Mismatch between specified field count and data column count."""
    pass


class RequiredFieldError(DatasetError):
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


    # Input data
    input_data can either be a list of dictionaries or a a matrix
    with shape [row_count, heading_count]

    """

    def __init__(self, input_data, input_fields, params, headings: List[str]=None):
        self.params = params
        self.options = dict()
        self.headings = headings or list(input_data[0].keys())
        self.input_data_is_matrix = headings is not None and type(
            input_data) is not dict

        self.input = input_data
        dd_key = "dd" if not self.input_data_is_matrix else self.headings.index('dd')
        ts_c_key = "ts_c" if not self.input_data_is_matrix else self.headings.index('ts_c')
        mean_temps, td_data = calc_thermal_time(self.input, dd_key, ts_c_key)
        self.input = [[*row, td] if self.input_data_is_matrix else {
            **row, "td": td} for row, td in zip(self.input, td_data)]
        headings = [*self.headings, 'td']

        # Check required fields are present
        required = [k for k, v in model.input_fields.items() if v['required']]
        for f in required:
            if not f in input_fields:
                raise RequiredFieldError([f])

        # Handle PAR/Global radiation input/derivation
        if 'par' in input_fields and 'r' in input_fields:
            self.options['r_par_method'] = model.options.r_par_use_inputs
            _log.debug('R/PAR calculation: use inputs')
        elif 'par' in input_fields:
            self.options['r_par_method'] = model.options.r_par_derive_r
            _log.debug('R/PAR calculation: derive R')
        elif 'ppfd' in input_fields:
            self.options['r_par_method'] = model.options.r_par_derive_r
            _log.debug('R/PAR calculation: derive R')
        elif 'r' in input_fields:
            self.options['r_par_method'] = model.options.r_par_derive_par
            _log.debug('R/PAR calculation: derive PAR')
        elif 'cloudfrac' in input_fields:
            self.options['r_par_method'] = model.options.r_par_derive_cloudfrac
            _log.debug('R/PAR calculation: derive PAR from cloudfrac')
        else:
            raise RequiredFieldError(['par', 'r'])

        # Calculate net radiation if not supplied
        if 'rn' in input_fields:
            self.options['rn_method'] = model.options.rn_use_input
            _log.debug('Rn calculation: use input')
        else:
            self.options['rn_method'] = model.options.rn_calculate
            _log.debug('Rn calculation: calculate')

        # Other switchable procedures
        fO3 = model.fO3_calcs[self.params.pop('fo3', model.default_fO3_calc)]
        _log.debug('fO3 calculation: "%(name)s" (%(id)s)' % fO3)
        self.options['fo3_method'] = fO3['func']

        ustar = model.ustar_calcs[self.params.pop(
            'ustar_method', model.default_ustar_calc)]
        _log.debug('ustar calculation: "%(name)s" (%(id)s)' % ustar)
        self.options['ustar_method'] = ustar['func']

        SAI = model.SAI_calcs[self.params.pop('sai', model.default_SAI_calc)]
        _log.debug('SAI calculation: "%(name)s" (%(id)s)' % SAI)
        self.options['sai_method'] = SAI['func']
        leaf_fphen = model.leaf_fphen_calcs[
            self.params.pop('leaf_fphen', model.default_leaf_fphen_calc)]
        _log.debug('leaf_fphen calculation: "%(name)s" (%(id)s)' % leaf_fphen)
        self.options['leaf_fphen_method'] = leaf_fphen['func']
        ra_method = model.ra_method[self.params.pop(
            'ra_method', model.default_ra_method)]
        self.options['ra_method'] = ra_method['func']
        fXWP = model.fXWP_calcs[self.params.pop(
            'fxwp', model.default_fXWP_calc)]
        self.options['fxwp_method'] = fXWP['func']
        fSWP = model.fSWP_calcs[self.params.pop(
            'fswp', model.default_fSWP_calc)]
        self.options['fswp_method'] = fSWP['func']
        ASW = model.ASW_calcs[self.params.pop(
            'asw', model.default_ASW_calc)]
        self.options['asw_method'] = ASW['func']
        LWP = model.LWP_calcs[self.params.pop('lwp', model.default_LWP_calc)]
        self.options['lwp_method'] = LWP['func']
        SGS_EGS = model.SGS_EGS_calcs[self.params.pop(
            'sgs_egs_calc', model.default_SGS_EGS_calc)]
        self.options['sgs_egs_method'] = SGS_EGS['func']
        gsto = model.gsto_calcs[self.params.pop(
            'gsto', model.default_gsto_calc)]
        self.options['gsto_method'] = gsto['func']
        tleaf = model.tleaf_calcs[self.params.pop(
            'tleaf', model.default_tleaf_calc)]
        self.options['tleaf_method'] = tleaf['func']

        # Soil parameters from soil type
        soil = model.soil_classes[self.params.pop(
            'soil_tex', model.default_soil_class)]
        # Allowing overriding of soil parameters
        soil['data']['soil_b'] = self.params.pop(
            'soil_b', soil['data']['soil_b']
        )
        soil['data']['fc_m'] = self.params.pop(
            'fc_m', soil['data']['fc_m']
        )
        soil['data']['swp_ae'] = self.params.pop(
            'swp_ae', soil['data']['swp_ae']
        )
        soil['data']['ksat'] = self.params.pop(
            'ksat', soil['data']['ksat']
        )
        self.params.update(soil['data'])


        # Use/copy measurement vegetation heights
        u_h = self.params.pop('u_h')
        self.params['u_h'] = self.params['h'] if u_h['disabled'] else u_h['value']
        o3_h = self.params.pop('o3_h')
        self.params['o3_h'] = self.params['h'] if o3_h['disabled'] else o3_h['value']

        if SGS_EGS['func'] == 3:
            sgs_set = False
            egs_set = False
            astart_set = False
            fphen_1_set = False
            leaf_f_phen_1_set = False
            leaf_f_phen_2_set = False
            mid_anthesis_acc_value = mean_temps[self.params['mid_anthesis']]
            for i, value in enumerate(mean_temps):
                if value > (mid_anthesis_acc_value - 1075) and not sgs_set and mid_anthesis_acc_value > 1075:
                    self.params['sgs'] = i
                    sgs_set = True
                if value > (mid_anthesis_acc_value + 700) and not egs_set:
                    self.params['egs'] = i
                    egs_set = True
                if value > (mid_anthesis_acc_value - 456) and not astart_set and mid_anthesis_acc_value > 456:
                    self.params['astart'] = i
                    astart_set = True
                if value > (mid_anthesis_acc_value - 795) and not fphen_1_set and mid_anthesis_acc_value > 795:
                    fphen_1_day = i
                    fphen_1_set = True
                if value > (mid_anthesis_acc_value + 100) and not leaf_f_phen_1_set:
                    leaf_fphen_1_day = i
                    leaf_f_phen_1_set = True
                if value > (mid_anthesis_acc_value + 525) and not leaf_f_phen_2_set:
                    leaf_fphen_2_day = i
                    leaf_f_phen_2_set = True
                i = i + 1

            if (
                not fphen_1_set or not egs_set or not leaf_f_phen_1_set or not leaf_f_phen_2_set or not sgs_set or not astart_set
            ):
                if self.params.get('allow_invalid_td', False):
                    _log.warning(
                        "Failed to calculate SGS/EGS, using input values")
                    # Set to invalid values so that fphen and leaf_fphen are not calculated
                    self.params['sgs'] = -999
                    self.params['egs'] = 999
                    self.params['astart'] = -998
                    self.params['fphen_1'] = 0
                    self.params['aend'] = 998
                    self.params['leaf_fphen_1'] = 0
                    self.params['leaf_fphen_2'] = 0
                    self.params['fphen_4'] = 999
                    self.params['invalid_td'] = True
                else:
                    raise Exception(
                        "Failed to calculate SGS/EGS, use allow_invalid_td to ignore")

            else:
                self.params['fphen_1'] = fphen_1_day - self.params['sgs']

                self.params['aend'] = self.params['egs'] + 1

                self.params['leaf_fphen_1'] = leaf_fphen_1_day - \
                    self.params['astart']

                self.params['leaf_fphen_2'] = self.params['aend'] - \
                    leaf_fphen_2_day

                self.params['fphen_4'] = self.params['egs'] - \
                    self.params['mid_anthesis']

        _log.info("Loaded %d data rows" % len(self.input))

    def run(self, progressbar=None, progress_interval=100):
        """Run the DO3SE model with this dataset.

        If a :class:`wx.Gauge` is supplied as the *progressbar* argument, it
        will have it's range set to the number of input rows, and will be
        updated every *progress_interval* rows.

        Returns a :class:`Resultset` object with the model run results.
        """
        skippedrows = 0

        # These parameters need special handling
        co2_const = self.params.pop('co2_constant')

        # Initialise function switchboard
        util.setattrs(model.options, self.options)
        # Load parameters
        util.setattrs(model.parameters, self.params)

        # Initialise the model
        _log.info("Initialising DOSE Fortran model")
        model.run.initialise()

        # Handle special parameters
        if not co2_const['disabled']:
            _log.debug('Using constant CO2 concentration: %s ppm' %
                       co2_const['value'])
            util.setattrs(model.inputs, {'co2': co2_const['value']})

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
                    progressbar.SetValue(
                        progressbar.GetValue() + progress_interval)

            # Skip rows that are missing values
            if not self.input_data_is_matrix and '' in row.values():
                skippedrows += 1
                continue
            # Catch TypeError - usually caused by some attributes being None
            # because there weren't enough fields in the input
            # TODO: Handle this differently?
            try:
                if self.input_data_is_matrix:
                    util.setattrsb(model.inputs, row, self.headings)
                else:
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
            w.writerow(
                dict((f, model.output_fields[f]['short']) for f in fields))

        if period is None:
            w.writerows(self.data)
            _log.info('Wrote all %d rows' % (len(self.data),))
        else:
            start, end = period
            w.writerows(
                list(filter(lambda r: r['dd'] >= start and r['dd'] <= end, self.data)))
            _log.info('Wrote rows from dd=%d to dd=%d' % (start, end))


class NoDataError(DatasetError):
    def __init__(self):
        DatasetError.__init__(self, 'No data in file')


class NotEnoughColumnsError(DatasetError):
    def __init__(self):
        DatasetError.__init__(self, 'Not enough columns in input')


class NotEnoughTrimError(DatasetError):
    def __init__(self):
        DatasetError.__init__(self, 'Non-numeric data at start of input, maybe'
                              ' not enough header rows were trimmed?')


class InvalidDataError(DatasetError):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        DatasetError.__init__(self, 'Invalid/empty value at row %d, '
                                    'column %d' % (row, col))


class UnquotedStringError(DatasetError):
    def __init__(self):
        DatasetError.__init__(self, 'CSV file invalid, unquoted string found')


def data_from_csv(infile, keys, trim):
    """Load data from CSV file.

    Data is loaded from *infile* as a list of dictionaries using *keys* to
    determine which key to store column's value under.  Lines are stripped from
    the beginning of the file according to *trim* to skip header rows.

    The requirements for the data input are more restrictive than
    :class:`csv.DictReader` is capable of, so instead the reading is done with
    a plain :class:`csv.reader` and the data checked before being used.  This
    function attempts to anticipate all common errors, raising an exception
    (which is always a subclass of :class:`DatasetError`) when a problem is
    encountered.  Among the errors handled are:

    * Empty data file
    * Not enough columns
    * Missing values
    * Invalid values
    * Not enough rows trimmed for headers
    """
    data = []

    # Skip header rows
    try:
        for x in range(trim):
            next(infile)
    except StopIteration:
        raise NoDataError()

    csvreader = csv.reader(infile, quoting=csv.QUOTE_NONNUMERIC)

    # Look at the first row, we can tell a lot from it...
    try:
        row1 = next(csvreader)
    except StopIteration:
        raise NoDataError()
    except ValueError:
        raise UnquotedStringError()
    else:
        # Check that there are enough input columns to satisfy the input format
        if len(row1) < len(keys):
            raise NotEnoughColumnsError()

        # Check for non-empty strings, means header rows might still exist
        for x in row1[:len(keys)]:
            if isinstance(x, str) and len(x) > 0:
                raise NotEnoughTrimError()

        # Otherwise, in general, strings mean values couldn't be converted to float
        for i, x in enumerate(row1[:len(keys)], 1):
            if isinstance(x, str):
                raise InvalidDataError(trim + 1, i)
        # Empty strings mean missing values
        for i, x in enumerate(row1[:len(keys)], 1):
            if x == '':
                raise InvalidDataError(trim + 1, i)

        # If we got this far, we can go ahead and add the first row
        data.append(dict(zip(keys, row1)))

    # Run for the rest of the data
    try:
        for r, row in enumerate(csvreader, trim + 2):
            for c, val in enumerate(row[:len(keys)], 1):
                if isinstance(val, str):
                    raise InvalidDataError(r, c)
            data.append(dict(zip(keys, row)))
    except ValueError:
        raise UnquotedStringError()

    return data


def calc_mean(temp_list):
    temp_list_sum = sum(temp_list)
    temp_list_len = len(temp_list)
    mean_value = float(temp_list_sum) / float(temp_list_len)
    if mean_value > 0:
        return mean_value
    return 0


def calc_thermal_time(data, dd_key="dd", ts_c_key="ts_c"):
    day_temps = []
    mean_temps = [0]*367
    set_day = None
    for row in data:
        dd, ts_c = row[dd_key],row[ts_c_key]
        if set_day == None:
            set_day = int(dd)
            day_temps = []
            day_temps.append(ts_c)
            continue
        if int(dd) != set_day:
            mean_temps[set_day] = calc_mean(day_temps)
            if set_day > 1:
                mean_temps[set_day] = mean_temps[set_day] + \
                    mean_temps[set_day - 1]
            day_temps = []
            set_day = int(dd)
            day_temps.append(ts_c)
        else:
            day_temps.append(ts_c)
    else:
        mean_temps[set_day] = calc_mean(day_temps)
        if set_day > 1:
            mean_temps[set_day] = mean_temps[set_day] + mean_temps[set_day - 1]
    td = [mean_temps[int(row[dd_key])] for row in data]

    return mean_temps, td
