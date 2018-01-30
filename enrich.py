from pyne.material import Material, MaterialLibrary

path_to_compendium = "/home/alex/.local/lib/python2.7/\
site-packages/pyne/nuc_data.h5"


def get_nitrogen():
    """Load the Nitrogen composition from the PyNE material compendium.
    """

    # Initialize material libraries.
    raw_matlib = MaterialLibrary()
    _matlib = MaterialLibrary()

    # Write entire PyNE material library.
    raw_matlib.from_hdf5(path_to_compendium,
                         datapath="/material_library/materials",
                         nucpath="/material_library/nucid")

    return raw_matlib['Nitrogen'].expand_elements().to_atom_frac()


def make_fuel(enrich):
    """Create a PyNE fuel material object based on an input enrichment
    """

    Nitrogen = get_nitrogen()

    fuel_afrac = Material({'U238': 1-enrich, 'U235':enrich},-1.0).to_atom_frac()

    for isotope in Nitrogen:
        fuel_afrac.update({isotope:Nitrogen[isotope]})

    fuel_afrac.update({n: 0.5 * fuel_afrac[n] for n in fuel_afrac.keys()})

    fuel = Material()
    fuel.from_atom_frac(fuel_afrac)
    
    return fuel.mcnp()

if __name__ == '__main__':

    fuel = make_fuel(0.9999)
    print(fuel.mcnp(frac_type='atom'))
