import tarfile

def get_XS_list():
    """Get the required XS's and the path to them.
    """
    XSs = []
    with open('needed_xs.txt', 'r') as fp:
        for line in fp:
            XSs.append(line.split()[0])
    fp.close()

    return XSs

def read_old_write_new(XSs, mcnp_datapath, tar_name, xsdirname):
    """Write new xsdir from list of necessary XS's. Tar the data and the mcnp6
    executable.
    """
    new_xsdir = open(xsdirname, 'w')
    directory = False
    # setup data tarball
    tar_name += ".tar.gz"
    tar_data = tarfile.open(tar_name, "w|gz")
    with open(mcnp_datapath + 'xsdir', 'r') as old_fp:
        for line in old_fp:
            if 'directory' in line:
                directory = True
                new_xsdir.write(line)
            if (directory == True and line.split()[0] in XSs):
                print(line.split()[0])
                # the good stuff we want to save
                new_xsdir.write(line)
                # add datafile to tarball
                name = mcnp_datapath + line.split()[2]
                tar_data.add(name, arcname=line.split()[2])
                # add weird ptables entry
                if " +" in line:
                    new_xsdir.write("          ptable\n")
            if directory == False:
                new_xsdir.write(line)
    new_xsdir.close()
    old_fp.close()
    tar_data.add(xsdirname)    
    # add the executables
    tar_data.add("/mnt/sdb/MCNP/MCNP_CODE/bin/mcnp6", arcname="mcnp6")
    # add the cinder depletion data
    tar_data.add(mcnp_datapath + "xdata/cinder.dat", arcname="cinder.dat")
    tar_data.close()


test = get_XS_list()
read_old_write_new(test, "/mnt/sdb/MCNP/MCNP_DATA/", "test", "testxsdir")
