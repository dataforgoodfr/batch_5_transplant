import pandas as pd
import numpy as np

from transplant.data.dataset import Dataset
from transplant.features.auc_features import run_auc_feature
from transplant.data.splitter_config import SPLITTER_AUC_FEATURE
from transplant.data.splitter import make_split_operation
from transplant.features.advanced_features import (make_advanced_feature,
                                                   get_len_of_windows_by_patient,
                                                   get_auc_dict_features,
                                                   calcul_pct_on_pre_post)

dataset = Dataset()

# Usefull functions


def merge_dyn_sta(X_train_static, X_train_dynamic, X_test_static,
                  X_test_dynamic):
    """
    Used to merge static and dynamic data (after having been flatten)
    """

    train_glob_0 = pd.merge(X_train_static, X_train_dynamic, on='id_patient')
    test_glob_0 = pd.merge(X_test_static, X_test_dynamic, on='id_patient')
    return train_glob_0, test_glob_0


def center_reduce_data(W_train, W_test):
    """
    Center and reduce the data
    """
    mean_train = W_train.mean()
    std_train = W_train.std()

    return (W_train-mean_train)/std_train, (W_test-mean_train)/std_train


def add_start_end_length_op_to_static(X_stat, X_dyn):
    """
    Add some information about the length and the date of the operations
    """
    # X_dyn.index.names=['index',None] #Parfois ne semblait pas marcher à
    # cause du format "grouped_by"
    # X_stat.index.names=['index']

    grouped_time = X_dyn.groupby(['id_patient'])['time']

    time_start_df = grouped_time.first().to_frame()
    time_start_df.columns = ['start_operation']
    # time_start_df['id_patient'] = time_start_df.index

    X_return = pd.merge(X_stat, time_start_df,
                        on='id_patient', right_index=True)

    time_ends_df = grouped_time.last().to_frame()
    time_ends_df.columns = ['ends_operation']
    # time_ends_df['id_patient'] = time_ends_df.index

    X_return = pd.merge(X_return, time_ends_df,
                        on='id_patient', right_index=True)

    X_return['length_op'] = \
        (X_return['ends_operation'] -
            X_return['start_operation']).apply(lambda x: x.seconds//60)

    X_return['start_operation_year'] = \
        X_return['start_operation'].apply(lambda x: x.year)
    X_return['start_operation_month'] = \
        X_return['start_operation'].apply(lambda x: x.month)
    X_return['start_operation_day'] = \
        X_return['start_operation'].apply(lambda x: x.dayofyear)

    X_return['ends_operation_year'] = \
        X_return['ends_operation'].apply(lambda x: x.year)
    X_return['ends_operation_month'] = \
        X_return['ends_operation'].apply(lambda x: x.month)
    X_return['ends_operation_day'] = \
        X_return['ends_operation'].apply(lambda x: x.dayofyear)

    return X_return.drop(['ends_operation', 'start_operation'], axis=1)


def get_timeseries_in_array(X_stat, X_dyn, dyn_to_drop=['id_patient', 'time']):
    """
    Merges Static and Dynamic (where we get the full time series)
    """

    X_return = X_stat

    grouped = X_dyn.groupby(['id_patient'])

    list_time_serie_col = X_dyn.drop(dyn_to_drop, axis=1).columns

    for i in list_time_serie_col:
        df_muette = grouped[i].apply(np.array).to_frame()
        df_muette['id_patient'] = df_muette.index
        df_muette.index.names = ['index']
        X_return = pd.merge(X_return, df_muette, on='id_patient')

    return X_return


def get_auc_features(train_glob_0, test_glob_0, fillna_auc):
        """
        Add advanced features on dynamic's data
        Split dynamic's data into 3 DataFrame (splitter)
        Calcul AUC features
        Merge AUC features with train_glob_0 & test_glob_0
        Count number of minute of windows operation by patient
            (get_len_of_windows_by_patient())
        Input :
            - train_glob_0 [DataFrame]: trainning dynamic's data
            - test_glob_0 [DataFrame]: trainning dynamic's data
            - fillna_auc [bool]: If True then fillna auc features
        Ouput :
            - train_glob_0 [DataFrame]: trainning dynamic's & AUC
            - test_glob_0 [DataFrame]: trainning dynamic's & AUC
        """

        # Dynamic's data
        train_dyna, test_dyna = dataset.get_dynamic()
        dynamic_df = pd.concat([train_dyna, test_dyna])

        # Static's data
        train_stat, test_stat = dataset.get_static()
        static_df = pd.concat([train_stat, test_stat])

        # Create 3 DataFrames with splitters. You can change config
        # duration of each DataFrames with arguments
        baseline_data_df, pre_declampage_df, post_declampage_df = \
            make_split_operation(dynamic_df, baseline_duration=90,
                                 pre_duration=90,
                                 post_chir_duration=20)

        # AUC cacul from transplant/features/auc_features.py
        post_auc_feature = run_auc_feature(post_declampage_df,
                                           baseline_data_df,
                                           static_df, SPLITTER_AUC_FEATURE,
                                           type_split='post', normalize=True)
        pre_auc_feature = run_auc_feature(pre_declampage_df,
                                          baseline_data_df,
                                          static_df, SPLITTER_AUC_FEATURE,
                                          type_split='pre', normalize=True)
        # To fill NaN value with 0
        if fillna_auc:
            post_auc_feature.fillna(0, inplace=True)
            pre_auc_feature.fillna(0, inplace=True)

        # Merging result with learningset train & test
        train_glob_0 = train_glob_0.merge(post_auc_feature, on='id_patient')
        train_glob_0 = train_glob_0.merge(pre_auc_feature, on='id_patient')

        test_glob_0 = test_glob_0.merge(post_auc_feature, on='id_patient')
        test_glob_0 = test_glob_0.merge(pre_auc_feature, on='id_patient')

        # Get duration of windows operation by patient
        train_glob_0 = get_len_of_windows_by_patient(post_declampage_df,
                                                     train_glob_0,
                                                     type_split='post')
        train_glob_0 = get_len_of_windows_by_patient(pre_declampage_df,
                                                     train_glob_0,
                                                     type_split='pre')
        test_glob_0 = get_len_of_windows_by_patient(post_declampage_df,
                                                    test_glob_0,
                                                    type_split='post')
        test_glob_0 = get_len_of_windows_by_patient(pre_declampage_df,
                                                    test_glob_0,
                                                    type_split='pre')

        return train_glob_0, test_glob_0


def get_advanced_features(train_glob_0, test_glob_0):
    """
    Call make_advanced_feature form features.advanced_features.py

    Add advanced features to dynamic's data
    Input :
        - train_glob_0 [DataFrame] trainning
        - test_glob_0 [DataFrame] test
    Ouput :
        - train_glob_0 [DataFrame] with advanced features
        - test_glob_0 [DataFrame] with advanced features
    """

    train_glob_0_adv = make_advanced_feature(train_glob_0)
    test_glob_0_adv = make_advanced_feature(test_glob_0)

    train_glob_0 = train_glob_0.merge(train_glob_0_adv, on='id_patient')
    test_glob_0 = test_glob_0.merge(test_glob_0_adv, on='id_patient')

    return train_glob_0, test_glob_0


class Learningset:

    # get_static_filled
    def get_static_filled(self):
        # Function that return the train and test set of the static data where:
        # - We transformed the string into numbers
        # - We drop the columns with just Nan
        # - We replace the remaning Nan with the train column mean
        # - We make sure we got the same columns for the train and the test set
        from transplant.data.dataset import Dataset
        train_static_0, test_static_0 = Dataset().get_static()

        # string in numbers and drop if full of Nan
        train_static_str_to_num = train_static_0.apply(
            pd.to_numeric, errors='coerce').dropna(1, how="all")

        # get mean of train to fill empty values in train and test
        mean_train_static = train_static_str_to_num.mean()

        train_static_filled = train_static_str_to_num.fillna(mean_train_static)

        # drop strings and fill Nan
        # in test by mean in train
        test_static_filled = test_static_0.apply(
            pd.to_numeric,
            errors='coerce').dropna(1, how="all").fillna(mean_train_static)

        # Same columns
        drop_test = []
        drop_train = []
        train_static_columns = train_static_filled.columns
        test_static_columns = test_static_filled.columns

        for i in train_static_filled.columns:
            if not(i in test_static_columns):
                drop_train += [i]

        for i in test_static_columns:
            if not(i in train_static_columns):
                drop_test += [i]

        train_static_filled = train_static_filled.drop(drop_train, axis=1)
        test_static_filled = test_static_filled.drop(drop_test, axis=1)

        return train_static_filled, test_static_filled

    def get_data_merged_dynamic_flatten_full(self, target_format="cls",
                                             centered_reduced=False,
                                             fillna_original=False,
                                             fillna_auc=False,
                                             full_df=False):
        """
        get_data_merged_dynamic_flatten_full
        """

        from transplant.data.learningset import Learningset
        learningset = Learningset()

        # On prend les statics utilisables pour ML
        train_static_0, test_static_0 = learningset.get_static_filled()
        train_dynamic_0, test_dynamic_0 = dataset.get_dynamic()

        if fillna_original:
            # On remplace les Nan par des 0 dans dynamic
            train_dynamic_0 = train_dynamic_0.fillna(0)
            test_dynamic_0 = test_dynamic_0.fillna(0)

        # On obtient entre autre la longueur de l'opération
        train_static_1 = add_start_end_length_op_to_static(train_static_0,
                                                           train_dynamic_0)
        test_static_1 = add_start_end_length_op_to_static(test_static_0,
                                                          test_dynamic_0)

        # Les fonctions qu'on applique sur les séries temporelle
        liste_func = [np.mean, np.std, np.amax, np.amin]
        liste_func_name = ['mean', 'std', 'max', 'min']

        train_glob_0, test_glob_0 = train_static_1, test_static_1

        for i in range(len(liste_func)):
            func = liste_func[i]
            # On enregistre les groupes
            train_grouped = \
                train_dynamic_0.drop(['time'],
                                     axis=1).groupby(['id_patient'],
                                                     as_index=False)
            test_grouped = \
                test_dynamic_0.drop(['time'],
                                    axis=1).groupby(['id_patient'],
                                                    as_index=False)
            # On conserve le id du patient
            train_id = train_grouped['id_patient'].apply(np.mean)
            test_id = test_grouped['id_patient'].apply(np.mean)

            # On applique la fonction
            train_dynamic_flat = train_grouped.apply(func)
            test_dynamic_flat = test_grouped.apply(func)

            train_dynamic_flat.rename(columns=lambda x:
                                      x+'_'+liste_func_name[i]
                                      if x != 'id_patient' else x,
                                      inplace=True)
            test_dynamic_flat.rename(columns=lambda x:
                                     x+'_'+liste_func_name[i]
                                     if x != 'id_patient' else x,
                                     inplace=True)

            train_dynamic_flat['id_patient'] = train_id
            test_dynamic_flat['id_patient'] = test_id

            train_glob_0, test_glob_0 = merge_dyn_sta(train_glob_0,
                                                      train_dynamic_flat,
                                                      test_glob_0,
                                                      test_dynamic_flat)

        # Get Advanced Features
        train_glob_0, test_glob_0 = \
            get_advanced_features(train_glob_0, test_glob_0)

        # Get AUC Features
        train_glob_0, test_glob_0 = \
            get_auc_features(train_glob_0, test_glob_0, fillna_auc)

        # Pct on AUC Features
        # All AUC features in dict
        dict_auc_features = get_auc_dict_features(train_glob_0)
        train_glob_0 = calcul_pct_on_pre_post(train_glob_0,
                                              dict_auc_features)
        test_glob_0 = calcul_pct_on_pre_post(test_glob_0,
                                             dict_auc_features)

        if full_df:
            return train_glob_0, test_glob_0

        dic_to_One_Hot = {0: [1, 0], 1: [0, 1]}

        y_train_cls = np.array(train_glob_0['target'])
        y_train_hot = \
            np.array(list(train_glob_0['target'].map(dic_to_One_Hot)))

        y_test_cls = np.array(test_glob_0['target'])
        y_test_hot = np.array(list(test_glob_0['target'].map(dic_to_One_Hot)))

        if centered_reduced:
            X_train, X_test = center_reduce_data(train_glob_0.drop(['target'],
                                                                   axis=1),
                                                 test_glob_0.drop(['target'],
                                                                  axis=1))
            X_train = np.array(X_train)
            X_test = np.array(X_test)

        else:
            X_train = np.array(train_glob_0.drop(['target'], axis=1))
            X_test = np.array(test_glob_0.drop(['target'], axis=1))

        # Return
        if target_format == "cls":
            return X_train, X_test, \
                   y_train_cls, y_test_cls, \
                   train_glob_0.drop(['target'], axis=1).columns

        if target_format == "One_Hot":
            return X_train, X_test, \
                   y_train_hot, y_test_hot, \
                   train_glob_0.drop(['target'], axis=1).columns

    def get_data_merged_dynamic(self, target_format="cls",
                                fillna_auc=False,
                                full_df=False):
        """
        get_data_merged_dynamic
        """
        from transplant.data.learningset import Learningset
        learningset = Learningset()

        train_static_0, test_static_0 = learningset.get_static_filled()
        train_dynamic_0, test_dynamic_0 = dataset.get_dynamic()

        # Fill Nan with mean
        mean_dynamic_train = \
            train_dynamic_0.groupby(['id_patient']).mean().mean()
        train_dynamic_0 = train_dynamic_0.fillna(mean_dynamic_train)
        test_dynamic_0 = test_dynamic_0.fillna(mean_dynamic_train)

        # Obtain length operation
        train_static_1 = add_start_end_length_op_to_static(train_static_0,
                                                           train_dynamic_0)
        test_static_1 = add_start_end_length_op_to_static(test_static_0,
                                                          test_dynamic_0)

        # Merge static and dynamic with full time series
        train_glob = get_timeseries_in_array(train_static_1, train_dynamic_0)
        test_glob = get_timeseries_in_array(test_static_1, test_dynamic_0)

        # Get Advanced Features
        train_glob, test_glob = \
            get_advanced_features(train_glob, test_glob)

        # Get AUC Features
        train_glob, test_glob = \
            get_auc_features(train_glob, test_glob, fillna_auc)

        if full_df:
            return train_glob, test_glob

        dic_to_One_Hot = {0: [1, 0], 1: [0, 1]}

        y_train_cls = np.array(train_glob['target'])
        y_train_hot = np.array(list(train_glob['target'].map(dic_to_One_Hot)))

        y_test_cls = np.array(test_glob['target'])
        y_test_hot = np.array(list(test_glob['target'].map(dic_to_One_Hot)))

        X_train = np.array(train_glob.drop(['target'], axis=1))
        X_test = np.array(test_glob.drop(['target'], axis=1))

        # Return
        if target_format == "cls":
            return X_train, X_test, y_train_cls, \
                   y_test_cls, train_glob.drop(['target'], axis=1).columns

        if target_format == "One_Hot":
            return X_train, X_test, y_train_hot, \
                   y_test_hot, train_glob.drop(['target'], axis=1).columns
