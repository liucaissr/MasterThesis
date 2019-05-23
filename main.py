# !/usr/bin/python
from os import getcwd, listdir, sep
import os.path
from tools.directories import Build
from tools.pdf import Explode, ConvertToSVG
from tools.design import ExtractObj, cutPolygon
import time
import sys
from shutil import *
import shutil
import logging
import setuplog

# arg1 = files folder
# arg2 = no_merge_threshpoint_on_pathold

no_merge_factor = 0
lp_factor = 0.2

setuplog.setup_logging()
logger = logging.getLogger(__name__)

# argv[2] = merging_factor
for i in range(0,len(sys.argv)):
    if i == 1:
        filesfolder = sys.argv[i]
    if i == 2:
        no_merge_factor = float(sys.argv[i])

# Directories names
currentpath = getcwd()
tmpdir = 'tmp'
pdfdir = 'pdf'
svgdir = 'svg'
resultdir = 'output'+ sep +time.strftime("%Y%m%d%H%M")
loglog = 'execution.log'

dirs = [pdfdir, svgdir, tmpdir, resultdir]

#dirs.append()
#dirs.append(resultdir)
# Creates a directory structure.
now = Build()
for newdir in dirs:
    now.createDirIfNotExist(newdir, currentpath)

for dir in dirs:
    dirpath = currentpath + sep + dir
    for fdir in listdir(dirpath):
        curpath = svgdir + sep + fdir
        if os.path.isdir(curpath):
            shutil.rmtree(dirpath+sep+fdir)

inputpath = currentpath + sep + filesfolder
for f in listdir(inputpath):
    src = inputpath + sep+ f
    temp = currentpath+sep+'tmp'+sep + f
    copyfile(src, temp)


logger.info('Begin the convertion')


# Normalize pdf names, cut and paste pdf in respective dir.
now.normalizeNameOfPdfs(listdir(tmpdir), tmpdir)

# Buid the dir structure for pdf and svg.
for filenamedir in listdir(tmpdir):
    if '.pdf' in filenamedir:
        filenamedir = filenamedir.replace('.pdf', '')
        now.createDirStructure(pdfdir + sep + filenamedir)
    if '.svg' in filenamedir:
        filenamedir = filenamedir.replace('.svg', '')
    now.createDirStructure(svgdir + sep + filenamedir)
    now.createDirStructure(resultdir + sep + filenamedir)

# Cut the pdf on tmp dir to pdf name dir.

now.cutFiles(tmpdir, pdfdir, svgdir)

# Performs the separate pages process.
action = Explode()#todo: change inkscape path firstly
for currentdir in listdir(pdfdir):
    curpath = pdfdir + sep + currentdir
    if os.path.isdir(curpath):
        action.explodePages(pdfdir + sep + currentdir)

# Convert each pdf page to svg file
action = ConvertToSVG()#todo: change inkscape path firstly
pdfdir = currentpath + sep + pdfdir
svgdir = currentpath + sep + svgdir
for currentdir in listdir(pdfdir):
    curpath = pdfdir + sep + currentdir
    if os.path.isdir(curpath):
        logger.info('Converting each pdf page of %s to svg' % (pdfdir + sep + currentdir))
        action.converPdfToSvg(pdfdir + sep + currentdir, svgdir + sep + currentdir)

# Convert each pdf page to svg file
action = cutPolygon()
resultdir = currentpath + sep + resultdir

for currentdir in listdir(svgdir):
    curpath = svgdir + sep + currentdir
    if os.path.isdir(curpath):
        logger.info('Partitioning each svg page of %s' % (svgdir + sep + currentdir))
        action.cutSVG(svgdir + sep + currentdir, resultdir + sep + currentdir, no_merge_factor, lp_factor)

# Extract objects from svg
action = ExtractObj()
for currentdir in listdir(resultdir):
    curpath = resultdir + sep + currentdir
    if os.path.isdir(curpath):
        logger.info('Extracting objects from svg %s' % (svgdir + sep + currentdir))
        action.extractObjects(resultdir + sep + currentdir)

logger.info('Output is saved in folder %s' % (resultdir))

