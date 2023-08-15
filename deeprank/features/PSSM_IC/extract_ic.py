import sys

import numpy as np


def write_newfile(names_oldfile, name_newfile):

    chainID = {0: 'A', 1: 'B'}
    resconv = {
        'A': 'ALA',
        'R': 'ARG',
        'N'	: 'ASN',
        'D': 'ASP',
        'C': 'CYS',
        'E': 'GLU',
        'Q': 'GLN',
        'G': 'GLY',
        'H': 'HIS',
        'I': 'ILE',
        'L': 'LEU',
        'K': 'LYS',
        'M': 'MET',
        'F': 'PHE',
        'P': 'PRO',
        'S': 'SER',
        'T': 'THR',
        'W': 'TRP',
        'Y': 'TYR',
        'V': 'VAL'
    }

    with open(name_newfile, 'w') as new_file:
        for ifile, f in enumerate(names_oldfile):

            with open(f, 'r') as f:
                data = f.readlines()[4:-6]
                    # write the new file
            for l in data:
                l = l.split()
                if len(l) > 0:

                    resNum = l[0]
                    feat = '{:>4}'.format(chainID[ifile]) + '{:>10}'.format(resNum)
                    resName1 = l[2]
                    resName3 = resconv[resName1]
                    feat += '{:>10}'.format(resName3)

                    feat += '\t'
                    values = float(l[-2])
                    feat += '\t{:>10}'.format(values)

                    feat += '\n'
                    new_file.write(feat)


oldfile_dir = '../PSSM/'
oldfiles = list(filter(lambda x: '.PSSM' in x, os.listdir(oldfile_dir)))
oldfiles = [oldfile_dir + f for f in oldfiles]

#oldfiles = sp.check_output('ls %s/*PSSM' %(oldfile_dir),shell=True).decode('utf-8').split()

nfile = len(oldfiles)
oldfiles = np.array(oldfiles).reshape(nfile // 2, 2).tolist()


for filenames in oldfiles:

    print('process files\n\t%s\n\t%s' % (filenames[0], filenames[1]))
    cplx_name = [filenames[0].split('/')[-1]]
    cplx_name.append(filenames[1].split('/')[-1])
    cplx_name = list({cplx_name[0][:4], cplx_name[1][:4]})
    print(cplx_name)

    if len(cplx_name) > 1:
        print(f'error{cplx_name}')
        sys.exit()

    name_newfile = f'./{cplx_name[0]}.PSSM_IC'
    print('\nexport to \t%s\n' % (name_newfile))
    write_newfile(filenames, name_newfile)
