# to confirm the result conflict relationship

from os import system, listdir, sep
from svgpathtools import svg2paths, wsvg
from tools.segment import *
from bisect import *
from operator import attrgetter
from os import getcwd, listdir, sep, remove, error, path
import os.path

cur = '/Users/my/Desktop/MT/code/MasterThesis/expectedOutput'

IDE = cur+sep+'171130-IDELayout-final'
Heater = cur+sep+'171130-MicroHeaterLayout-final'
L1 = cur+sep+'LAYER1'
L2 = cur+sep+'LAYER2'
L3 = cur+sep+'LAYER3'
tempdir = cur + sep + 'tmp'

curproject = getcwd()
outputpath = '/Users/my/Desktop/MT/code/MasterThesis/output/'
resultpath = outputpath + max(listdir(outputpath))
testpath = '/Users/my/Desktop/MT/code/MasterThesis/testrecord/'
testfile = testpath + max(listdir(outputpath)) + '.txt'
record = open(testfile, 'w')

inputs = []
for f in listdir(resultpath):
    if not f.startswith('.'):
        inputs.append(f)

no_merge_real = {}
no_absorb_real = {}
distance_real = {}
no_merge_test = {}
no_absorb_test = {}
distance_test = {}

for file in inputs:
    realdir = cur+sep+file+sep
    testdir = resultpath+sep+file+sep
    conflict_real = realdir+'conflict.txt'
    test = testdir + 'conflict.txt'
    for ff in listdir(testdir):
        if '.svg' in ff:
            rawpaths, attributes = svg2paths(testdir  +ff)
            n = len(rawpaths) - 1
            break
    curcur = 'nomerge'
    flag = 0
    finno = 0
    testno = 0
    no_merge_real = {}
    no_absorb_real = {}
    distance_real = {}
    no_merge_test = {}
    no_absorb_test = {}
    distance_test = {}
    with open(conflict_real,'r') as f:
        for line in f:
            if line == 'FIN\n':
                finno += 1
                continue
            if finno == 0:
                if line != '\n' and line != 'no merge conflict:\n':
                    str = line.split()
                    if str[0] not in no_merge_real.keys():
                        no_merge_real[str[0]] = []
                    for i in range(0, int(str[1])):
                        no_merge_real[str[0]].append(str[2+i])
            if finno == 1:
                if line != '\n' and line != 'no absorption conflict:\n':
                    str = line.split()
                    if str[0] not in no_absorb_real.keys():
                        no_absorb_real[str[0]] = []
                    for i in range(0, int(str[1])):
                        no_absorb_real[str[0]].append(str[2+i])
            if finno == 2:
                if line != '\n' and line != 'distance:\n':
                    str = line.split()
                    if str[0] not in distance_real.keys():
                        distance_real[str[0]] = {}
                    distance_real[str[0]][str[1]] = str[2]
    with open(test,'r') as f:
        for line in f:
            if line == 'FIN\n':
                testno += 1
                continue
            if testno == 0:
                if line != '\n' and line != 'no merge conflict:\n':
                    str = line.split()
                    if str[0] not in no_merge_test.keys():
                        no_merge_test[str[0]] = []
                    for i in range(0, int(str[1])):
                        no_merge_test[str[0]].append(str[2+i])
            if testno == 1:
                if line != '\n' and line != 'no absorption conflict:\n':
                    str = line.split()
                    if str[0] not in no_absorb_test.keys():
                        no_absorb_test[str[0]] = []
                    for i in range(0, int(str[1])):
                        no_absorb_test[str[0]].append(str[2+i])
            if testno == 2:
                if line != '\n' and line != 'distance:\n':
                    str = line.split()
                    if str[0] not in distance_test.keys():
                        distance_test[str[0]] = {}
                    distance_test[str[0]][str[1]] = str[2]

    record.write('%s\n'% file)
    tf =  no_merge_real == no_merge_test and no_absorb_real == no_absorb_test\
    #and distance_real == distance_test
    record.write('%s\n'% tf)
    print file
    print tf
    no_merge = [no_merge_real, no_merge_test]
    no_absorb = [no_absorb_real, no_absorb_test]
    distance = [distance_real, distance_test]
    d = [no_merge, no_absorb, distance]
    # i[0] = real / i[1] = testscript
    record.write('1: merge, 2: LP, 3: distance')
    for i in d:
        num_er = 0
        #record.write('%d\n' % d.index(i))
        if i[0]==i[1]:
            continue
        else:
            record.write('%d false\n' % (d.index(i)))

        for k1 in i[1].keys():
            for k2 in i[0].keys():
                if k1 == k2:
                    if set(i[1][k1]) != set(i[0][k2]):
                        record.write('%s '%(k1))
                        s = set(i[1][k1]) - set(i[0][k2])
                        if len(s) == 0:
                            s = set(i[0][k1]) - set(i[1][k2])
                            num_er -= len(s)
                            record.write('- ')
                        else:
                            num_er += len(s)
                            record.write('+ ')
                        for obj in s:
                            record.write('%s ' % (obj))
                        record.write('\n')
        error = float(num_er) / n
        if error != 0:
            record.write('%s error = %s\n' % (d.index(i), error))

