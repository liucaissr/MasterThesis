# script to testscript all testscript cases
import os

# Layer1,2,3 not working because of overlap between patterns.
os.system("python main.py /input/merged 0.036")
#os.system("python main.py /input/IDE 15.0")
#os.system("python main.py /input/Heater 80")
os.system("python confirmresult.py")
