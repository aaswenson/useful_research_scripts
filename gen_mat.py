"""Script to generate mcnp-style composition from the PNNL material compendium
using PyNE.

Following function is included in this script.
  * build_pyne_matlib
  * print_mcnp_mat
"""
import sys
import os

# Import PyNE packages.
from pyne.material import MaterialLibrary

# Import argparse for command-line argument.
import argparse

# Add scripts to path for reactor_data import
sys.path.append('../python_script/')

def build_pyne_matlib(nucdata_file, material):
    """Fetch pyne material from compendium.

    This function builds PyNE material library
    for UWNR non-fuel components defined in reactor_data.py

    Arguments:
        nucdata_file (str)[-]: Filename 'nuc_data.h5' with its full path.
        material (str)[-]: material name
    """

    # Initialize material libraries.
    raw_matlib = MaterialLibrary()
    _matlib = MaterialLibrary()

    # Write entire PyNE material library.
    raw_matlib.from_hdf5(nucdata_file,
                         datapath="/material_library/materials",
                         nucpath="/material_library/nucid")

    # Write Desire material to json.
    pyne_obj = raw_matlib[material].expand_elements()
    _matlib[material] = pyne_obj

    _matlib.write_json('mat.json')

def print_mcnp_mat(mat, atom):
    """ Print the material in mcnp form.
    
        This function loads the material from the PyNE material library and
        prints the mcnp version to the screen.

    Arguments:
        mat (str)[-]: material identifier
        atom (bool)[-]: atom frac 
    """
    # set default frac to mass
    frac = 'mass'
    # if desired change to atom frac
    if atom == True:
        frac = 'atom'
    # access the material
    matlib = MaterialLibrary()
    matlib.from_json('./mat.json')
    # generate the expanded-elements, mcnp-form mat string
    matstring = matlib[mat].expand_elements().mcnp(frac_type=frac)
    # print the string
    print(matstring)


if __name__=="__main__":
    # from command-line argument.
    parser = argparse.ArgumentParser(description=
            "Generate HDF5 file containing material library for the model.")
    parser.add_argument("mat", type=str, help="desired mat")
    parser.add_argument("-a", "--atomic", action="store_true",
                        help="Produce atom fraction")
    # (optional)
    # Set the full path to `nuc_data.h5` with the filename included
    parser.add_argument("-filename", type=str,
                        default="/home/alex/.local/lib/python2.7/\
site-packages/pyne/nuc_data.h5", help="filename nuc_data.h5 with its full path")
    args = parser.parse_args()

    # Generate model-specific HDF5 file.
    build_pyne_matlib(args.filename, args.mat)
    # print material to screen
    print_mcnp_mat(args.mat, args.atomic)
    # remove the file
    os.remove('./mat.json')
