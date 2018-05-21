# !/usr/bin/python
from os import getcwd, listdir, sep, remove, error, path
from tools.directories import Build
from tools.pdf import Explode, ConvertToSVG
from tools.svg import ExtractObj, cutPolygon
from tools.printobj import PrintObj
import time
from svgpathtools import svg2paths, wsvg


execfile('reset.py')
# Directories names
currentpath = getcwd()
tmpdir = 'tmp'
pdfdir = 'pdf'
svgdir = 'svg'
objdir = 'obj'
printdir = 'print'
resultdir = 'resultsvg'
logfile = 'execution.log'

try:
    if path.isfile(logfile):
        remove(logfile)
        out = open(logfile, 'w')
        out.close()
except error, value:
    print value[1]

dirs = [tmpdir, pdfdir, svgdir, objdir, resultdir]


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
    logthis('Create a directory structure to: %s.' % (objdir + sep + filenamedir))
    now.createDirStructure(objdir + sep + filenamedir)
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
no_merge_factor = 2
no_absorption_factor = 0.2
logthis('\n')
for currentdir in listdir(svgdir):
    if currentdir != ".DS_Store":
        logthis('Cut each svg page of %s for print' % (svgdir + sep + currentdir))
        action.cutSVG(svgdir + sep + currentdir, resultdir + sep + currentdir, no_merge_factor, no_absorption_factor)

# Extract objects from svg
action = ExtractObj()
objdir = currentpath + sep + objdir
for currentdir in listdir(resultdir):
    if currentdir != ".DS_Store":
        logthis('Extracting objects from svg %s to obj' % (resultdir + sep + currentdir))
        action.extractObjects(resultdir + sep + currentdir, objdir + sep + currentdir)

logthis('Finish conversions.')