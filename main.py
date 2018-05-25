# !/usr/bin/python
from os import getcwd, listdir, sep, remove, error, path
from tools.directories import Build
from tools.pdf import Explode, ConvertToSVG
from tools.svg import ExtractObj, cutPolygon
import time
import sys
from shutil import *
import shutil
import logging
import setuplog

# arg1 = files folder
# arg2 = no_merge_threshold

no_merge_factor = 0
no_absorption_factor = 0.2

'''
logfile = 'debug.log'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(logfile)
stream_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')

stream_handler.setFormatter(stream_formatter)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(file_formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
'''
setuplog.setup_logging()
logger = logging.getLogger(__name__)

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
loglog = 'execution.log'

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
    if path.isfile(loglog):
        remove(loglog)
        out = open(loglog, 'w')
        out.close()
except error, value:
    print value[1]

def logthis(newtext):
    log = currentpath + sep + loglog
    input = open(log, 'r')
    text = input.read()
    input.close()
    output = open(log, 'w')
    output.write(text + newtext + '\n')
    output.close()

logger.info('Begin the convertion')

dirs.append(tmpdir)
dirs.append(resultdir)
# Creates a directory structure.
now = Build()
for newdir in dirs:
    now.createDirIfNotExist(newdir, currentpath)

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
action = Explode()
for currentdir in listdir(pdfdir):
    # todo: ".pdf" in currentdir
    if '.pdf' in currentdir:
        action.explodePages(pdfdir + sep + currentdir)

# Convert each pdf page to svg file
action = ConvertToSVG()
pdfdir = currentpath + sep + pdfdir
svgdir = currentpath + sep + svgdir
for currentdir in listdir(pdfdir):
    if '.pdf' in currentdir:
        logger.info('Converting each pdf page of %s to svg' % (pdfdir + sep + currentdir))
        action.converPdfToSvg(pdfdir + sep + currentdir, svgdir + sep + currentdir)

# todo: cut polygon
# Convert each pdf page to svg file
action = cutPolygon()
resultdir = currentpath + sep + resultdir

for currentdir in listdir(svgdir):
    #todo: change to general
    if currentdir != ".DS_Store":
        logger.info('Partitioning each svg page of %s' % (svgdir + sep + currentdir))
        action.cutSVG(svgdir + sep + currentdir, resultdir + sep + currentdir, no_merge_factor, no_absorption_factor)

# Extract objects from svg
action = ExtractObj()
for currentdir in listdir(resultdir):
    if currentdir != ".DS_Store":
        logger.info('Extracting objects from svg %s' % (svgdir + sep + currentdir))
        action.extractObjects(resultdir + sep + currentdir)

logger.info('Output is saved in folder %s' % (resultdir))


# add log
#todo change time format
#todo log.debug (try cast)
#todo multithreading