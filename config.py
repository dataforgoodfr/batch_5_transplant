# -*- coding: utf-8 -*-

import os
import inspect, sys

##############################
####	  PROCESS
##############################


ROOT_DIR = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))

# Directory
DATA_DIR= "%s/data/"%ROOT_DIR
DATA_ORIGINAL = "%s/original_data/"%DATA_DIR
DATA_CLEAN = "%s/clean_data/"%DATA_DIR


##############################
####	  VARIABLES
##############################


FULL_HEADER = ['id_patient', 'time', 'B.I.S', 'BIS SR', 'DC', 'ET Des.', 'ET Sevo.', 'ETCO2', 'ETCO2 (mmHg)',
 				'ETO2', 'FC', 'FICO2', 'FICO2 (mmHg)', 'FIN2O', 'FiO2', 'FR', 'FR(ecg)', 'MAC',
 				'NMT TOF', 'NMTratio', 'PAPdia', 'PAPmoy', 'PAPsys', 'PASd', 'PASm', 'PASs',
 				'PEEPtotal', 'Pmax', 'Pmean', 'PNId', 'PNIm', 'PNIs', 'Pplat', 'RR(co2)', 'SpO2',
 				'SvO2 (m)', 'Temp', 'VT']