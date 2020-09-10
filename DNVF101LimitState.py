# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 20:39:05 2020

@author: WRShipway

note - need to use pressure along line, not a constant
for trawling see F101, 2017, Eq.5.34 as well
"""

import numpy as np
import csv
#from odbAccess import *
import string
import os, sys
#import osutils

clear = lambda: os.system('cls')
clear()

g = 9.80665

E = 207.0E+09           # [Pa] elastic modulus 
nu = 0.3                # [-] poisson's ratio

D = 304.0 / 1000        # [m] nominal steel pipeline outer diameter
ODmax = 304.0 / 1000
ODmin = 304.0 / 1000

t = 19.7 / 1000		    # [m] inner pipe thickness
tCorr = 0.0 / 1000      # [m] corrosion allowance
WD = 100.0              # [m] water depth      
h   = 0.0               # [m] elevation, for pressure above water surface
Tdes = 50.0             # [degC] design temperature
rhoW = 1025.0           # [kg/cu.m] seawater density
rhoCon = 800.0          # [kg/cu.m] content density, for pMin
SMYS = 450.0E+06        # [Pa]
SMTS = 535.0E+06        # [Pa]
SuppU = ""              # "Y" for yes
gammam  = 1.15          # material resistance factor, Table 5-4. 1.0 for fatigue
gammaSC = 1.14          # safety class resistance factor, Table 5-5. L, M, H = 1.04, 1.14, 1.26. Pressure containment is other values
gammaF = 1.1            # functional load effect factor, F101, 2007, Table 4-4, 1.0 for ALS, 1.1 for ULS
gammaC = 1.0            # conditional load effect factor, F101, 2007, Table 4-5, uneven seabed = 1.07, flat = 0.82, pressure test = 0.93, otherwise = 1
gammaE = 1.3            # env load effect factor, F101, 2007, Table 4-4, 1.0 for ALS, 1.3 for ULS
gammaEp = 2.5           # strain resistance factor, F101, 2007, Table 5-8, L, M, H = 2, 2.5, 3.3
alphaFab = 1.0          # SMLS = 1, UOE = 0.85, other = 0.93

alphah = max(SMYS / SMTS, 0.93)                             # F101, 2007, Sec.5 D608 (0.93 for CS)
alphaU = 1.0 if SuppU == "Y" else 0.96                      # F101, 2007, Table 5-6
# geometry
t2 = t - tCorr
f0 = max((ODmax - ODmin) / D, 0.005)                      # Eq. 5.13
xf_derateT = [50, 100, 200]
yf_derateT = [0, 30, 70]
xf_girthWeld = [0, 20, 60]
yf_girthWeld = [1, 1, 0.6]

# validity
if D / t2 > 45: "Warning - DCC check not valid"

# DCC, 2007, Sec.5, p.47-48, functional loading only
def DCC(eF):

    fyT = np.interp(Tdes, xf_derateT, yf_derateT) * 1.0E+06     # F101, 2007, Figure 2
    fy = (SMYS - fyT) * alphaU                                  # F101, 2007, Eq.5.5
    fu = (SMTS - fyT) * alphaU                                  # F101, 2007, Eq.5.6
    alphagw = max(0.6, np.interp(D / t2, xf_girthWeld, yf_girthWeld))      # F101, 2007, Sec.13 E1000
    if D / t2 > 60: print '\nNote: D/t is outside girth weld factor limits\n'
    
    pExt    = rhoW * g * WD                                     # [Pa] external pressure
    pMin    = rhoCon * g * (WD + h)                             # [Pa] minimum sustainable internal pressure
    fcb     = min(fy, fu / 1.15)                                # F101, 2007, Eq.5.9
    
    pb = 2 * t2 / (D - t2) * fcb * 2/np.sqrt(3)       # F101, 2007, Eq.5.8. Using t, not tmin?? Note D200 Eq. 5.9 states t2 in LCC, but not DCC. What does new code say?
    
    # **** DCC internal overpressure ****
    # DNV F101, 2007, Section 5 D608, DCC internal overpressure
    #eF = max(aeF)
    eSd = eF * gammaF * gammaC
    ec = 0.78 * ((t2 / D) - 0.01) * (1.0 + 5.75 * (pMin - pExt) / pb) * alphah**-1.5 * alphagw      # F101, 2007, Eq.5.30
    eRd = ec / gammaEp
    
    DCCpIn = eSd / eRd                                          # F101, 2007, Formula.5.29
    
    # DNV F101, 2007, Section 5 D609, DCC external overpressure
    pEl = (2 * E * (t2 / D)**3) / (1 - nu**2)                      # Eq. 5.11
    pP = fy * alphaFab * 2 * t2 / D                                # Eq. 5.12
    
    # DNV F101, 2007, Section 13 E700, 3rd deg poly solution
    b		= -pEl
    c		= -(pP**2.0 + pP * pEl * f0 * D / t2)
    d		= pEl * pP**2.0
    u		= (b**2.0 / -3.0 + c) / 3.0
    v		= (2.0 * b**3 / 27.0 - b * c / 3.0 + d) / 2.0
    phi     = np.arccos(-v / np.sqrt(-1.0 * u**3.0))
    
    ya = 2.0 * np.sqrt(-u)
    	
    y1  = ya * np.cos(phi / 3.0)
    	
    y2a	= np.cos(phi / 3.0 + 2.0 * np.pi / 3.0)
    y2  = ya * y2a
    
    y3a = np.cos((phi / 3.0) + (np.pi * 60.0 / 180.0))
    y3  = -ya * y3a
    		
    if (y1 - b /3) < 0: y1 = 1.0E99
    if (y2 - b /3) < 0: y2 = 1.0E99
    if (y3 - b /3) < 0:	y3 = 1.0E99
    if y3 <= y1:
    	if y3 <= y2: y = y3
    	else: y = y2
    else:
    	if y1 <= y2: y = y1
    	else: y = y2
    
    pC = y - b / 3
    
    ecpExt = 0.78 * (t2 / D - 0.01) * (1.0 + 5.75 * (0.0 / pb)) * (alphah**-1.5) * alphagw
    DCCpExt = (eSd / (ecpExt / gammaEp))**0.8 + ((pExt - pMin) / (pC / (gammam * gammaSC)))
    
    # results
    if pExt < pMin:
        DCC = DCCpIn
        pSwitch = "internal"
    else:
        DCC = DCCpExt
        pSwitch = "external"    
    
    if DCC > 1.0: print "WARNING: DCC = {}, {} pressure check FAILS" .format(DCC, pSwitch)

    return DCC
'''
aeF = [0.0, 0.35 / 100.0, 0.2 / 100, 2.0 / 100]       # testing - mechanical strain
aeDCC= []

for eF in aeF:
    aeDCC.append (DCC(eF))
print aeDCC
'''
# LCC, 2007, Sec.5, p.47-48, functional loading only
def LCC(M, EAF):

    g = 9.81
    
    E = 207.0E+09       # [Pa] elastic modulus 
    nu = 0.3            # [-] poisson's ratio
    
    D = 304.0 / 1000       # [m] nominal steel pipeline outer diameter
    ODmax = 304.0 / 1000
    ODmin = 304.0 / 1000
    
    t = 19.7 / 1000         # [m] steel pipeline wall thickness
    tCorr = 0.0 / 1000      # [m] steel pipeline corrosion allowance
    
    p   = 100.0E+05         # [Pa] internal pressure, Table 4-3
    pMin = 0.0              # [Pa] minimum sustainable internal pressure
    aSM = 100.0E+03         # testing
    aESF = -100.0E+03       # testing
    WD = 100.0              # [m] water depth
    rhoW = 1025.0           # [kg/cu.m] seawater density
    Tdes = 50.0             # [degC] design temperature
    
    gammaInc = 1.05         # incidental to design pressure ratio, Table 3-1
    gammam  = 1.15          # material resistance factor, Table 5-4. 1.0 for fatigue
    gammaSC = 1.14          # safety class resistance factor, Table 5-5. L, M, H = 1.04, 1.14, 1.26. Pressure containment is other values
    gammaF  = 1.2           # functional load effect factor, F101, 2007, Table 4-4, 1.0 for ALS, 1.1 for ULS
    gammaC  = 1.0           # conditional load effect factor, uneven bed = 1.07, hydrotest = 0.93. Concept select = 0.85
    alphaFab = 1.0          # SMLS = 1, UOE = 0.85, other = 0.93
    
    # moment & EAF load from FEA
    M = max(0.0, aSM)           # [Nm] max moment
    MSd = M * gammaF * gammaC   # design moment, Eq. 4.5
    #EAF = max(0.0, aESF)
    EAF = aESF
    SSd = EAF * gammaF * gammaC  # design EAF, Eq. 4.7. USE pIn
    
    # geometry
    t2 = t - tCorr
    f0 = max(((ODmax - ODmin) / D), 0.005)      # Eq. 5.13
    
    # material rating
    SMYS = 450.0E+06        # [Pa]
    SMTS = 535.0E+06        # [Pa]
    SuppU = ""              # "Y" for yes
    alphaU = 1.0 if SuppU == "Y" else 0.96                      # F101, 2007, Table 5-6
    xf_derateT = [50, 100, 200]
    yf_derateT = [0, 30, 70]
    fyT = np.interp(Tdes, xf_derateT, yf_derateT) * 1.0E+06     # F101, 2007, Figure 2
    fy = (SMYS - fyT) * alphaU                                  # F101, 2007, Eq.5.5
    fu = (SMTS - fyT) * alphaU                                  # F101, 2007, Eq.5.6
    
    fcb     = min(fy, fu / 1.15)
    pExt    = rhoW * g * WD                                     # external pressure, Sec4 B300
    pb      = ((2 * t2) / (D - t2)) * fcb * 2 / np.sqrt(3)     # burst pressure, Eq. 5.8. USE T2
    pIn     = p * gammaInc
    
    # DNV F101, 2007, Section 5 D607, LCC internal overpressure
    # combined loading factor, Eq. 5.24
    if D / t2 < 15.0: beta = 0.5       
    elif D / t2 <= 60.0: beta = (60.0 - (D / t2)) / 90.0
    else: beta = 0.0
    
    # pressure factor, Eq. 5.23
    p_ratio = (pIn - pExt) / pb
    if p_ratio < 2.0 / 3.0: alphaP = 1 - beta
    else: alphaP = 1 - (3 * beta * (1 - p_ratio))
    
    alphaC  = (1 - beta) + beta * (fu / fy)                     # flow stress parameter, Eq. 5.22
    Mp      = fy * (D - t2)**2 * t2                            # plastic moment capacity, Eq. 5.21. USE T2
    Sp      = fy * np.pi * (D - t2) * t2                       # plastic EAF capacity, Eq. 5.20. USE T2
    MSdNorm   = MSd / Mp                                      # normalised moment
    SSdNorm   = SSd / Sp                                      # normalised EAF. USE T2
    
    LCCpIn = (gammam * gammaSC * (abs(MSdNorm) / alphaC) + 
           ((gammam * gammaSC * SSdNorm) / alphaC)**2)**2 + \
           (alphaP * ((pIn - pExt)/(alphaC * pb)))**2                # Eq. 5.19b
    
    # DNV F101, 2007, Section 5 D607, LCC external overpressure
    pEl = (2 * E * (t2 / D)**3) / (1 - nu**2)                      # Eq. 5.11
    pP = fy * alphaFab * (2 * t2 / D)                              # Eq. 5.12
    
    # DNV F101, 2007, Section 13 E700, 3rd deg poly solution
    b		= -pEl
    c		= -(pP**2.0 + pP * pEl * f0 * D / t2)
    d		= pEl * pP**2.0
    u		= ((b**2.0) / -3.0 + c) / 3.0
    v		= (2.0 * (b**3) / 27.0 - b * c / 3.0 + d) / 2.0
    phi     = np.arccos(-v / np.sqrt(-1.0 * u**3.0))
    
    ya = 2.0 * np.sqrt(-u)
    	
    y1  = ya * np.cos(phi / 3.0)
    	
    y2a	= np.cos(phi / 3.0 + 2.0 * np.pi / 3.0)
    y2  = ya * y2a
    
    y3a = np.cos((phi / 3.0) + (np.pi * 60.0 / 180.0))
    y3  = -ya * y3a
    		
    if (y1 - b /3) < 0: y1 = 1.0E99
    if (y2 - b /3) < 0: y2 = 1.0E99
    if (y3 - b /3) < 0:	y3 = 1.0E99
    if y3 <= y1:
    	if y3 <= y2: y = y3
    	else: y = y2
    else:
    	if y1 <= y2: y = y1
    	else: y = y2
    
    pC = y - b / 3
    
    LCCpExt = (gammam * gammaSC * (abs(MSdNorm) / alphaC) + \
           ((gammam * gammaSC * SSdNorm) / alphaC)**2)**2 + \
           (gammam * gammaSC * ((pExt - pMin) / pC))**2                # Eq. 5.28b
    
    # results
    if pExt < pIn:
        LCC = LCCpIn
        pSwitch = "internal"
    else:
        LCC = LCCpExt
        pSwitch = "external"
        
    #if LCC <= 1.0: print "LCC = {}, {} pressure check PASSES" .format(LCC, pSwitch)
    #else: print "LCC = {}, {} pressure check FAILS" .format(LCC, pSwitch)
    if LCC > 1.0: print "LCC = {}, {} pressure check FAILS" .format(LCC, pSwitch)
    
    return LCC
    
    # validity
    #if LCC_pIn < LCC_pExt: "
    if D / t2 > 45: "Warning - LCC check not valid"
    if D / t2 < 15: "Warning - LCC check limitation (DNV F101 Table 1-1)"
    if abs(SSd) / Sp < 0.4: "Warning - axial capacity not valid (DNV F101, 2017)"    