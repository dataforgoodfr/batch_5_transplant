import pandas as pd


def calcul_pct_on_pre_post(df, dict_auc_features):
    """
    Calcul percentage change on KPI AUC on pre & post
    declampage (like the evolution between before and after
    declampage).
    Input :
        - df [DataFrame]: your train / test set
        - dict_auc_features [dict]: Dict of all AUC features
            {'FEATURE_NAME_pre_auc : FEATURE_NAME_post_auc'}
    Ouput :
        - df [DataFrame]: with pct auc features called
            FEATURE_NAME__pct_pre_post
    """

    for pre_auc_feature in dict_auc_features.keys():
        original_feature_name = pre_auc_feature.split('_pre_auc')[0]
        new_feature_name = original_feature_name+"_pct_pre_post"
        df[new_feature_name] = \
            (df[dict_auc_features[pre_auc_feature]] - df[pre_auc_feature]) /\
            df[pre_auc_feature] * 100
    return df


def get_auc_dict_features(df):
    """
    Return a dict of all pre AUC feature and their post AUC features
    Input :
        - df [DataFrame]: your train / test set
    return :
        - dict_auc_features [dict]: Dict of all AUC features
            {'FEATURE_NAME_pre_auc : FEATURE_NAME_post_auc'}

    """
    pre_AUC_features = \
        [col for col in df.columns if col.endswith("_pre_auc")]
    post_AUC_features = \
        [col for col in df.columns if col.endswith("_post_auc")]

    dict_auc_features = {}
    for pre_feature in pre_AUC_features:
        for post_feature in post_AUC_features:
            if pre_feature.split("_pre_auc")[0] == \
                    post_feature.split("_post_auc")[0]:
                dict_auc_features[pre_feature] = post_feature

    return dict_auc_features


def get_len_of_windows_by_patient(df_window, df, type_split):
    """
    Count number of row (minute) of windows operation
    (pre & post declampage) by patient
    Input :
        - df_window [DataFrame]: pre or post dataframe
        - df [DataFrame]: Your train or test set
        - type_split [str]: for your new feature duration_TYPE_SPLIT
            (pre or post)
    """

    # Count number of row by patient
    grp_windows_by_patient = \
        df_window.groupby('id_patient',
                          as_index=False)['time'].count()
    grp_windows_by_patient.columns = ['id_patient', 'duration_'+type_split]
    df = df.merge(grp_windows_by_patient, on='id_patient', how='left')
    return df


def create_nb_nan(df, advanced_features_list):
    """
    Calcul for each patient number of variable missing (NaN)
    Input :
        - df [DataFrame]
        - advanced_features_list [list] - list of features
            create by advanced_features.py
    Ouput :
        - df [DataFrame] with count_NaN feature
        - advanced_features_list [list] - list of features
            create by advanced_features.py + count_NaN
    """

    df['count_NaN'] = pd.isnull(df).sum(axis=1)
    advanced_features_list.append('count_NaN')
    return df, advanced_features_list


def make_advanced_feature(df):
    """
    Function to build advanced features (previous functions)
    Input :
        - df [dataFrame]: to get dynamic's data
    Ouput :
        - df [dataFrame] with all advanced features
            and 'id_patient' to make a merge
    """

    advanced_features_list = []

    # count_NaN
    df, advanced_features_list = \
        create_nb_nan(df.copy(), advanced_features_list)

    advanced_features_list.append('id_patient')

    return df[advanced_features_list]
