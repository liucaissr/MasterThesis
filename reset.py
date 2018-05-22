from os import getcwd, listdir, sep, remove, error, path
from shutil import *
import shutil

#shutil.rmtree('/folder_name')


cur = getcwd()
pdfdir = cur+sep+'pdf'
svgdir = cur+sep+'svg'
objdir = cur+sep+'obj'
resultdir = cur+sep+'resultsvg'
tempdir = cur + sep + 'tmp'

dirs = [pdfdir, svgdir, objdir, resultdir, tempdir]

for dir in dirs:
    for fdir in listdir(dir):
        if fdir != ".DS_Store":
            shutil.rmtree(dir+sep+fdir)


srcdir = '/Users/my/Desktop/MasterThesis/mt1git/OriginalInput'

input = []
input.append('Layer3.pdf')
input.append('Layer2.pdf')
input.append('Layer1.pdf')
input.append('171130-MicroHeaterLayout-final.svg')
input.append('171130-IDELayout-final.svg')



for f in input:
    src = srcdir + sep + f
    temp = cur+sep+'tmp'+sep+ f
    copyfile(src, temp)

'''
testdir = '/Users/my/Desktop/MasterThesis/source/testcase'
testinput = []
# todo not work on testpatition1.svg!!!
testinput.append('testpatition1.svg')
for f in testinput:
    src = testdir + sep + f
    temp = cur+sep+'tmp'+sep+ f
    copyfile(src, temp)
'''