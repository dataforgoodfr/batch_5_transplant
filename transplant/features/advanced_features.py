import pandas as pd


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
