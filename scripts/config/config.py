# -*- coding: utf-8 -*-

import os
import inspect, sys

##############################
####	  PROCESS
##############################


ROOT_DIR = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))

SCRIPT_ROOT_DIR = os.path.realpath(os.path.dirname(__file__))

"""
# Directory
DATA_DIR= "%s/data/"%ROOT_DIR
DATA_ORIGINAL = "%s/original_data/"%DATA_DIR
DATA_CLEAN = "%s/clean_data/"%DATA_DIR

"""

# Path for scripts
DATA_ORIGINAL_MACHINES = "../data/original_data/machines/"
DATA_ORIGINAL_PATIENT = "../data/original_data/patient-donor/"
DATA_MODEL = "../data/clean_data/model/"
DATA_CLEAN = "../data/clean_data/"



##############################
####	  VARIABLES
##############################

FILE_NAME_HEADER = {
	'machines': 'BLOC'
}


FULL_HEADER = ['id_patient', 'time', 'B.I.S', 'BIS SR', 'DC', 'ET Des.', 'ET Sevo.', 'ETCO2', 'ETCO2 (mmHg)',
 				'ETO2', 'FC', 'FICO2', 'FICO2 (mmHg)', 'FIN2O', 'FiO2', 'FR', 'FR(ecg)', 'MAC',
 				'NMT TOF', 'NMTratio', 'PAPdia', 'PAPmoy', 'PAPsys', 'PASd', 'PASm', 'PASs',
 				'PEEPtotal', 'Pmax', 'Pmean', 'PNId', 'PNIm', 'PNIs', 'Pplat', 'RR(co2)', 'SpO2',
 				'SvO2 (m)', 'Temp', 'VT']

MODEL_TABLE_FIELDS = {
	'neurology': ['id_patient', 'time', 'bis', 'bis sr','et_des', 'et_sevo', 'nmt_tof', 'nmtratio'],
	'haemodynamic': ['id_patient', 'time', 'dc', 'fc', 'papdia', 'papmoy', 'papsys', 'pasd', 'pasm', 'pass', 'pnid', 'pnim', 'pnis'],
	'respiratory': ['id_patient', 'time', 'etco2', 'eto2', 'fico2', 'fin2o', 'fio2', 'fr','fr_ecg', 'mac', 'peeptotal', 'pmax', 'pmean', 'pplat', 'rr_co2','spo2', 'svo2__m', 'vt'],
	'temperature': ['id_patient', 'time', 'temp']
}