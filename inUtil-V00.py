# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 16:06:56 2020

@author: WRShipway
"""

'''
GUIDE
1. inUtil - define files 
    run all friction combinations
2. extract results
3. pp with DNVLimitState
4. check acceptance
5. reduce length
6. re run loop of inUtil
7. setup a nice GUI

# POST PROCESS AND WRITE TO CSV FILE
# PRODUCE PLOTS
# FIX THE OD AND TOD
# VAS MODEL NEEDS TO HAVE MESH REFINEMENT

# DELETE THE LCK FILE
# only re-run the model with friction variables that fail
# use the DNV definition more thoroughly

'''

'''
MAIN INPUT AND PROCESSING FILE

Hobbs and EAF hand calc as part of buckling model pre processing (creation def function and call it)
change to int points: Frame.fieldOutputs['LE'].getSubset(region=elSet1, position=INTEGRATION_POINT).values

automate the pressure and temp inputs

'''

import numpy as np
import csv
#from odbAccess import *
#import string
import os, sys
#import osutils

clear = lambda: os.system('cls')
clear()

#def inUtil():

# *********************************************************
#                           Inputs
# *********************************************************
template            = 'VAS_template'
odbFile             = 'VAS_'                                # Name of default odb file
Header              = 'VAS model'
run_analysis        = "N"
formatting          = '** *************************'
SP                  = 24                                     # section points, 8 (default thin), 32, or 24 (default thick)
L                   = 100

dict={}
dict={
#'pipe_length':          [100,     100],
'e_size':               [1,      1],
'imp_mag':              [0.5,    1.0],
'carrier_node_shift':   [10000,  10000],
'mu_ax':                [0.56,   0.7],
'mu_lat':               [0.8,    1.0],
'MD_coulomb':           [0.005,  0.01],
'WD':                   [100,    100]
}

# *********************************************************
#                    Pre Processing of Data
# *********************************************************
# read template and store as list
template = template + ".inp"

with open(template, "r") as f: lines = f.read()

# write batch variables & template
cases = range(len(dict['mu_ax']))

for case in cases:
    caseName = ('%s%sax%slattest' % (odbFile, dict['mu_ax'][case], dict['mu_lat'][case]))
    with open(caseName + '.inp', "w+") as f:
        i = 0
        f.write('*HEADING\n%s\n*PREPRINT, PARVALUES=yes\n*PARAMETER\n' % Header)
        f.write('%s\n** batch parameters\n%s\n' % (formatting, formatting))
        f.write('pipe_length = %s\n' % (L))
        for key in dict:
            f.write('%s = %s\n' % (key, dict.values()[i][case]))
            i += 1
        f.write(lines)
    # *********************************************************
    #                    Processing Analysis
    # *********************************************************
    #print ("** Starting Analysis **\n")
    #os.system('abq2018 j=%s ask_delete=off int' % caseName)
    #print ("\n** Analysis Completed **\n")

# *********************************************************
#                    Post Processing of Data
# *********************************************************

#all pp needs to be in for loop
# then call following

import DNVF101LimitState

# TESTING
# initialise lists of results
aCoords1, aCoords2, aCoords3 = [], [], []
aKP = []
aNodes, aElementsc = [], []
aPipeESF = []
aPipeWeightc = []
aLE11SP1, aLE11SP2, aLE11SP3, aLE11SP4 = [], [], [], []
aTHESP1, aTHESP2, aTHESP3, aTHESP4 = [], [], [], []
aeF, aeFSP1, aeFSP2, aeFSP3, aeFSP4 = [], [], [], [], []
aSM, aSM1, aSM2, aSM3 = [], [], [], []
aeDCC, aeLCC = [], []


# Read Abq results csv
# or use pandas to read, as it will be read as floating
output = "output_VAS_0.7ax1.0lat"
with open(output+".csv") as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)  # skip the headers
    for row in reader:
        aNodes.append(float(row[0]))
        aCoords1.append(float(row[3]))
        aCoords2.append(float(row[4]))
        aCoords3.append(float(row[5]))
        aKP.append(float(row[6]))  
        aPipeESF.append(float(row[7]))
        aSM.append(float(row[8]))
        aeF.append(float(row[21]))

# calculate LCC/DCC
for eF in aeF:
    aeDCC.append (DNVF101LimitState.DCC(eF))

for PipeESF, SM in zip(aPipeESF, aSM):
    aeLCC.append(DNVF101LimitState.LCC(PipeESF, SM))

# write LCC/DCC to Abq results csv
# note python 2.7 causes issues with appending, so re-write
'''
with open(output, "a+") as f:
    writer = csv.writer(f)
    writer.writerow(aeDCC)
'''
headList = ['nodes', 'x', 'y', 'z', 'KP', 'EAF', 'SM', 'DCC', 'LCC']
EResList = zip(aNodes, aCoords1, aCoords2, aCoords3, aKP, aPipeESF, aSM, aeDCC, aeLCC)

with open(output + "LCC.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerow(headList)
    writer.writerows(EResList)

# remove redundant file, or use tempfile, section 11.6
#os.remove(output+".csv")

print ("\n** Post Processing Completed **")

'''
# and do for each case, record the DCC and LCC for each element into same output file, also get max
# if max is > 1 then decrease VAS length. need a loop to decrease, use batch file.py in notepad++
'''