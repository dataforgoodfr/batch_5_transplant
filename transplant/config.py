import os

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PATH_DYNAMIC_RAW = ROOT_DIR + '/data/raw/dynamic/'
PATH_DYNAMIC_CLEAN = ROOT_DIR + '/data/clean/dynamic.csv'
PATH_STATIC_RAW = ROOT_DIR + '/data/raw/static/'
PATH_STATIC_CLEAN = ROOT_DIR + '/data/clean/static.csv'

# Dynamic Headers
DYNAMIC_HEADERS = [
    'id_patient', 'time', 'B.I.S', 'BIS SR', 'DC', 'ET Des.', 'ET Sevo.',
    'ETCO2', 'ETCO2 (mmHg)', 'ETO2', 'FC', 'FICO2', 'FICO2 (mmHg)', 'FIN2O',
    'FR', 'FR(ecg)', 'FiO2', 'NMT TOF', 'NMTratio', 'PAPdia', 'PAPmoy',
    'PAPsys', 'PASd', 'PASm', 'PASs', 'PEEPtotal', 'PNId', 'PNIm', 'PNIs',
    'Pmax', 'Pmean', 'Pplat', 'RR(co2)', 'SpO2', 'SvO2 (m)', 'Temp', 'VT'
]

DYNAMIC_CATEGORIES = {
    'neurology': [
        'id_patient', 'time', 'B.I.S', 'BIS SR', 'ET Des.', 'ET Sevo.',
        'NMT TOF', 'NMTratio'],
    'haemodynamic': [
        'id_patient', 'time', 'DC', 'FC', 'PAPdia', 'PAPmoy', 'PAPsys',
        'PASd', 'PASm', 'PASs', 'PNId', 'PNIm', 'PNIs'],
    'respiratory': [
        'id_patient', 'time', 'ETCO2', 'ETCO2 (mmHg)', 'ETO2', 'FICO2',
        'FICO2 (mmHg)', 'FIN2O', 'FiO2', 'FR', 'FR(ecg)', 'MAC', 'PEEPtotal',
        'Pmax', 'Pmean', 'Pplat', 'RR(co2)', 'SpO2', 'SvO2 (m)', 'VT'],
    'temperature': [
        'id_patient', 'time', 'Temp']
}

# Static Headers
STATIC_CATEGORIES = {
    'patient_preoperative': [
        'id_patient', 'date_transplantation', 'heure_arrivee_bloc',
        'pathologie', 'age', 'sexe', 'Poids', 'Taille',
        'other_organ_transplantation', 'super_urgence', 'retransplant',
        'transplanted_twice_during_study_period', 'time_on_waiting_liste',
        'LAS', 'preoperative_ICU', 'preoperative_vasopressor',
        'preoperative_mechanical_ventilation', 'ATCD_medicaux', 'PFO',
        'body_mass_index', 'diabetes', 'preoperative_pulmonary_hypertension',
        'PAPS', 'Insuffisance_renale', 'CMV_receveur', 'plasmapherese',
        'preoperative_ECMO', 'ATCD_chirugicaux', 'thoracic_surgery_history'],
    'patient_intraoperative': [
        'id_patient', 'exvivo', 'Immunosuppresseurs', 'heure_transfert_rea',
        'date_sortie_bloc', 'duree_sejour_bloc', 'Antibioprophylaxie',
        'PB_induction', 'Pb_induction_detail', 'FIO2_initiale', 'pH_initial',
        'PAPS_initiale', 'PA_initiale', 'VT_initial', 'PaCO2_initial',
        'PAPM_initiale', 'Fc_initiale', 'FR_initial', 'PaO2_initial',
        'PAPD_initiale', 'NORAD_initiale', 'PEEP_initial',
        'Bicarbonates_initial', 'NO_initiale', 'Lactate_initial',
        'SvO2_initiale', 'Ic_initial', 'Hb_initial', 'Qc_initiale',
        'Examen_Echographique_initial', 'Problemes_VBP',
        'Problemes_VBP_commentaires', 'premiere_transplantation_cote',
        'Ventilation_Unipulmonaire_Pb', 'FiO2_clampage_cote_1',
        'PH_clampage_cote_1', 'PAPS_clampage_cote_1', 'PA_clampage_cote_1',
        'VT_clampage_cote_1', 'PaCO2_clampage_cote_1', 'PAPM_clampage_cote_1',
        'FC_clampage_cote_1', 'Fr_clampage_cote_1', 'PaO2_clampage_cote_1',
        'PAPD_clampage_cote_1', 'NORAD_clampage_cote_1', 'PEEP_clampage_cote_1',
        'Bicarbonates_clampage_cote_1', 'NO_clampage_cote_1',
        'Evolution_PAP_clampage_cote_1', 'Lactates_clampage_cote_1',
        'SvO2_clampage_cote_1', 'Ic_clampage_cote_1', 'Hb_clampage_cote_1',
        'Qc_clampage_cote_1', 'Examen_Echographique_clampage_cote_1',
        'evenements_clampage_cote_1', 'evenements_clampage_cote_1_commentaires',
        'Heure_declampage_cote1', 'first_lung_ischemic_time',
        'FiO2_declampage_cote1', 'PH_declampage_cote_1',
        'PAPS_declampage_cote_1', 'PA _declampage_cote_1',
        'VT_declampage_cote_1', 'PaCO2_declampage_cote_1',
        'PAPM_declampage_cote_1', 'FC_declampage_cote_1',
        'Fr_declampage_cote_1', 'PaO2_declampage_cote_1',
        'PAPD_declampage_cote_1', 'NORAD_declampage_cote_1',
        'PEEP_declampage_cote_1', 'Bicarbonates_declampage_cote_1',
        'NO_declampage_cote_1', 'Evolution_PAP_declampage_cote_1',
        'SvO2_declampage_cote_1', 'Lactates_declampage_cote_1',
        'Ic_declampage_cote_1', 'Hb_declampage_cote_1', 'Qc_declampage_cote_1',
        'Examen_Echographique_declampage_cote_1',
        'evenements_declampage_cote_1',
        'evenements_declampage_cote_1_commentaires',
        'Saigement_estime_declampage_cote1', 'classification_bullage_1',
        'duree_bullage_1', 'retentissement_ETO_bullage_1',
        'retentissement_ECG_bullage_1', 'retentissement_BIS_bullage_1',
        'Retentissement_hemodynamique_bullage_1',
        'deuxieme_transplantation_cote', 'Ventilation_Unipulmonaire_Pb.1',
        'FiO2_clampage_cote_2', 'PH_clampage_cote_2', 'PAPS_clampage_cote_2',
        'PA_clampage_cote_2', 'VT_clampage_cote_2', 'PaCO2_clampage_cote_2',
        'PAPM_clampage_cote_2', 'FC_clampage_cote_2', 'Fr_clampage_cote_2',
        'PaO2_clampage_cote_2', 'PAPD_clampage_cote_2', 'NORAD_clampage_cote_2',
        'PEEP_clampage_cote_2', 'Bicarbonates_clampage_cote_2',
        'NO_clampage_cote_2', 'Evolution_PAP_clampage_cote_2',
        'Lactates_clampage_cote_2', 'SvO2_clampage_cote_2',
        'Ic_clampage_cote_2', 'Hb_clampage_cote_2', 'Qc_clampage_cote_2',
        'Examen_Echographique_clampage_cote_2', 'evenements_clampage_cote_2',
        'evenements_clampage_cote_2_commentaires', 'Heure_declampage_cote2',
        'second_lung_ischemic_time', 'FiO2_declampage_cote2',
        'PH_declampage_cote_2', 'PAPS_declampage_cote_2',
        'PA _declampage_cote_2', 'VT_declampage_cote_2',
        'PaCO2_declampage_cote_2', 'PAPM_declampage_cote_2',
        'FC_declampage_cote_2', 'Fr_declampage_cote_2',
        'PaO2_declampage_cote_2', 'PAPD_declampage_cote_2',
        'NORAD_declampage_cote_2', 'PEEP_declampage_cote_2',
        'Bicarbonates_declampage_cote_2', 'NO_declampage_cote_2',
        'Evolution_PAP_declampage_cote_2', 'SvO2_declampage_cote_2',
        'Lactates_declampage_cote_2', 'Ic_declampage_cote_2',
        'Hb_declampage_cote_2', 'Qc_declampage_cote_2',
        'Examen_Echographique_declampage_cote_2',
        'evenements_declampage_cote_2',
        'evenements_declampage_cote_2_commentaires',
        'Saigement_estime_declampage_cote2', 'classification_bullage_2',
        'duree_bullage_2', 'retentissement_ETO_bullage_2',
        'retentissement_ECG_bullage_2', 'retentissement_BIS_bullage_2',
        'Retentissement_hemodynamique_bullage_2', 'Problemes_survenus_VBP_2',
        'Problemes_survenus_VBP_2_commentaires', 'postoperative_ECMO',
        'only_intraoperative_ECMO', 'ECMO_during_surgery', 'ECMO_duration',
        'CEC', 'moment_de_pose_ECMO', 'cause_ECMO', 'pulmonary_reduction',
        'adrenaline_perop', 'FiO2_fermeture', 'PH_fermeture', 'PAPS_fermeture',
        'PA_fermeture', 'VT_fermeture', 'PaCO2_fermeture', 'PAPM_fermeture',
        'FC_fermeture', 'Fr_fermeture', 'PaO2_fermeture', 'PAPD_fermeture',
        'NORAD_fermeture', 'PEEP_fermeture', 'Bicarbonates_fermeture',
        'NO_fermeture', 'Evolution_fermeture', 'SvO2_fermeture',
        'Lactates_fermeture', 'Ic_fermeture', 'Hb_fermeture', 'Qc_fermeture',
        'Fibroscopie_fermeture', 'Extubation_commentaire', 'VNI',
        'Analgesie_post_operatoire', 'Peridurale_fermeture', 'PRDC_intraop',
        'CEC.1', 'ECMO', 'FFP_intraop', 'platelets_intraop', 'NO_per_op',
        'NO_dependence', 'cause_NO_dependance', 'adre_end_surgery',
        'nad_end_surgery', 'estimated_blood_loss', 'Fibrinogene_fermeture',
        'Cell_Saver', 'Diurese_fermeture', 'fluid_support',
        'Drains_D_fermeture', 'Drains_G_fermeture', 'Albumine 20% fermeture'],
    'patient_postoperative': [
        'id_patient', 'LOS_first_ventilation', 'LOS_total_ventilation',
        ' immediate_extubation', 'secondary_intubation',
        'time_to_secondary_intubation', 'secondary_ECMO', 'delai_recours_ECMO',
        'Cause_ECMO_secondaire', 'postoperative_vasopressive_support', 'ACFA',
        'PRBC_postop', 'FFP_postop', 'Platelets_postop', 'CVA', 'hemodyalisis',
        'tracheostomy', 'reoperation_for_bleeding', 'bleeding',
        'lower_limb_complication', 'lower_limb_ischemia', 'scarpa_complication',
        'vascular_complications', 'thromboembolic_complication',
        'choc_septique', 'cardiac_arrest_during_surgery', 'LOS_ICU', 'LOS_hosp',
        'in_hospital_mortality', '30_d_survival', 'P_F_H0', 'PGD_H0',
        'P_F_end_surgery', 'PGD_end_surgery', 'time_last_PF', 'PDG_h24',
        'PGD_h48', 'PGD3', 'date_de_deces', 'Survival_days_27_10_2018'],
    'donor': [
        'id_patient', 'CMV_donneur', 'EBV_donneur', 'Age_donor', 'Sex_donor',
        'BMI_donor', 'Poids_donor', 'Taille_donor', 'Donneur_CPT',
        'Tabagisme_donor', 'Aspirations_donor', 'RX_donor', 'PF_donor',
        'oto_score']
}
