#to confirm the resultsvg
from os import system, listdir, sep
from svgpathtools import svg2paths, wsvg
from tools.cut import *
from bisect import *
from operator import attrgetter
from os import getcwd, listdir, sep, remove, error, path
from string import *

cur = '/Users/my/Desktop/MasterThesis/mt1git/zxj'
IDE = cur+sep+'171130-IDELayout-final'
Heater = cur+sep+'171130-MicroHeaterLayout-final'
L1 = cur+sep+'LAYER1'
L2 = cur+sep+'LAYER2'
L3 = cur+sep+'LAYER3'
tempdir = cur + sep + 'tmp'

files = []

files.append('171130-IDELayout-final')
files.append('171130-MicroHeaterLayout-final')
files.append('LAYER1')
files.append('LAYER2')
files.append('LAYER3')
files.append('180523IDEPITCH70MERGED')
dirs = []
dirs.append(IDE)
#dirs.append(Heater)
dirs.append(L1)
#dirs.append(L2)
#dirs.append(L3)
curproject = getcwd()
resultsvg = curproject + '/output/201806011530'

no_merge_real = {}
no_absorb_real = {}
distance_real = {}
no_merge_test = {}
no_absorb_test = {}
distance_test = {}
for file in files:
    realdir = cur+sep+file+sep
    testdir = resultsvg+sep+file+sep
    conflict_real = realdir+'conflict.txt'
    test = testdir + 'conflict.txt'
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
    print file
    print no_merge_real == no_merge_test and no_absorb_real == no_absorb_test and distance_real == distance_test



#todo: layer 1 2 3 false???