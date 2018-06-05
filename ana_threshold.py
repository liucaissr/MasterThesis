from tools.svg import ExtractObj, cutPolygon
from os import getcwd, listdir, sep
import os.path
import time
import numpy as np
import confirm
from tools.directories import Build

'''
currentpath = getcwd()
svgdir = 'svg'
svgdir = currentpath + sep + svgdir
filedir = currentpath + sep + svgdir + sep + '171130-MicroHeaterLayout-final'

# Convert each pdf page to svg file
action = cutPolygon()
now = Build()
no_absorption_factor = 0.2
for no_merge_factor in np.arange(0.1,1,0.3):
    resultdir = 'testthreshold'+ sep + '171130-MicroHeaterLayout-final' + sep +time.strftime("%Y%m%d%H%M")
    testthresholddir = currentpath + sep + resultdir
    #for currentdir in listdir(svgdir):
        #curpath = svgdir + sep + currentdir
    currentdir = '171130-MicroHeaterLayout-final'
    curpath = svgdir + sep + '171130-MicroHeaterLayout-final'
    now.createDirStructure(resultdir + sep + currentdir)
    if os.path.isdir(curpath):
        action.cutSVG(curpath, resultdir + sep + currentdir, no_merge_factor, no_absorption_factor)

outputpath = '/Users/my/Desktop/MasterThesis/source/testthreshold/'
testresults = outputpath + '171130-MicroHeaterLayout-final'
testrecord = outputpath + '171130-MicroHeaterLayout-final.txt'

for d in listdir(testresults):
    confirm(testresults, testrecord)
'''

#todo wtf why you are not working???