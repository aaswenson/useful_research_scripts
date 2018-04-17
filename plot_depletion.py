
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


lines = get_lines()
keff, res_err = parse_keff(lines)
time, BU = parse_table_210(lines)
print(time)
