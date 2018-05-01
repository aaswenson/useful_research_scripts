import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

import numpy as np
import pandas as pd
import argparse


axis_labels = {'core_r' : 'Core r [cm]',
               'power' : 'Power [kW]',
               'PD' : 'Pitch/Cool. D. [-]',
               'keff' : 'EOL keff [-]',
               'ave_E' : 'Average Energy EOL [MeV]',
               'enrich' : 'enrich [-]',
               'mass' : 'fuel mass [kg]'}

def filter_data(filters, data):

    """Apply useful filters on the data
    """
    opers = {'less' : operator.lt,
             'equal' : operator.eq,
             'great' : operator.gt}
    
    for op in filters:
        data = data[opers[op[1]](data[op[0]], op[2])]   
    
    return data


def plot_results(data, ind, dep, colorplot=None):
    """Generate 2d scatter Plots
    """
    # plot
    fig = plt.figure()
    if len(colorplot) > 0:
        plt.scatter(data[ind], data[dep], c=data[colorplot], s=6,
                cmap=plt.cm.get_cmap('plasma', len(set(colorplot))))
        plt.colorbar()
    else:
        plt.scatter(data[ind], data[dep], s=6)
    
    plt.show()

    return plt

def property_plot(data, params, colorplot=None):
        """ Create grid of plots for multi-dimensional visualization
        """
        dim = len(params)

        plots = []
        # generate plot grid
        for i in range(dim):
            row = []
            for j in range(dim):
                row.append((params[i], params[j]))
            plots.append(row)

        pass_idx = []
        # create list of "skippable" repeat plots
        for rowdx in range(dim):
            basedx = rowdx * dim 
            for i in range(rowdx):
                pass_idx.append(basedx + i)


        fig = plt.figure(figsize=(14, 10))
        for xidx, row in enumerate(plots):
            for yidx, plot in enumerate(row): 
                pass_id = dim*yidx + xidx
                if pass_id not in pass_idx:
                    ax = fig.add_subplot(dim, dim, pass_id+1)
                    xkey = plot[0] 
                    ykey = plot[1]
                    x = data[xkey]
                    y = data[ykey]
                    if colorplot:
                        ax.scatter(x, y, s=(3/dim), c=data[colorplot], cmap=plt.cm.get_cmap('plasma', len(set(data['keff']))))
                    else:
                        ax.scatter(x, y, s=(3/dim), cmap=plt.cm.get_cmap('plasma', len(set(data['keff']))))
                    if ykey == 'power':
                        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
                    if xkey == 'power':
                        ax.ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
                    if yidx == 0:
                        plt.title(axis_labels[xkey], fontsize=12)
                    if xidx == yidx:
                        plt.ylabel(axis_labels[ykey], fontsize=12)
        fig.savefig('property_matrix.png', dpi=700)
        
        return plt

def surf_plot(data, ind1, ind2, dep, colorplot=None):
    """3D surface plot
    """

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    X = data[ind1]
    Y = data[ind2]
    Z = data[dep]
    if colorplot:
        # Plot the surface.
        p = ax.scatter(X,Y,Z, c=data[colorplot], cmap=plt.cm.get_cmap('plasma',
            len(data[colorplot])))
        plt.colorbar(p, ax=ax, label=axis_labels[colorplot])
    else:
        ax.scatter(X, Y, Z, c=Z)

    # Customize the z axis.
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    
    ax.set_xlabel(axis_labels[ind1])
    ax.set_ylabel(axis_labels[ind2])
    ax.set_zlabel(axis_labels[dep])

    return plt

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--datafile', type=str, help="path to csv datafile",
                        default="data.csv")
    parser.add_argument('-i', action="store_true", default=False, help='display\
plot in interactive mode')

    args = parser.parse_args()
    data = pd.read_csv(args.datafile)

    plt = property_plot(data, ('core_r', 'mass', 'PD', 'enrich'), 'keff')
#   plt = surf_plot(data, 'core_r', 'PD', 'mass', 'keff')

    
    if args.i:
        plt.show()
