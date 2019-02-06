import pandas as pd


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
