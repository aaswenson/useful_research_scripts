import glob
import matplotlib.pyplot as plt

process_files = glob.glob('./inputs/*')

def get_EOL_keff(filename):

    with open(filename, 'r') as file:
        savestate = False
        radius = float(file.readline().split('_')[1])
        
        for line in file:
            if 'Correcter calc    30' in line:
                savestate = True
            if savestate == True and 'final k(col/abs/trk len)' in line:
                keff = float(line.split()[4])
                std = float(line.split()[8])

    return radius, keff, std

keff = []
radii = []

for file in process_files:
    r, k, e = get_EOL_keff(file)
    radii.append(r)
    keff.append(k)

plt.scatter(radii, keff)
plt.show()
