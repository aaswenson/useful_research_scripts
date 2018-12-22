import copy
import os
import sys
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.colors as colors
import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import patches
from cycler import cycler

if sys.version_info[0] != 2: raise Exception('Must be using Python 2')

# Tally object
class MeshTally():
    def __init__(self):
        self.name = 'default'      # filename
        self.tally_id = 0          # tally ID (104 for fmesh104)
        self.particle = 'unknown'  # particle type ('neutron', 'proton', etc.)
        self.geom = 'unknown'      # geometry type ('rec' or 'cyl')
        self.out_fmt = 'none'      # file format ('default', 'ij', 'ik', 'jk')
        self.ibins = []            # x-direction bins
        self.jbins = []            # y-direction bins
        self.kbins = []            # z-direction bins
        self.ebins = []            # energy bins
        self.num_ibins = 0         # number of x-direction bins
        self.num_jbins = 0         # number of y-direction bins
        self.num_kbins = 0         # number of z-direction bins
        self.num_ebins = 0         # number of energy bins
        self.origin = [None] * 3   # origin (cyl only)
        self.axs = [None] * 3      # axis (cyl only)
        self.vec = [None] * 3      # vec (cyl only)
        self.result = None         # result values
        self.relerr = None         # relative error values

    # Tally addition operator
    def __add__(self, other):
        self.check_equal_dims(other)
        tally_new = copy.deepcopy(self)
        if self.particle != other.particle: tally_new.particle = 'combined'
        tally_new.result = self.result + other.result
        tally_new.relerr = (np.sqrt((self.result * self.relerr)**2 +
                                   (other.result * other.relerr)**2) /
                            tally_new.result)
        return tally_new

    # Tally subtraction operator
    def __subtract__(self, other):
        self.check_equal_dims(other)
        tally_new = copy.deepcopy(self)
        if self.particle != other.particle: tally_new.particle = 'combined'
        tally_new.result = self.result - other.result
        tally_new.relerr = (np.sqrt((self.result * self.relerr)**2 +
                                   (other.result * other.relerr)**2) /
                            tally_new.result)
        return tally_new

    # Check to make sure two tallies have the same dimensions
    def check_equal_dims(self, other):
        if (self.num_ibins != other.num_ibins or
            self.num_jbins != other.num_jbins or
            self.num_kbins != other.num_kbins or
            self.num_ebins != other.num_ebins):
            raise Exception('dimension mismatch; cannot combine tallies')

    # Allocate an array for a tally of known size
    def allocate(self):
        self.result = np.zeros((self.num_ibins, self.num_jbins,
                                self.num_kbins, self.num_ebins))
        self.relerr = np.zeros((self.num_ibins, self.num_jbins,
                                self.num_kbins, self.num_ebins))

    # Print out some statistics about a tally
    def validate(self):
        num_zero = (self.result == 0).sum()
        print ((' %4u %4s %7s %8s %24s %10.4e'
                ' %10.4e %10.4e %10.4e %10.4e %10.4e %8u %8u') %
               (self.tally_id, self.geom, self.out_fmt, self.particle,
                str(self.result.shape),
                np.min(self.result), np.max(self.result), np.mean(self.result),
                np.min(self.relerr), np.max(self.relerr), np.mean(self.relerr),
                self.result.size, num_zero))

    # Plot the mesh tally
    def plot(self, params_input):
        '''
        Required parameters
        ===================
        params_input : dictionary
            tally_id : int
                tally ID
            slice : string
                'x' to plot through the x-direction
                'y' to plot through the x-direction
                'z' to plot through the x-direction
            loc : float
                location through which to slice
            eind : int
                energy bin index (0 is first, 1 is second, ..., -1 is last)
            data : string
                'result' for the result
                'relerr' for the relative error
            distance_units: string
                allowed values: 'mm', 'cm', 'in', 'ft', 'yd', 'm'
            vmin : float
                minimum value on the colorbar
            vmax : float
                maximum value on the colorbar
            logscale : bool
                plot data in log scale
            draw_geom_func : function
                function to draw geometry on the plot
            title : string
                plot title
            colorbar_label : string
                colorbar label
            colorbar_orient : string
                'horizontal' or 'vertical'
            contour_colors : vector
                contour line colors
            contour_levels : vector
                contour line levels
            contour_labels : string or vector
                'decimal' for decimal labels
                'percent' for percent labels
                'powers_ten' for powers of ten
                vector for custom labels
            filename : string
                plot filename
        '''

        # Set some default plotting parameters
        line_color = 'k'
        line_width = 1
        plt.rcParams['image.cmap']          = 'Spectral_r'
        plt.rcParams['image.interpolation'] = 'bilinear'

        plt.rcParams['axes.prop_cycle'] = cycler('color', [line_color])
        plt.rcParams['patch.edgecolor'] = line_color
        plt.rcParams['lines.linewidth'] = line_width
        plt.rcParams['patch.linewidth'] = line_width

        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['text.usetex'] = True

        # Copy input params
        params = params_input.copy()

        # Set default params
        params_default = {}
        params_default['tally_id']        = 0
        params_default['slice']           = 'z'
        params_default['loc']             = 0.
        params_default['eind']            = -1
        params_default['data']            = 'result'
        params_default['distance_units']  = 'cm'
        params_default['vmin']            = None
        params_default['vmax']            = None
        params_default['logscale']        = True
        params_default['draw_geom_func']  = None
        params_default['title']           = ''
        params_default['colorbar_label']  = ''
        params_default['colorbar_orient'] = 'vertical'
        params_default['contour_colors']  = []
        params_default['contour_levels']  = []
        params_default['contour_labels']  = 'decimal'
        for param in params_default:
            if param not in params:
                params[param] = params_default[param]
        if 'filename' not in params:
            params['filename'] = ('%s_%s_%.1f_%u_%s.png' %
                                  (self.name, params['slice'], params['loc'],
                                   params['eind'], params['data']))

        # Make sure parameters are valid
        #params['tally_id'] = int(params['tally_id'])
        assert(params['slice'] in 'xyz')
        params['loc'] = float(params['loc'])
        params['eind'] = int(params['eind'])
        assert(params['data'] in ['result', 'relerr'])
        assert(params['distance_units'] in ['mm', 'cm', 'in', 'ft', 'yd', 'm'])
        if params['vmin'] != None: params['vmin'] = float(params['vmin'])
        if params['vmax'] != None: params['vmax'] = float(params['vmax'])
        assert(params['logscale'] in [True, False])
        if params['draw_geom_func'] != None:
            assert(callable(params['draw_geom_func']) == True)
        params['title'] = str(params['title'])
        params['colorbar_label'] = str(params['colorbar_label'])
        assert(params['colorbar_orient'] in ['vertical', 'horizontal'])
        assert(type(params['contour_colors']) is list)
        assert(type(params['contour_levels']) is list)
        assert(len(params['contour_levels']) == len(params['contour_colors']))
        assert((params['contour_labels'] in
                ['decimal', 'percent', 'powers_ten']) or
               (type(params['contour_labels']) is list))
        if type(params['contour_labels']) is list:
            assert(len(params['contour_labels']) ==
                   len(params['contour_colors']))
        params['filename'] = str(params['filename'])

        # If energy bin index is negative, set it to the absolute index
        if params['eind'] < 0:
            params['eind'] = self.result.shape[3] + params['eind']

        # Dimensions to display on the chart
        if self.geom == 'rec':
            if params['slice'] == 'x':
                bins_main  = self.ibins
                bins_horiz = self.jbins
                bins_vert  = self.kbins
                horiz = 'y'
                vert  = 'z'
            elif params['slice'] == 'y':
                bins_main  = self.jbins
                bins_horiz = self.ibins
                bins_vert  = self.kbins
                horiz = 'x'
                vert  = 'z'
            elif params['slice'] == 'z':
                bins_main  = self.kbins
                bins_horiz = self.ibins
                bins_vert  = self.jbins
                horiz = 'x'
                vert  = 'y'
            num_bins_main  = len(bins_main) - 1
            num_bins_horiz = len(bins_horiz) - 1
            num_bins_vert  = len(bins_vert) - 1
            extent = [bins_horiz[0], bins_horiz[-1],
                      bins_vert[0], bins_vert[-1]]
        elif self.geom == 'cyl':
            bins_horiz = self.jbins
            bins_vert = [-i for i in reversed(self.ibins[1:])] + self.ibins
            if self.axs[0] == 1.:
                bins_horiz = [i + self.origin[0] for i in bins_horiz]
                bins_vert = [i + self.origin[1] for i in bins_vert]
                horiz = 'x'
                vert = 'y'
                slice_new = 'z'
                loc_new = self.origin[2]
            elif self.axs[1] == 1.:
                bins_horiz = [i + self.origin[1] for i in bins_horiz]
                bins_vert = [i + self.origin[2] for i in bins_vert]
                horiz = 'y'
                vert = 'z'
                slice_new = 'x'
                loc_new = self.origin[0]
            elif self.axs[2] == 1.:
                bins_horiz = [i + self.origin[2] for i in bins_horiz]
                bins_vert = [i + self.origin[0] for i in bins_vert]
                horiz = 'z'
                vert = 'x'
                slice_new = 'y'
                loc_new = self.origin[1]
            else:
                raise Exception('axis of cylindrical mesh must be parallel to '
                                'the x, y, or z axes')
            if params['slice'] != slice_new or params['loc'] != loc_new:
                params['slice'] = slice_new
                params['loc'] = loc_new
                print ('Note: slice plane for cylindrical mesh set to ' +
                       '%s = %.f' % (params['slice'], params['loc']))
            num_bins_horiz = len(bins_horiz) - 1
            num_bins_vert  = len(bins_vert) - 1
            extent = [bins_horiz[0], bins_horiz[-1],
                      bins_vert[0], bins_vert[-1]]

        # Convert the distances to the correct units
        distance_divisors = {'mm':  0.1 , 'cm':  1.  , 'in':   2.54,
                             'ft': 30.48, 'yd': 91.44, 'm' : 100.  }
        global distance_divisor
        distance_divisor = distance_divisors[params['distance_units']]
        extent = [v / distance_divisor for v in extent]

        # Get tally slice index
        if self.geom == 'rec':
            if params['loc'] < bins_main[0] or params['loc'] > bins_main[-1]:
                raise Exception('tally slice location out of range')
            for ind in range(num_bins_main + 1):
                if params['loc'] == bins_main[ind]:
                    raise Exception('tally slice on boundary')
                if params['loc'] < bins_main[ind]:
                    break
            ind -= 1
        elif self.geom == 'cyl':
            pass

        # Get array data to be plotted
        if self.geom == 'rec':
            if params['data'] == 'result':
                if params['slice'] == 'x':
                    result = np.rot90(self.result[ind, :, :, params['eind']])
                elif params['slice'] == 'y':
                    result = np.rot90(self.result[:, ind, :, params['eind']])
                elif params['slice'] == 'z':
                    result = np.rot90(self.result[:, :, ind, params['eind']])
            elif params['data'] == 'relerr':
                if params['slice'] == 'x':
                    result = np.rot90(self.relerr[ind, :, :, params['eind']])
                elif params['slice'] == 'y':
                    result = np.rot90(self.relerr[:, ind, :, params['eind']])
                elif params['slice'] == 'z':
                    result = np.rot90(self.relerr[:, :, ind, params['eind']])
        elif self.geom == 'cyl':
            if params['data'] == 'result':
                result = np.concatenate((
                    np.flipud(self.result[:, :, 0, params['eind']]),
                    self.result[:, :, 0, params['eind']]), axis=0)
            elif params['data'] == 'relerr':
                result = np.concatenate((
                    np.flipud(self.relerr[:, :, 0, params['eind']]),
                    self.relerr[:, :, 0, params['eind']]), axis=0)

        # Turn off logscale if the entire result is zero
        if params['logscale'] and np.count_nonzero(result) == 0:
            params['logscale'] = False
            print('Note: entire plot is zero; logscale turned off')

        # Colorbar bounds
        # If not specified and using a linear scale, use the min/max value
        # If not specified and using a log scale, use the min/max nonzero value
        if params['vmin'] == None:
            if params['logscale']: params['vmin'] = np.min(result[result != 0.])
            else: params['vmin'] = np.min(result)
        if params['vmax'] == None:
            if params['logscale']: params['vmax'] = np.max(result[result != 0.])
            else: params['vmax'] = np.max(result)
        if params['logscale']:
            if params['vmin'] == 0.:
                params['vmin'] = np.min(result[result != 0.])
                print ('Note: vmin cannot be zero while using logscale; ' +
                       'using %.f instead' % (params['vmin']))
            if params['vmax'] == 0.:
                params['vmax'] = np.max(result[result != 0.])
                print ('Note: vmax cannot be zero while using logscale; ' +
                       'using %.f instead' % (params['vmax']))
        if params['logscale']:
            norm = colors.LogNorm(vmin=params['vmin'], vmax=params['vmax'])
        else:
            norm = colors.Normalize(vmin=params['vmin'], vmax=params['vmax'])

        # Replace 0% error with 100% error
        if params['data'] == 'relerr': result[result == 0.] = 1.

        # Replace zero values with tiny nonzero value to remove white areas
        if params['data'] == 'result':
            if params['logscale']: result[result == 0.] = 1e-100

        # Draw the plot
        plt.imshow(result, extent=extent, norm=norm)

        # Colorbar
        cbar = plt.colorbar(orientation=params['colorbar_orient'])
        if params['colorbar_label'] != '':
            cbar.set_label(params['colorbar_label'])

        # Labels
        if params['title'] != '': plt.title(params['title'])
        plt.xlabel('%s location [%s]' % (horiz, params['distance_units']))
        plt.ylabel('%s location [%s]' % (vert, params['distance_units']))

        # Draw geometry on the plot
        if params['draw_geom_func'] != None: params['draw_geom_func'](self)

        # Draw contour lines
        if params['contour_levels'] != []:
            if params['contour_labels'] == 'decimal':
                fmt = {}
                for i, level in enumerate(params['contour_levels']):
                    if int(level) == level: fmt[level] = '%u' % (level)
                    else: fmt[level] = '%s' % (str(level))
            elif params['contour_labels'] == 'percent':
                fmt = {}
                for i, level in enumerate(params['contour_levels']):
                    percent = level * 100
                    if int(percent) == percent:
                        fmt[level] = '%u' % (percent) + '\%'
                    else:
                        fmt[level] = '%s' % (str(percent)) + '\%'
            elif params['contour_labels'] == 'powers_ten':
                fmt = ticker.LogFormatterMathtext()
                fmt.create_dummy_axis()
            else:
                fmt = {}
                for i, level in enumerate(params['contour_levels']):
                    fmt[level] = '%s' % (params['contour_labels'][i])
            CS = plt.contour(result[::-1], params['contour_levels'],
                             extent=extent, colors=params['contour_colors'])
            plt.clabel(CS, params['contour_levels'], inline=1,
                       fmt=fmt, fontsize=10)
            cax = cbar.ax
            if params['logscale']:
                cbar_lines = [(np.log10(level) - np.log10(params['vmin'])) /
                              (np.log10(params['vmax']) -
                               np.log10(params['vmin']))
                              for level in params['contour_levels']]
            else:
                cbar_lines = [(level - params['vmin']) /
                              (params['vmax'] - params['vmin'])
                              for level in params['contour_levels']]
            for i, cbar_line in enumerate(cbar_lines):
                if params['colorbar_orient'] == 'vertical':
                    cax.hlines(cbar_line, 0, 1,
                               colors=params['contour_colors'][i])
                else:
                    cax.vlines(cbar_line, 0, 1,
                               colors=params['contour_colors'][i])

        # Save to file
        print('Writing plot %s' % (params['filename']))
        plt.savefig(params['filename'], dpi=150, bbox_inches='tight')
        plt.close()

# Read a meshtal file
def read_meshtal(fname, tally_ids=[], validate=False):
    print('Reading file "%s", tally IDs:' % (fname))

    # Tally name
    if fname.endswith('.imsht'): name = fname[:-6]
    else: name = fname

    reader = open(fname, 'r')
    line = reader.readline()

    tallies = {}        # Dictionary of tally objects indexed by their tally IDs
    num_skip_lines = 4  # Number of lines to skip
    off = 0             # 0 if neutron tally and only 1 energy bin; 1 otherwise

    # Loop over all the lines in the file
    while line:
        tokens = line.split()

        # Skip this line
        if num_skip_lines > 0:
            num_skip_lines -= 1

        # Blank line
        elif not tokens:
            pass

        # New mesh tally
        elif 'Mesh Tally Number' in line:
            tid = int(tokens[3])
            if len(tally_ids) == 0 or tid in tally_ids:
                print('%u' % (tid))
                tally = MeshTally()
                tally.name = name
                tally.tally_id = tid
                tally.out_fmt = 'none'
                tallies[tid] = tally

        # Don't do anything if currently reading unneeded tally
        elif len(tally_ids) != 0 and tid not in tally_ids:
            pass

        # Particle type
        elif 'mesh tally.' in line:
            tally.particle = tokens[-3]

        # Cylindrical mesh origin, axs, vec
        elif ('origin at' in line and
              'axis in' in line and
              'VEC direction' in line):
            tally.origin = [float(i) for i in tokens[2:5]]
            tally.axs = [float(i) for i in tokens[7:10]]
            tally.vec = [float(i) for i in tokens[13:16]]

        # Rectangular geometry
        elif 'X direction:' in line:
            tally.geom = 'rec'
            tally.ibins = [float(i) for i in tokens[2:]]
            tally.ibins = [i for i in tally.ibins]
            tally.num_ibins = len(tally.ibins) - 1
        elif 'Y direction:' in line:
            tally.jbins = [float(j) for j in tokens[2:]]
            tally.jbins = [j for j in tally.jbins]
            tally.num_jbins = len(tally.jbins) - 1
        elif tally.geom == 'rec' and 'Z direction:' in line:
            tally.kbins = [float(k) for k in tokens[2:]]
            tally.kbins = [k for k in tally.kbins]
            tally.num_kbins = len(tally.kbins) - 1

        # Cylindrical geometry
        elif 'R direction:' in line:
            tally.geom = 'cyl'
            tally.ibins = [float(i) for i in tokens[2:]]
            tally.ibins = [i for i in tally.ibins]
            tally.num_ibins = len(tally.ibins) - 1
        elif tally.geom == 'cyl' and 'Z direction:' in line:
            tally.jbins = [float(j) for j in tokens[2:]]
            tally.jbins = [j for j in tally.jbins]
            tally.num_jbins = len(tally.jbins) - 1
        elif 'Theta direction' in line:
            tally.kbins = [float(k) for k in tokens[3:]]
            tally.num_kbins = len(tally.kbins) - 1

        # Energy bins
        elif 'Energy bin boundaries:' in line:
            tally.ebins = [float(e) for e in tokens[3:]]
            if len(tally.ebins) == 2: tally.num_ebins = 1
            else: tally.num_ebins = len(tally.ebins)  # Includes total bin
            # If neutron tally and only 1 energy bin, energy bin is not shown
            if tally.particle == 'neutron' and tally.num_ebins == 1: off = 0
            else: off = 1

        # Default output format
        elif (tally.out_fmt == 'none' and
              ((tokens[off] == 'X' and tokens[1 + off] == 'Y' and
                tokens[2 + off] == 'Z') or
               (tokens[off] == 'R' and tokens[1 + off] == 'Z' and
                tokens[2 + off] == 'Th'))):
            tally.out_fmt = 'default'
            i = 0; j = 0; k = 0; e = 0
            tally.allocate()

        # Non-default output format
        elif tally.out_fmt == 'none' and 'Tally Results:' in line:
            section = 'result'
            tally.out_fmt = ''
            for n in [2, 5]:
                if tally.geom == 'rec':
                    if   tokens[n] == 'X': tally.out_fmt += 'i'
                    elif tokens[n] == 'Y': tally.out_fmt += 'j'
                    elif tokens[n] == 'Z': tally.out_fmt += 'k'
                elif tally.geom == 'cyl':
                    if   tokens[n] == 'R':     tally.out_fmt += 'i'
                    elif tokens[n] == 'Z':     tally.out_fmt += 'j'
                    elif tokens[n] == 'Theta': tally.out_fmt += 'k'
            across = tally.out_fmt[0]
            down = tally.out_fmt[1]
            if 'i' not in tally.out_fmt: next = 'i'
            if 'j' not in tally.out_fmt: next = 'j'
            if 'k' not in tally.out_fmt: next = 'k'
            i = 0; j = 0; k = 0; e = 0
            tally.allocate()
            num_skip_lines = 1

        # Non-default output format: in relative error
        elif len(tally.out_fmt) == 2 and 'Relative Errors' in line:
            section = 'relerr'
            if   next == 'i': j = 0; k = 0
            elif next == 'j': i = 0; k = 0
            elif next == 'k': i = 0; j = 0
            num_skip_lines = 1

        # Non-default output format: in result, new energy bin, reset indices
        elif (len(tally.out_fmt) == 2 and
              ('Energy Bin:' in line or 'Total Energy Bin' in line)):
            section = 'result'
            i = 0; j = 0; k = 0; e += 1
            num_skip_lines = 5

        # Non-default output format: new location bin
        elif (len(tally.out_fmt) == 2 and
              ((tokens[0] in ['X', 'Y', 'Z', 'R'] and tokens[1] == 'bin:') or
               (tokens[0] == 'Theta' and tokens[1] == 'bin'))):
            section = 'result'
            if   next == 'i': i += 1; j = 0; k = 0
            elif next == 'j': i = 0; j += 1; k = 0
            elif next == 'k': i = 0; j = 0; k += 1
            num_skip_lines = 3

        # Default output format: load data into array
        elif tally.out_fmt == 'default':
            tally.result[i, j, k, e] = float(tokens[3 + off])
            tally.relerr[i, j, k, e] = float(tokens[4 + off])
            if k == tally.num_kbins - 1:
                k = 0
                if j == tally.num_jbins - 1:
                    j = 0
                    if i == tally.num_ibins - 1:
                        i = 0
                        if e == tally.num_ebins - 1:
                            e = 0
                        else: e += 1
                    else: i += 1
                else: j += 1
            else: k += 1

        # Non-default output_format: load data into array
        elif len(tally.out_fmt) == 2:
            vals = [float(val) for val in tokens[1:]]
            if section == 'result':
                if   across == 'i': tally.result[:, j, k, e] = vals
                elif across == 'j': tally.result[i, :, k, e] = vals
                elif across == 'k': tally.result[i, j, :, e] = vals
            elif section == 'relerr':
                if   across == 'i': tally.relerr[:, j, k, e] = vals
                elif across == 'j': tally.relerr[i, :, k, e] = vals
                elif across == 'k': tally.relerr[i, j, :, e] = vals
            if   down == 'i': i += 1
            elif down == 'j': j += 1
            elif down == 'k': k += 1

        # Read new line
        line = reader.readline()

    print
    reader.close()

    # Print some statistics if requested
    if validate:
        print (' %4s %4s %7s %8s %24s %10s %10s %10s %10s %10s %10s %8s %8s' %
               ('ID', 'Geom', 'OutFmt', 'Particle', 'Shape',
                'Min', 'Max', 'Mean', 'Min_err', 'Max_err', 'Mean_err',
                'Elements', 'Num_zero'))
        for tid in sorted(tallies): tallies[tid].validate()

    # Return the dictionary of tally objects
    return tallies

# Draw a line from (x0, y0) to (x1, y1)
def draw_line(x0, x1, y0, y1, angle=0, xrot=0, yrot=0):
    x0_plot   = float(x0  ) / distance_divisor
    x1_plot   = float(x1  ) / distance_divisor
    y0_plot   = float(y0  ) / distance_divisor
    y1_plot   = float(y1  ) / distance_divisor
    xrot_plot = float(xrot) / distance_divisor
    yrot_plot = float(yrot) / distance_divisor
    if angle == 0:
        plt.plot([x0_plot, x1_plot], [y0_plot, y1_plot])
    else:
        sin_theta = np.sin(-angle * np.pi / 180)
        cos_theta = np.cos(-angle * np.pi / 180)
        x0_off = x0_plot - xrot_plot
        x1_off = x1_plot - xrot_plot
        y0_off = y0_plot - yrot_plot
        y1_off = y1_plot - yrot_plot
        x0_new = (x0_off * cos_theta - y0_off * sin_theta) + xrot_plot
        x1_new = (x1_off * cos_theta - y1_off * sin_theta) + xrot_plot
        y0_new = (x0_off * sin_theta + y0_off * cos_theta) + yrot_plot
        y1_new = (x1_off * sin_theta + y1_off * cos_theta) + yrot_plot
        plt.plot([x0_new, x1_new], [y0_new, y1_new])

# Draw a horizontal line from (x0, y) to (x1, y)
def draw_hriz_line(y, x0, x1, angle=0, xrot=0, yrot=0):
    draw_line(x0, x1, y, y, angle, xrot, yrot)

# Draw a vertical line from (x, y0) to (x, y1)
def draw_vert_line(x, y0, y1, angle=0, xrot=0, yrot=0):
    draw_line(x, x, y0, y1, angle, xrot, yrot)

# Draw a rectangle with opposite corners at (x0, y0) and (x1, y1)
def draw_rectangle(x0, x1, y0, y1, angle=0, xrot=0, yrot=0):
    draw_hriz_line(y0, x0, x1, angle, xrot, yrot)
    draw_hriz_line(y1, x0, x1, angle, xrot, yrot)
    draw_vert_line(x0, y0, y1, angle, xrot, yrot)
    draw_vert_line(x1, y0, y1, angle, xrot, yrot)

# Draw a circle with a center at (x, y) and a radius of r
def draw_circle(x, y, r):
    x_plot = float(x) / distance_divisor
    y_plot = float(y) / distance_divisor
    r_plot = float(r) / distance_divisor
    circ = pylab.Circle((x_plot, y_plot), radius=r_plot, fill=False)
    pylab.gca().add_patch(circ)

# Draw an arc with a center at (x, y) and a radius of r and an angular span in
# degrees from t0 to t1
def draw_arc(x, y, r, t0, t1):
    x_plot = float(x) / distance_divisor
    y_plot = float(y) / distance_divisor
    r_plot = float(r) / distance_divisor
    if t0 < 0 and t1 > 0:
        arc = patches.Arc((x_plot, y_plot), 2*r_plot, 2*r_plot, angle=0,
                          theta1=0, theta2=t1, fill=False)
        pylab.gca().add_patch(arc)
        arc = patches.Arc((x_plot, y_plot), 2*r_plot, 2*r_plot, angle=0,
                          theta1=t0 + 360, theta2=360, fill=False)
        pylab.gca().add_patch(arc)
    else:
        arc = patches.Arc((x_plot, y_plot), 2*r_plot, 2*r_plot, angle=0,
                          theta1=t0, theta2=t1, fill=False)
        pylab.gca().add_patch(arc)
