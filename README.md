# VAS-Automation
Analysis automation, post processing, and results tool for abaqus use.

Initial repo for VAS tool.

Contains 3 files:
  1. inUtil.py - main file. Input data and dictionary for multiple cases.
  1.1. pre-processing file for defined input variables.
  1.2. processing (commented out), to run the abaqus file.
  2. postprocessing extraction of results from abaqus file. writes to a csv for user to independantly compute results.
  3. DNVF101LimitState.py (called from item 1) - calls functions to calculate results based on postprocessing (item 2). Note not all results are required to conformity checks. Writes a separate csv file for conformity checks  along the system for interogation.
  4. plotUtil.py - reads csv results file and produces matplotlib plots for design analysis report and for engineer investigations
  
Further details are contained within code as comments.
   
The software runs by inputting relevant data into inUtil-V01.py, and DNVF101LimitState.py; running inUtil-V01.py, then plotUtil.py. Note, DNVF101LimitState.py does not need to be ran, the contained functions are called. The user is informed of progress at milestones through the cmd or kernal.

Developed with python 2.7 and anaconda/spyder. Abaqus interface only works with python 2.7 (until abaqus 2020 is released and purchased).
