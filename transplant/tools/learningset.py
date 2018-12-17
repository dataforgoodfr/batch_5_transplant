import pandas as pd
import numpy as np

from transplant.tools.dataset import Dataset
dataset=Dataset()

class Learningset:


    def get_static_filled(self):
        # Function that return the train and test set of the static data where :
        # - We transformed the string into numbers
        # - We drop the columns with just Nan
        # - We replace the remaning Nan with the train column mean
        # - We make sure we got the same columns for the train and the test set
        from transplant.tools.dataset import Dataset
        train_static_0, test_static_0 = Dataset().get_static()

        train_static_str_to_num = train_static_0.apply(
            pd.to_numeric, errors='coerce').dropna(1, how="all")

        mean_train_static = train_static_str_to_num.mean()

        train_static_filled = train_static_str_to_num.fillna(mean_train_static)
        test_static_filled = test_static_0.apply(
            pd.to_numeric, errors='coerce').dropna(1, how="all").fillna(mean_train_static)

        # Same columns
        drop_test = []
        drop_train = []
        train_static_columns = train_static_filled.columns
        test_static_columns = test_static_filled.columns

        for i in train_static_filled.columns:
            if not(i in test_static_columns):
                drop_train += [i]

        for i in test_static_columns:
            if not(i in train_static_filled.columns):
                drop_test += [i]

        train_static_filled = train_static_filled.drop(drop_train, axis=1)
        test_static_filled = test_static_filled.drop(drop_test, axis=1)

        return train_static_filled, test_static_filled


    def get_data_merged_dynamic_flatten(self, target_format="cls", centered_reduced=False):
        # To have more explanation about this preparation see the notebook called "Data Preparation for our studies"
        print(
            "Static merged with Flattent Dynamic (i.e. : took the mean for each time serie).")
        print(
            "You can chose between One_Hot encoding ([0,1] , [1,0]) with 'One_Hot' for target data or not with 'cls'.")
        print("You can chose to center and reduce your data with the train set data with 'True'")

        from transplant.tools.learningset import Learningset
        learningset = Learningset()

        train_static,test_static = learningset.get_static_filled()

        #Dynamic (flatten)
        train_dynamic_0, test_dynamic_0 = dataset.get_dynamic()

        mean_dynamic_train = train_dynamic_0.groupby(
            ['id_patient']).mean().mean()

        train_dynamic = train_dynamic_0.fillna(mean_dynamic_train)
        test_dynamic = test_dynamic_0.fillna(mean_dynamic_train)

        train_dynamic_flat = train_dynamic.groupby(
            ['id_patient'], as_index=False).mean()
        test_dynamic_flat = test_dynamic.groupby(
            ['id_patient'], as_index=False).mean()

        # Merging
        def merge_dyn_sta(X_train_static, X_train_dynamic, X_test_static, X_test_dynamic):
            return pd.merge(X_train_static, X_train_dynamic, on='id_patient'), pd.merge(X_test_static, X_test_dynamic, on='id_patient')
        train_glob, test_glob = merge_dyn_sta(
            train_static, train_dynamic_flat, test_static, test_dynamic_flat)

        # Centering and Reducing if needed

        def center_reduce_data(W_train, W_test):
            mean_train = W_train.mean()
            std_train = W_test.std()

            return (W_train-mean_train)/std_train, (W_test-mean_train)/std_train

        dic_to_One_Hot = {0: [1, 0], 1: [0, 1]}

        y_train_cls = np.array(train_glob['target'])
        y_train_hot = np.array(list(train_glob['target'].map(dic_to_One_Hot)))

        y_test_cls = np.array(test_glob['target'])
        y_test_hot = np.array(list(test_glob['target'].map(dic_to_One_Hot)))

        if centered_reduced:
            X_train, X_test = center_reduce_data(train_glob.drop(
                ['target'], axis=1), test_glob.drop(['target'], axis=1))

            X_train = np.array(X_train)
            X_test = np.array(X_test)

        else:
            X_train = np.array(train_glob.drop(['target'], axis=1))
            X_test = np.array(test_glob.drop(['target'], axis=1))

        # Return
        if target_format == "cls":
            return X_train, X_test, y_train_cls, y_test_cls, train_glob.drop(['target'], axis=1).columns

        if target_format == "One_Hot":
            return X_train, X_test, y_train_hot, y_test_hot, train_glob.drop(['target'], axis=1).columns
        

    def get_data_merged_dynamic_flatten_desc(self, target_format="cls", centered_reduced=False):
        
     
        from transplant.tools.learningset import Learningset
        learningset = Learningset()

        train_static,test_static = learningset.get_static_filled()

        #Dynamic (flatten)
        train_dynamic_0, test_dynamic_0 = dataset.get_dynamic()

        mean_dynamic_train = train_dynamic_0.groupby(
            ['id_patient']).mean().mean()

        train_dynamic = train_dynamic_0.fillna(mean_dynamic_train)
        test_dynamic = test_dynamic_0.fillna(mean_dynamic_train)

        train_dynamic_flat = train_dynamic.groupby(
            ['id_patient'], as_index=False).mean()
        test_dynamic_flat = test_dynamic.groupby(
            ['id_patient'], as_index=False).mean()

        # Merging
        def merge_dyn_sta(X_train_static, X_train_dynamic, X_test_static, X_test_dynamic):
            return pd.merge(X_train_static, X_train_dynamic, on='id_patient'), pd.merge(X_test_static, X_test_dynamic, on='id_patient')
        train_glob, test_glob = merge_dyn_sta(
            train_static, train_dynamic_flat, test_static, test_dynamic_flat)

        # Centering and Reducing if needed

        def center_reduce_data(W_train, W_test):
            mean_train = W_train.mean()
            std_train = W_test.std()

            return (W_train-mean_train)/std_train, (W_test-mean_train)/std_train

        dic_to_One_Hot = {0: [1, 0], 1: [0, 1]}

        y_train_cls = np.array(train_glob['target'])
        y_train_hot = np.array(list(train_glob['target'].map(dic_to_One_Hot)))

        y_test_cls = np.array(test_glob['target'])
        y_test_hot = np.array(list(test_glob['target'].map(dic_to_One_Hot)))

        if centered_reduced:
            X_train, X_test = center_reduce_data(train_glob.drop(
                ['target'], axis=1), test_glob.drop(['target'], axis=1))

            X_train = np.array(X_train)
            X_test = np.array(X_test)

        else:
            X_train = np.array(train_glob.drop(['target'], axis=1))
            X_test = np.array(test_glob.drop(['target'], axis=1))

        # Return
        if target_format == "cls":
            return X_train, X_test, y_train_cls, y_test_cls, train_glob.drop(['target'], axis=1).columns

        if target_format == "One_Hot":
            return X_train, X_test, y_train_hot, y_test_hot, train_glob.drop(['target'], axis=1).columns



    def get_data_merged_dynamic(self, target_format="cls"):


        from transplant.tools.learningset import Learningset
        learningset = Learningset()
        train_static_0, test_static_0 = learningset.get_static_filled()

        train_dynamic_0, test_dynamic_0 = dataset.get_dynamic()

        mean_dynamic_train = train_dynamic_0.groupby(['id_patient']).mean().mean()
        
        train_dynamic_0 = train_dynamic_0.fillna(mean_dynamic_train)
        test_dynamic_0 = test_dynamic_0.fillna(mean_dynamic_train)

        def add_start_end_length_op_to_static(X_stat, X_dyn):
            grouped_time = X_dyn.groupby(['id_patient'])['time']

            time_start_df = grouped_time.first().to_frame()
            time_start_df.columns = ['start_operation']
            time_start_df['id_patient'] = time_start_df.index

            X_return = pd.merge(X_stat, time_start_df, on='id_patient')

            time_ends_df = grouped_time.last().to_frame()
            time_ends_df.columns = ['ends_operation']
            time_ends_df['id_patient'] = time_ends_df.index

            X_return = pd.merge(X_return, time_ends_df, on='id_patient')

            X_return['length_op'] = X_return['ends_operation'] - X_return['start_operation']

            return X_return

        train_static_1 = add_start_end_length_op_to_static(train_static_0, train_dynamic_0)
        test_static_1 = add_start_end_length_op_to_static(test_static_0, test_dynamic_0)

        def get_timeseries_in_array(X_stat, X_dyn, dyn_to_drop=['id_patient', 'time']):

            X_return = X_stat

            grouped = X_dyn.groupby(['id_patient'])

            list_time_serie_col = X_dyn.drop(dyn_to_drop, axis=1).columns

            for i in list_time_serie_col:
                df_muette = grouped[i].apply(np.array).to_frame()
                df_muette['id_patient'] = df_muette.index
                X_return = pd.merge(X_return, df_muette, on='id_patient')

            return X_return
            


        train_glob = get_timeseries_in_array(train_static_1, train_dynamic_0)
        test_glob = get_timeseries_in_array(test_static_1, test_dynamic_0)
        



        dic_to_One_Hot = {0: [1, 0], 1: [0, 1]}

        y_train_cls = np.array(train_glob['target'])
        y_train_hot = np.array(list(train_glob['target'].map(dic_to_One_Hot)))

        y_test_cls = np.array(test_glob['target'])
        y_test_hot = np.array(list(test_glob['target'].map(dic_to_One_Hot)))


        X_train = np.array(train_glob.drop(['target'], axis=1))
        X_test = np.array(test_glob.drop(['target'], axis=1))

        # Return
        if target_format == "cls":
            return X_train, X_test, y_train_cls, y_test_cls, train_glob.drop(['target'], axis=1).columns

        if target_format == "One_Hot":
            return X_train, X_test, y_train_hot, y_test_hot, train_glob.drop(['target'], axis=1).columns