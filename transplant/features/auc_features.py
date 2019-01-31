import pandas as pd
import numpy as np


def get_feature_split_name(type_split, feature_name):
    """
    Transforme feature name based on type_split
    If type_split = 'post' then feature will be
    'FEATURE_NAME_post'
    Input :
        - type_split [str] : "pre" or post
        - feature_name [str] : original feature name
    Ouput :
        New feature name [str]
    """
    if type_split == 'pre':
        return feature_name+"_pre"
    elif type_split == 'post':
        return feature_name+"_post"
    else:
        raise("Error, type_split must be 'pre' or 'post'")


def calcul_mean_baseline_patient(baseline_data_df, id_patient,
                                 original_feature_name):
    """

    """
    temp_baseline_df = \
        baseline_data_df[baseline_data_df['id_patient'] == id_patient]
    median_baseline = temp_baseline_df[original_feature_name].median()
    return median_baseline


def get_auc_feature(df, df_static, baseline_data_df,
                    feature_name, init_feature_name, normalize=True):
    """
    Calcul Area Under the Curve of a feature for each patient
    If this features is not in init (static's data)
    we calcul the median based on baseline_data_df (before operation)
    Input :
        - df [DataFrame] : post or pre DataFrame used in splitter.py
        - df_static [DataFrame] : static's data
        - baseline_data_df :[DataFrame] : From get_baseline_patient_data()
        - feature_name [str] : Original feature's name
        - init_feature_name [str] : Init feature's name (form static's data)
        - normalize [bool] : Normalize AUC by duration on the DataFrame (len)
                             Default = True.
    Output :
        - [DataFrame] with 2 column :
            - id_patient (to merge with other DataFrame)
            - AUC feature called : feature
    """
    data_list = []
    for patient in df['id_patient'].unique():
        temp = df[df.id_patient == patient][feature_name]

        # If init feature exist in static's data
        if init_feature_name in df_static.columns:
            init_feature = \
                df_static[df_static.id_patient == patient][init_feature_name].values[0]

            # If non init feature in static's data
            # taking median of baseline_patient data on
            # this feature
            if np.isnan(init_feature):
                # Calcul AUC base on baseline operation
                init_feature = \
                    calcul_mean_baseline_patient(baseline_data_df,
                                                 patient,
                                                 feature_name.split('_')[0])
        # If no init feature, we take median of baseline patient operation
        else:
            init_feature = \
                calcul_mean_baseline_patient(baseline_data_df,
                                             patient,
                                             feature_name.split('_')[0])

        baseline_patient = [init_feature] * len(temp)
        auc = np.trapz(temp) - np.trapz(baseline_patient)

        # Normaliza AUC by duration
        if normalize:
            auc = auc/len(temp)

        data_list.append({'id_patient': patient,
                          feature_name+'_auc': auc})

    auc_df = pd.DataFrame(data_list)
    return auc_df


def run_auc_feature(df, baseline_data_df, df_static,
                    SPLITTER_AUC_FEATURE, type_split,
                    normalize=True):
    """
    Cacul AUC features
    Input :
        - df [DataFrame] : post or pre dataframe from splitter.py
        - baseline_data_df [DataFrame] : from splitter.get_baseline_patient_data()
        - df_static [DataFrame] : static's data
        - SPLITTER_AUC_FEATURE [DICT] : from  from splitter_config.py
        - type_split [str] : 'pre' or 'post'
        - normalize [bool] : Normalize AUC by duration on the DataFrame (len)
                             Default = True.
    Ouput :
        - [DataFrame] with id_patient and auc features

    """

    # Create DataFrame with id_patient
    agg_data = pd.DataFrame(df['id_patient'].unique(), columns=['id_patient'])

    for init_feature in SPLITTER_AUC_FEATURE.keys():
        # Check feature's name
        # If feature have no inital feature in static's data
        if init_feature.startswith("dynamic_"):
            feature_name = SPLITTER_AUC_FEATURE[init_feature]+"_"+type_split
            init_feature = feature_name.split('_')[0]
        # feature have inital feature in static's data
        else:
            feature_name = \
                get_feature_split_name(type_split=type_split,
                                       feature_name=SPLITTER_AUC_FEATURE[init_feature])

        temp_auc = get_auc_feature(df, df_static, baseline_data_df,
                                   feature_name,  # FC_post / FC_pre
                                   init_feature,  # Fc_initiale / ETCO2
                                   normalize=normalize)
        agg_data = agg_data.merge(temp_auc, on='id_patient', how='left')
    return agg_data
