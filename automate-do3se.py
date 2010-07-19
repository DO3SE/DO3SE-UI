#!/usr/bin/env python

import os.path
import logging
import sys
from optparse import OptionParser

import wx

from do3se.config import Config
from do3se.application import app_name
from do3se.dataset import Dataset
from do3se import model

config = None

class FakeApp(wx.App):
    """Fake application to trick wxPython into letting us use StandardPaths."""
    def OnInit(self):
        self.SetAppName('DO3SE')
        return True

def load_config():
    app = FakeApp()
    conf_path = os.path.join(wx.StandardPaths_Get().GetUserDataDir(), 'config.json')
    return Config(conf_path, 'resources/default_veg_presets.csv')

def list_presets(option, opt, value, parser):
    print "Input format presets:"
    for p in config['input_format'].iterkeys():
        print "\t" + p
    print "Site parameter presets:"
    for p in config['site_params'].iterkeys():
        print "\t" + p
    print "Vegetation parameter presets:"
    for p in config['veg_params'].iterkeys():
        print "\t" + p
    print "Output format presets:"
    for p in config['output_format'].iterkeys():
        print "\t" + p
    print "\t(Or any valid comma-separated variable list, see --list-outputs)"
    exit(0)

def list_outputs(option, opt, value, parsers):
    print "Available output variables: ([field] Description)"
    for f in model.output_fields:
        print "\t[%(variable)-11s] %(long)s" % f
    exit(0)


if __name__ == '__main__':
    # Setup logging
    level = logging.DEBUG
    logging.basicConfig(level=level, format='[%(levelname)-8s] %(message)s')

    # Load config
    global config
    config = load_config()

    # Arguments
    parser = OptionParser(usage="usage: %prog [options] INPUT_FORMAT SITE_PARAMS"
                                " VEG_PARAMS OUTPUT_FORMAT")
    parser.add_option('-l', '--list-presets', action="callback", callback=list_presets,
                      help="List the names of available presets")
    parser.add_option('--list-outputs', action="callback", callback=list_outputs,
                      help="List all available output fields")
    parser.add_option('-i', '--infile', dest="infile", metavar="FILE",
                      help="Input file (defaults to stdin)")
    parser.add_option('-o', '--outfile', dest="outfile", metavar="FILE",
                      help="Output file (defaults to stdout)")
    (options, args) = parser.parse_args()

    if len(args) < 4:
        parser.error("not enough arguments")
    if len(args) > 4:
        parser.error("too many arguments")

    if options.infile == None:
        infile = sys.stdin
    else:
        try:
            infile = open(options.infile)
        except IOError:
            parser.error("could not open input file: " + options.infile)

    if options.outfile == None:
        outfile = sys.stdout
    else:
        try:
            outfile = open(options.outfile, 'wb')
        except IOError:
            parser.error("could not open output file: " + options.outfile)

    (informat_preset, site_preset, veg_preset, outformat_preset) = args

    try:
        informat = config['input_format'][informat_preset]
    except KeyError:
        parser.error('invalid input format preset: %s (see --list-presets)' % informat_preset)

    try:
        siteparams = config['site_params'][site_preset]
    except KeyError:
        parser.error('invalid site parameter preset: %s (see --list-presets)' % site_preset)

    try:
        vegparams = config['veg_params'][veg_preset]
    except KeyError:
        parser.error('invalid vegetation parameter preset: %s (see --list-presets)' % veg_preset)

    try:
        outformat = config['output_format'][outformat_preset]
    except KeyError:
        outformat = {'fields': outformat_preset.split(','),
                     'reduce': False, 'headers': True}
    for f in outformat['fields']:
        if not f in model.output_field_map:
            parser.error('invalid field name: %s (see --list-outputs)' % f)

    d = Dataset(infile, informat['fields'], informat['trim'],
                siteparams, vegparams)

    d.run()

    d.save(outfile, outformat['fields'], outformat['headers'])
