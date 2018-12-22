# =========================
# Available plot parameters
# =========================
# 
# tally_id : int
#     tally ID
# slice : string
#     'x' to plot through the x-direction
#     'y' to plot through the x-direction
#     'z' to plot through the x-direction
# loc : float
#     location through which to slice
# eind : int
#     energy bin index (0 is first, 1 is second, ..., -1 is last)
# data : string
#     'result' for the result
#     'relerr' for the relative error
# distance_units: string
#     allowed values: 'mm', 'cm', 'in', 'ft', 'yd', 'm'
# vmin : float
#     minimum value on the colorbar
# vmax : float
#     maximum value on the colorbar
# logscale : bool
#     plot data in log scale
# draw_geom_func : function
#     function to draw geometry on the plot
# title : string
#     plot title
# colorbar_label : string
#     colorbar label
# colorbar_orient : string
#     'horizontal' or 'vertical'
# contour_colors : vector
#     contour line colors
# contour_levels : vector
#     contour line levels
# contour_labels : string or vector
#     'decimal' for decimal labels
#     'percent' for percent labels
#     'powers_ten' for powers of ten
#     vector for custom labels
# filename : string
#     plot filename
#
# =====================================
# Available geometry plotting functions
# =====================================
# 
# draw_line(x0, x1, y0, y1)
# draw_hriz_line(y, x0, x1)
# draw_vert_line(x, y0, y1)
# draw_rectangle(x0, x1, y0, y1)
# draw_circle(x, y, r)
# draw_arc(x, y, r, t0, t1)

from meshtal import *
import glob

def make_plots():
    
    # Specify meshtal filenames
    files = glob.glob('./*msht')
    

    # Loop over all filenames
    for fname in files:
        print(fname)

        # Read meshtal from file
        tallies = read_meshtal(fname, validate=True)
        
        # Create the dictionary that will hold the plot parameters
        p = {}

        
        # Set appropriate parameters
        p['slice']           = 'z'                                                              # Slice through the x-direction
        p['loc']             =  0.5                                                               # Location through which to slice
        p['data']            = 'result'                                                         # Plot the result, as opposed to the relative error
        p['distance_units']  = 'cm'                                                              # Convert distance units to meters
        p['vmin']            = 1e4                                                              # Minimum value on the colorbar
        p['vmax']            = 1e9                                                             # Maximum value on the colorbar
        p['logscale']        = True                                                             # Plot data in log scale
#        p['draw_geom_func']  = data['bbox']    # Function to draw geometry on the plot
        p['title']           = 'Tally: {0}'.format(504)
        p['colorbar_label']  = 'Photon Dose Rate [mrem/hr]'                   # Fancy colorbar label
        p['colorbar_orient'] = 'horizontal'                                                     # Colorbar orientation
        p['contour_colors']  = ['w', 'orange', 'r', 'g']  # Contour line colors
        p['contour_levels']  = [1e4, 1e6, 1e8, 1e9]             # Contour line levels
        p['contour_labels']  = 'powers_ten'                                                      # Contour line label type
        p['filename']        = 'test.png' # Plot filename

        # Plot meshtal
        tallies[504].plot(p)
        

def draw_geom_x_target(tally):
    draw_rectangle(0, 1.987, -5.715, 5.715)
    draw_rectangle(-15.90725, -0.636, -5.08, 5.08)

def draw_geom_x_be_plug(tally):
    draw_rectangle(2.0605, 15.078, -6.0388, 6.0388)

def draw_geom_x_c_plug(tally):
    draw_rectangle(14.8605, 33.02, -6.03885, 6.03885)

if __name__ == '__main__': make_plots()
