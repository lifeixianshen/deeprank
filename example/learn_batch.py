import glob
import os
import re
import sys
from math import *

import numpy as np

from deeprank.learn import *
from deeprank.learn.model3d import cnn_class as cnn3d
from torch import optim

"""
An example to do cross-validation 3d_cnn at the case level
(i.e., all docked models of one case will belong either to training, valiation or test only)
"""

# os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def divide_data(
        hdf5_DIR,
        caseID_FL,
        portion=[
            0.8,
            0.1,
            0.1],
    random=True,
        write_to_file=True):
    # INPUT: the dir that stores all hdf5 data (training, validation, and test)
    # OUPUT: randomly divide them into train, validation, and test at the caseID-level. Return the filenames.
    # write_to_file: True then write the files of trainSet.txt,
    # valiatonSet.txt and testSet.txt

    if sum(portion) > 1:
        sys.exit(
            "Error: The sum of portions for train/validatoin/test is larger than 1!")

    if len(portion) != 3:
        sys.exit("Error: the length of portions has to be 3.")

    caseIDs = np.array(read_listFL(caseID_FL))
    train_caseIDs, valid_caseIDs, test_caseIDs = random_split(
        caseIDs, portion, random=random)

    print(f"\nnum of training cases: {len(train_caseIDs)}")
    print(f"num of validation cases: {len(valid_caseIDs)}")
    print(f"num of test cases: {len(test_caseIDs)}\n")

    train_database = get_hdf5FLs(train_caseIDs, hdf5_DIR)
    valid_database = get_hdf5FLs(valid_caseIDs, hdf5_DIR)
    test_database = get_hdf5FLs(test_caseIDs, hdf5_DIR)

    if write_to_file is True:
        outDIR = os.getcwd()
        write_train_valid_testFLs(
            train_database,
            valid_database,
            test_database,
            outDIR)
    return train_database, valid_database, test_database


def get_hdf5FLs(caseIDs, hdf5_DIR):

    hdf5_FLs = []
    for caseID in caseIDs:
        hdf5_FLs.extend(glob.glob(f"{hdf5_DIR}/*{caseID}.hdf5"))

    return hdf5_FLs


def read_listFL(listFL):

    with open(listFL, 'r') as f:
        caseIDs = f.readlines()
    caseIDs = [x.strip() for x in caseIDs if not re.search('^#', x)]
    print(f"{len(caseIDs)} cases read from {listFL}")
    return caseIDs


def random_split(array, portion, random=True):
    # array: np.array. Can be a list of caseIDs or a list of hdf5 file names

    if random is True:
        np.random.shuffle(array)
    n_cases = len(array)
    n_train = min(ceil(n_cases * portion[0]), n_cases)
    n_valid = floor(n_cases * portion[1])

    if sum(portion) == 1:
        n_test = n_cases - n_train - n_valid
    else:
        n_test = floor(n_cases * portion[2])

    train = array[:n_train]
    valid = array[n_train:n_train + n_valid]
    test = array[n_train + n_valid: n_train + n_valid + n_test]

    return train, valid, test


def write_train_valid_testFLs(
        train_database,
        valid_database,
        test_database,
        outDIR):
    trainID_FL = f"{outDIR}/trainIDs.txt"
    validID_FL = f"{outDIR}/validIDs.txt"
    testID_FL = f"{outDIR}/testIDs.txt"

    outFLs = [trainID_FL, validID_FL, testID_FL]
    databases = [train_database, valid_database, test_database]

    for outFL, database in zip(outFLs, databases):

        if database is not True:
            np.savetxt(outFL, database, delimiter="\n", fmt="%s")
            print(f"{outFL} generated.")


def main():

    out = './out'
    hdf5_DIR = './hdf5'
    caseID_FL = 'caseIDs.txt'
    train_database, valid_database, test_database = divide_data(
        hdf5_DIR=hdf5_DIR, caseID_FL=caseID_FL, portion=[0.2, 0.1, 0.1], random=False)

    # clean the output dir
    out = './out_3d'
    if os.path.isdir(out):
        for f in glob.glob(f'{out}/*'):
            os.remove(f)
        os.removedirs(out)

    # declare the dataset instance

    data_set = DataSet(train_database=train_database,
                       valid_database=valid_database,
                       test_database=test_database,
                       mapfly=True,
                       use_rotation=0,
                       grid_info={
                           'number_of_points': [
                               6, 6, 6], 'resolution': [
                               5, 5, 5]},

                       #            select_feature={'AtomicDensities': {'C': 1.7, 'N': 1.55, 'O': 1.52, 'S': 1.8},
                       #                			'Features'       : ['coulomb','vdwaals','charge','PSSM_*'] },
                       #           select_feature = 'all',
                       select_feature={'Features': ['PSSM_*']},
                       select_target='BIN_CLASS',
                       tqdm=True,
                       normalize_features=False,
                       normalize_targets=False,
                       clip_features=False,
                       pair_chain_feature=np.add,
                       dict_filter={'DOCKQ': '>0.01', 'IRMSD': '<=4 or >10'})

    # create the network
    model = NeuralNet(data_set, cnn3d, model_type='3d', task='class',
                      cuda=False, plot=True, outdir=out)
    #model = NeuralNet(data_set, model3d.cnn,cuda=True,ngpu=1,plot=False, task='class')

    # change the optimizer (optional)
    model.optimizer = optim.SGD(model.net.parameters(),
                                lr=0.0001, momentum=0.9, weight_decay=0.00001)

    # start the training
    model.train(
        nepoch=2,
        divide_trainset=None,
        train_batch_size=50,
        num_workers=8,
        save_model='all')


if __name__ == '__main__':
    main()
