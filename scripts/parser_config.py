# -*- coding: utf-8 -*-

import os
import inspect, sys

##############################
####	  PROCESS
##############################

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), '..')

REPO_NAME = 'batch_5_transplant'
ROOT_DIR = os.path.dirname(os.getcwd())
ROOT_DIR = ROOT_DIR.replace(ROOT_DIR.split('{}'.format(REPO_NAME))[-1], '')

if not ROOT_DIR:
	ROOT_DIR = os.path.dirname(os.getcwd())

"""
# Directory
DATA_DIR= "%s/data/"%ROOT_DIR
DATA_ORIGINAL = "%s/original_data/"%DATA_DIR
DATA_CLEAN = "%s/clean_data/"%DATA_DIR
"""

# Path for scripts
DATA_ORIGINAL_MACHINES = os.path.join(ROOT_DIR, 'data/original_data/machines/')
DATA_ORIGINAL_PATIENT = os.path.join(ROOT_DIR, 'data/original_data/patient-donor/')
DATA_CLEAN = os.path.join(ROOT_DIR, 'data/clean_data/')
DATA_MODEL = os.path.join(ROOT_DIR, 'data/clean_data/model/')

##############################
####	  VARIABLES
##############################

FILE_NAME_PATTERN = {
	'machines': 'Bloc*.xls',
	'patient-donor': 'base*.xlsx'
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
