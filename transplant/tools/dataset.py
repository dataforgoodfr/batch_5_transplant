import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
from sklearn.model_selection import train_test_split

from transplant.config import (PATH_STATIC_CLEAN, PATH_DYNAMIC_CLEAN,
                               STATIC_CATEGORIES, DYNAMIC_CATEGORIES,
                               DYNAMIC_HEADERS)


class Dataset:
    """
    Transform csv patient and donors into a dimension dataset that
    can be used for modeling. Following steps are applied:
    Step 1 - Select a subset of columns
    Step 2 - Build the target variable
    Step 3 - Export data
    """

    _random_state = 1

    def __init__(self, time_offset=30):
        self.time_offset = time_offset

    def get_static(self):

        data = pd.read_csv(PATH_STATIC_CLEAN)

        cols = np.unique(STATIC_CATEGORIES['patient_preoperative'] +
                         STATIC_CATEGORIES['donor'] +
                         STATIC_CATEGORIES['patient_postoperative_filtered'])

        data = data[list(cols)]

        # See https://github.com/dataforgoodfr/batch_5_transplant/blob/master/data/README.md#target

        data['target'] = 0

        # Success A
        idx_successA = (data.immediate_extubation == 1) & \
                       (data.secondary_intubation == 0)

        # Success B
        idx_successB = (data.immediate_extubation == 0) & \
                        (data.secondary_intubation == 0) & \
                        (data.LOS_first_ventilation < 2) & \
                        (data.Survival_days_27_10_2018 >= 2)
        data.loc[idx_successA | idx_successB, 'target'] = 1

        # Drop post_operation variables
        data.drop(STATIC_CATEGORIES['patient_postoperative_filtered'],
                  inplace=True,
                  axis=1)

        return self._split_data(data)

    def get_dynamic(self):

        df = pd.read_csv(PATH_DYNAMIC_CLEAN, parse_dates=['time'])

        # Truncate dynamic file to time_offset before end of operation

        df = df.groupby('id_patient').apply(self._truncate_datetime)

        # Filter result based on static set

        train, test = self.get_static()
        train_dynamic = df[df.id_patient.isin(train['id_patient'])]
        test_dynamic = df[df.id_patient.isin(test['id_patient'])]

        return train_dynamic, test_dynamic

    def _split_data(self, df):

        train_df, test_df = train_test_split(df,
                                             test_size=0.3,
                                             random_state=self._random_state)

        #test_df = self._drop_target_column(test_df)

        return train_df, test_df

    def _drop_target_column(self, df):
        return df.drop(['target'], axis=1)

    def _truncate_datetime(self, df):
        date_max = df.time.max() - timedelta(minutes=self.time_offset)
        return df[df.time <= date_max]

    
    def get_data_pierre(self, target_format="cls"):
        # see notebook called "Data Preparation Once and for All"
        
        
        from transplant.tools.dataset import Dataset 
        dataset = Dataset()
        train_static_0, test_static_0 = dataset.get_static()
        
        #Static 
        
        train_static_str_to_num=train_static_0.apply(pd.to_numeric,errors='coerce').dropna(1, how="all")

        mean_train_static = train_static_str_to_num.mean()

        train_static_filled=train_static_str_to_num.fillna(mean_train_static)
        test_static_filled=test_static_0.apply(pd.to_numeric,errors='coerce').dropna(1, how="all").fillna(mean_train_static)
        
        ##Same columns 
        drop_test=[]
        drop_train=[]
        train_static_columns=train_static_filled.columns
        test_static_columns=test_static_filled.columns

        for i in train_static_filled.columns :
            if not(i in test_static_columns) :
                drop_train+=[i]
        
        for i in test_static_columns :
            if not(i in train_static_filled.columns) :
                drop_test+=[i]
    

        train_static_filled=train_static_filled.drop(drop_train, axis=1)
        test_static_filled=test_static_filled.drop(drop_test, axis=1)


        train_static=train_static_filled
        test_static=test_static_filled
        
        #Dynamic (flatten)
        train_dynamic_0, test_dynamic_0 = dataset.get_dynamic()
        
        mean_dynamic_train=train_dynamic_0.groupby(['id_patient']).mean().mean()
        
        train_dynamic=train_dynamic_0.fillna(mean_dynamic_train)
        test_dynamic=test_dynamic_0.fillna(mean_dynamic_train)
        
        train_dynamic_flat=train_dynamic.groupby(['id_patient'], as_index=False).mean()
        test_dynamic_flat=test_dynamic.groupby(['id_patient'],as_index=False).mean()
        
        #Merging
        def merge_dyn_sta(X_train_static,X_train_dynamic,X_test_static,X_test_dynamic):
            return pd.merge(X_train_static, X_train_dynamic, on='id_patient') , pd.merge(X_test_static, X_test_dynamic, on='id_patient') 
        train_glob, test_glob = merge_dyn_sta(train_static,train_dynamic_flat,test_static,test_dynamic_flat)
    
        dic_to_One_Hot = {0 : [1,0], 1 : [0,1]}
    
        X_train=np.array(train_glob.drop(['target'], axis=1))
        X_test=np.array(test_glob.drop(['target'], axis=1))

        y_train_cls=np.array(train_glob['target']).reshape(-1,1)
        y_train_hot=np.array(list(train_glob['target'].map(dic_to_One_Hot)))

        y_test_cls=np.array(test_glob['target']).reshape(-1,1)
        y_test_hot=np.array(list(test_glob['target'].map(dic_to_One_Hot)))
        
        
        #Return
        if target_format=="cls" :
            return X_train, X_test, y_train_cls , y_test_cls , train_glob.drop(['target'], axis=1).columns
        
        if target_format=="One_Hot" :
            return X_train,X_test,y_train_hot , y_test_hot , train_glob.drop(['target'], axis=1).columns

        print("Static merged with Flattent Dynamic, you can chose between One_Hot encoding ([0,1] , [1,0]) for target data or not.")
    
    