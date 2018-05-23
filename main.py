# !/usr/bin/python
from os import getcwd, listdir, sep, remove, error, path
from tools.directories import Build
from tools.pdf import Explode, ConvertToSVG
from tools.svg import ExtractObj, cutPolygon
import time
import sys
from shutil import *
import shutil

# arg1 = files folder
# arg2 = no_merge_threshold

no_merge_factor = 0
no_absorption_factor = 0.2

#execfile('reset.py')

for i in range(0,len(sys.argv)):
    if i == 1:
        filesfolder = sys.argv[i]
    if i == 2:
        no_merge_factor = sys.argv[i]

# Directories names
currentpath = getcwd()
tmpdir = 'tmp'
pdfdir = 'pdf'
svgdir = 'svg'
resultdir = 'output'+ sep +time.strftime("%Y%m%d%I%M")
logfile = 'execution.log'

dirs = [pdfdir, svgdir]

for dir in dirs:
    dirpath = currentpath + sep + dir
    for fdir in listdir(dirpath):
        if fdir != ".DS_Store":
            shutil.rmtree(dirpath+sep+fdir)

inputpath = currentpath + sep + filesfolder
for f in listdir(inputpath):
    src = inputpath + sep+ f
    temp = currentpath+sep+'tmp'+sep + f
    copyfile(src, temp)

try:
    if path.isfile(logfile):
        remove(logfile)
        out = open(logfile, 'w')
        out.close()
except error, value:
    print value[1]


def logthis(newtext):
    log = currentpath + sep + logfile
    input = open(log, 'r')
    text = input.read()
    input.close()
    output = open(log, 'w')
    output.write(text + newtext + '\n')
    output.close()

logthis(time.ctime())
logthis('\nBegin the convertion\n\n')

dirs.append(tmpdir)
dirs.append(resultdir)
# Creates a directory structure.
now = Build()
for newdir in dirs:
    logthis('Create a directory structure to: %s.' % newdir)
    now.createDirIfNotExist(newdir, currentpath)

# Normalize pdf names, cut and paste pdf in respective dir.
logthis('\nNormalize name of the pdfs.\n')
now.normalizeNameOfPdfs(listdir(tmpdir), tmpdir)

# Buid the dir structure for pdf and svg.
for filenamedir in listdir(tmpdir):
    if '.pdf' in filenamedir:
        filenamedir = filenamedir.replace('.pdf', '')
        logthis('Create a directory structure to: %s.' % (pdfdir + sep + filenamedir))
        now.createDirStructure(pdfdir + sep + filenamedir)
    if '.svg' in filenamedir:
        filenamedir = filenamedir.replace('.svg', '')
    logthis('Create a directory structure to: %s.' % (svgdir + sep + filenamedir))
    now.createDirStructure(svgdir + sep + filenamedir)
    logthis('Create a directory structure to: %s.' % (resultdir + sep + filenamedir))
    now.createDirStructure(resultdir + sep + filenamedir)

# Cut the pdf on tmp dir to pdf name dir.
logthis('\nCut the pdf files of %s to %s.\n' % (tmpdir + '/', pdfdir + '/'))
now.cutFiles(tmpdir, pdfdir, svgdir)

# Performs the separate pages process.
action = Explode()
for currentdir in listdir(pdfdir):
    # todo: ".pdf" in currentdir
    if currentdir != ".DS_Store":
        logthis('Performs the separate pdf pages on %s.' % (pdfdir + sep + currentdir))
        action.explodePages(pdfdir + sep + currentdir)

# Convert each pdf page to svg file
action = ConvertToSVG()
pdfdir = currentpath + sep + pdfdir
svgdir = currentpath + sep + svgdir
logthis('\n')
for currentdir in listdir(pdfdir):
    if currentdir != ".DS_Store":
        logthis('Converting each pdf page of %s to svg' % (pdfdir + sep + currentdir))
        action.converPdfToSvg(pdfdir + sep + currentdir, svgdir + sep + currentdir)

# todo: cut polygon
# Convert each pdf page to svg file
action = cutPolygon()
resultdir = currentpath + sep + resultdir

logthis('\n')
for currentdir in listdir(svgdir):
    if currentdir != ".DS_Store":
        logthis('Cut each svg page of %s for print' % (svgdir + sep + currentdir))
        action.cutSVG(svgdir + sep + currentdir, resultdir + sep + currentdir, no_merge_factor, no_absorption_factor)

# Extract objects from svg
action = ExtractObj()
for currentdir in listdir(resultdir):
    if currentdir != ".DS_Store":
        logthis('Extracting objects from svg %s to obj' % (resultdir + sep + currentdir))
        action.extractObjects(resultdir + sep + currentdir)

logthis('Finish conversions.')