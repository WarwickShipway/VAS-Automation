import math
import csv
import string
import os, sys

import matplotlib.pyplot as plt
import numpy as np

print ("\n** Solution found **")
print ("\n** Running results plots **")

# *********************************************************
#                    Pre Processing of Results
# *********************************************************
# initialise lists of results
aCoords1, aCoords2, aCoords3 = [], [], []
aKP = []
aNodes = []
aPipeESF = []
aSM = []
aeDCC, aeLCC = [], []

output = "output_VAS_0.7ax1.0lat"
with open(output + "LCC.csv",) as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)  # skip the headers
    for row in reader:
        aNodes.append(float(row[0]))
        aCoords1.append(float(row[1]))
        aCoords2.append(float(row[2]))
        aCoords3.append(float(row[3]))
        aKP.append(float(row[4]))  
        aPipeESF.append(float(row[5]))
        aSM.append(float(row[6]))
        aeDCC.append(float(row[7]))
        aeLCC.append(float(row[8]))

#fig, ax = plt.subplots()
#ax.plot(aKP, aPipeESF)
        
fig, ax = plt.subplots(2, 2, figsize = (12, 7))

# for EAF inverted plot
minEAF = min(aPipeESF)
maxEAF = max(aPipeESF)
'''
# plotting
ax[0, 0].plot(aKP, aPipeESF)
ax[1, 0].plot(aKP, aCoords2)
ax[0, 1].plot(aKP, aSM)
ax[1, 1].plot(aKP, aeDCC)
ax[1, 1].plot(aKP, aeLCC, '-g')

plt.rcParams['axes.grid'] = True

plt.show()
'''

ax1 = plt.subplot(221) # plot 1
ax1.plot(aKP, aPipeESF)
ax1.set_ylim(minEAF, maxEAF)
#plt.title('EAF')
plt.xlabel('KP, m')
plt.ylabel('EAF, N')

ax2 = plt.subplot(222) # plot 2
ax2.plot(aKP, aSM)
plt.xlabel('KP, m')
plt.ylabel('Moment, Nm')

ax3 = plt.subplot(223) # plot 3
ax3.plot(aKP, aCoords2)
plt.xlabel('KP, m')
plt.ylabel('Lateral Displacement, m')

ax4 = plt.subplot(224) # plot 4
ax4.plot(aKP, aeDCC, 'k')
ax4.plot(aKP, aeLCC)
plt.xlabel('KP, m')
plt.ylabel('Acceptance Criteria, -')
ax4.legend(["DCC", "LCC"])

plt.rcParams['axes.grid'] = True
plt.show()