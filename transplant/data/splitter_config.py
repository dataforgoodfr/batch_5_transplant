SPLITTER_PRE_FEATURES = ['id_patient', 'B.I.S', 'BIS SR', 'DC', 'ETCO2', 'FC',
                         'FR', 'FiO2', 'PAPdia', 'PAPmoy', 'PAPsys', 'PASd',
                         'PASm', 'PASs', 'PEEPtotal', 'PNId', 'PNIm', 'PNIs',
                         'Pmax', 'Pmean', 'SpO2', 'SvO2 (m)', 'Temp', 'VT']

SPLITTER_POST_FEATURES = ['id_patient', 'B.I.S', 'BIS SR', 'DC', 'ETCO2', 'FC',
                          'FR', 'FiO2', 'PAPdia', 'PAPmoy', 'PAPsys', 'PASd',
                          'PASm', 'PASs', 'PEEPtotal', 'PNId', 'PNIm', 'PNIs',
                          'Pmax', 'Pmean', 'SpO2', 'SvO2 (m)', 'Temp', 'VT']

# Static data 'initial' to dynamic data
# Based on operation block input
SPLITTER_INIT_FEATURE = {
                         'Fc_initiale': 'FC',
                         'FR_initial': 'FR',
                         'FIO2_initiale': 'FiO2',
                         'PAPM_initiale': 'PAPmoy',  #PAPM_initiale = PASm ou PAPmoy ?
                         'PAPS_initiale': 'PAPsys',
                         'PAPD_initiale': 'PAPdia',
                         'PEEP_initial': 'PEEPtotal',
                         'VT_initial': 'VT'
                         }

# List des valeurs null en init ou dans les dynamiques :
# B.I.S_post_auc     103
# Temp_post_auc        6
# PAPdia_post_auc     21
# PAPmoy_post_auc     21
# PAPsys_post_auc     21
# BIS SR_post_auc    107

# Other dynamic's features with no initial in static's data
SPLITTER_DYNA_FEATURE_LIST = ['ETCO2',
                              # 'PAPS',
                              'Temp', 'B.I.S', 'BIS SR',
                              'SpO2_by_FiO2',
                              # 'PNIs'
                              # 'SpO2'
                              ]

# Create a dict automatically based on SPLITTER_DYNA_FEATURE_LIST
SPLITTER_DYNA_FEATURE = {}
for i in range(0, len(SPLITTER_DYNA_FEATURE_LIST)):
    SPLITTER_DYNA_FEATURE['dynamic_'+str(i)] = SPLITTER_DYNA_FEATURE_LIST[i]

# Create a dict SPLITTER_INIT_FEATURE + SPLITTER_DYNA_FEATURE
SPLITTER_AUC_FEATURE = {}
SPLITTER_AUC_FEATURE.update(SPLITTER_INIT_FEATURE)
SPLITTER_AUC_FEATURE.update(SPLITTER_DYNA_FEATURE)
