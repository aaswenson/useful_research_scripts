import matplotlib.pyplot as plt

def get_lines(filename='outp'):
    
    fp = open(filename, 'r')
    lines = fp.readlines()

    return lines

def parse_keff(lines):

    
    keff = []
    err = []

    for line in lines:
        if 'final result' in line:
            data = line.split()
            keff.append(float(data[2]))
            err.append(float(data[3]))

    res_k = keff[::2]   # skip predictor calc 
    res_err = err[::2]

    return res_k, res_err

def parse_table_210(lines):

    ptable_210_offset = 8
    
    time = []
    BU = []

    for idx, line in enumerate(lines):
        if 'print table 210' in line:  
            idx += ptable_210_offset
            break

    for line in lines[idx:]:
        if line == '\n':
            break
        time.append(float(line.split()[2]))
        BU.append(float(line.split()[8]))

    return time, BU

def plot_results(keff, rel_err, ind_vars):


    fig, axes = plt.subplots() # Size of 12 inches X 8 inches.
    axes.set_title("Homogeneous Depletion (300 K)")
    axes.set_xlabel("Time [days]", fontsize=12)
    axes.set_ylabel("keff [-]", fontsize=12)

    keff_list=[]
    for idx, keff in enumerate(keff):
        err = rel_err[idx]
        ind = ind_vars[idx]

        axes.errorbar(ind, keff, yerr=err, fmt='s', markersize=2,
                      color='blue', capsize=4)

    fig.savefig('depletion_results.eps', format='eps', dpi=2000)
    


lines = get_lines()
keff, res_err = parse_keff(lines)
time, BU = parse_table_210(lines)

plot_results(keff, res_err, time)
