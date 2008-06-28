################################################################################
# The main application handler
################################################################################

# Configuration file version
CFGVERSION = "0.5"

# Set up logging
import logging
import sys
try:
    if sys.frozen:
        # If we are running standalone, don't annoy the user with pointless debug
        # messages
        logging.basicConfig(
            level = logging.CRITICAL,
            format = '%(levelname)-8s %(message)s'
        )
    else:
        logging.basicConfig(
            level = logging.DEBUG,
            format = '%(levelname)-8s %(message)s'
        )
except AttributeError:
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(levelname)-8s %(message)s'
    )


# The application
import wx
import shelve
import os

import util
import dose

class Application(wx.App):
    def OnInit(self):
        self.SetAppName('DOSE')
        self.title = 'DOSE Model'

        # Single instance checker - only allow one instance of the program
        self.sichecker = wx.SingleInstanceChecker("%s-%s.lock" % 
                (self.GetAppName(), wx.GetUserId()))
        if self.sichecker.IsAnotherRunning():
            logging.error("Another instance is already running, exiting.")
            return False

        self._config_load()

        return True


    def _config_load(self):
        dirname = wx.StandardPaths_Get().GetUserDataDir()
        path = os.path.join(dirname, 'dose.cfg')
        logging.info("Using configuration file '%s'" % path)

        if not os.path.exists(dirname):
            os.mkdir(dirname)
            logging.debug("Created directory '%s'" % dirname)

        self.config = shelve.open(os.path.join(dirname, 'dose.cfg'))

        if (not 'version' in self.config) \
                or (util.versioncmp(CFGVERSION, self.config['version'])):
            self._config_upgrade()


    def _config_upgrade(self):
        if 'version' in self.config:
            logging.info('Creating configuration file (format version %s)' 
                    % CFGVERSION)
        else:
            logging.info("Upgrading configuration format (%s -> %s) ..." 
                    % (self.config['version'], CFGVERSION))

        # Blank configuration format
        new = {
                'filehistory':      list(),
                'preset.inputs':    dict(),
                'preset.outputs':   dict(),
                'preset.model':     dict(),
                'preset.site':      dict(),
                'preset.veg':       dict(),
        }

        blank = {
                'preset.site': {
                    'lat': float(getattr(dose.params_site, 'lat')),
                    'lon': float(getattr(dose.params_site, 'lon')),
                    'elev': float(getattr(dose.params_site, 'elev')),
                    'o3zr': float(getattr(dose.params_site, 'o3zr')),
                    'uzr': float(getattr(dose.params_site, 'uzr')),
                    'xzr': float(getattr(dose.params_site, 'xzr')),
                    'o3_h': float(getattr(dose.params_site, 'o3_h')),
                    'u_h': float(getattr(dose.params_site, 'u_h')),
                    'o3_h_copy': False,
                    'u_h_copy': False,
                    'rsoil': float(getattr(dose.params_site, 'rsoil')),
                    'soil_a': float(getattr(dose.params_site, 'soil_a')),
                    'soil_b': float(getattr(dose.params_site, 'soil_b')),
                    'soil_bd': float(getattr(dose.params_site, 'soil_bd')),
                    'fc_m': float(getattr(dose.params_site, 'fc_m')),
                },
                'preset.veg': {
                    'h': float(getattr(dose.params_veg, 'h')),
                    'root': float(getattr(dose.params_veg, 'root')),
                    'lai_min': float(getattr(dose.params_veg, 'lai_min')),
                    'lai_max': float(getattr(dose.params_veg, 'lai_max')),
                    'lm': float(getattr(dose.params_veg, 'lm')),
                    'albedo': float(getattr(dose.params_veg, 'albedo')),
                    'rext': float(getattr(dose.params_veg, 'rext')),
                    'sgs': float(getattr(dose.params_veg, 'sgs')),
                    'egs': float(getattr(dose.params_veg, 'egs')),
                    'astart': float(getattr(dose.params_veg, 'astart')),
                    'aend': float(getattr(dose.params_veg, 'aend')),
                    'ls': float(getattr(dose.params_veg, 'ls')),
                    'le': float(getattr(dose.params_veg, 'le')),
                    't_min': float(getattr(dose.params_veg, 't_min')),
                    't_opt': float(getattr(dose.params_veg, 't_opt')),
                    't_max': float(getattr(dose.params_veg, 't_max')),
                    'vpd_min': float(getattr(dose.params_veg, 'vpd_min')),
                    'vpd_max': float(getattr(dose.params_veg, 'vpd_max')),
                    'swp_min': float(getattr(dose.params_veg, 'swp_min')),
                    'swp_max': float(getattr(dose.params_veg, 'swp_max')),
                    'fphen_a': float(getattr(dose.params_veg, 'fphen_a')),
                    'fphen_b': float(getattr(dose.params_veg, 'fphen_b')),
                    'fphen_c': float(getattr(dose.params_veg, 'fphen_c')),
                    'fphen_d': float(getattr(dose.params_veg, 'fphen_d')),
                    'fphens': float(getattr(dose.params_veg, 'fphens')),
                    'fphene': float(getattr(dose.params_veg, 'fphene')),
                    'y': float(getattr(dose.params_veg, 'y')),
                    'f_lightfac': float(getattr(dose.params_veg, 'f_lightfac')),
                    'fmin': float(getattr(dose.params_veg, 'fmin')),
                    'gmax': float(getattr(dose.params_veg, 'gmax')),
                },
        }

        # Copy the recent file list
        logging.info("\tCopying filehistory")
        new['filehistory'] = list(self.config['filehistory'])

        # Simple conversions: default + update
        for cat in ('preset.site', 'preset.veg'):
            logging.info("\tCreating %s.%s" % (cat, 'Default'))
            new[cat]['Default'] = dict(blank[cat])
            for k, v in self.config[cat].iteritems():
                logging.info("\tUpdating %s.%s" % (cat, k))
                new[cat][k] = dict(blank[cat])
                new[cat][k].update(v)

        # Copy other presets
        for cat in ('preset.outputs', 'preset.inputs'):
            logging.info("\tCopying %s" % cat)
            new[cat].update(self.config[cat])

        # Set new version
        new['version'] = CFGVERSION

        # Make changes and save
        logging.info("\tSaving changes")
        #import pprint
        #pprint.pprint(dict(self.config))
        #pprint.pprint(new)
        self.config.update(new)


    def AddFileToHistory(self, path):
        """Add a path to recent file history

        Adds the path to the file history list, removing duplicates and making sure
        the list is only 9 items long and in chronological order.
        """
        d = self.config['filehistory']
        try:
            d.remove(path)
        except ValueError:
            pass
        d.append(path)
        d = d[-9:]
        self.config['filehistory'] = d


    def OnExit(self):
        """Clean up on exit

        Clean up configurating, SingleInstanceChecker, etc. on application exit
        """
        self.config.close()
        logging.debug("Configuration file closed")
        del self.sichecker


    def Run(self):
        import ui
        self.toplevel = ui.MainWindow()
        self.toplevel.Bind(wx.EVT_CLOSE, lambda evt: self.Exit())
        self.toplevel.Show()
        self.MainLoop()


    def Exit(self):
        # do some stuff
        wx.App.Exit(self)



app = Application(False)
