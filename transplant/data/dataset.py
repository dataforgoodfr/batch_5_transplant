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

        # Only filter columns in Dynamic Header, see https://github.com/dataforgoodfr/batch_5_transplant/issues/42

        df = df[DYNAMIC_HEADERS]

        # create bool event on declampage
        df = self._get_declampage_event(df)

        # Truncate dynamic file to time_offset before end of operation

        df = df.groupby('id_patient').apply(self._truncate_datetime)

        # Filter result based on static set

        train, test = self.get_static()
        train_dynamic = df[df.id_patient.isin(train['id_patient'])]
        test_dynamic = df[df.id_patient.isin(test['id_patient'])]

        return train_dynamic, test_dynamic

    def _split_data(self, df):

        train_df, test_df = train_test_split(df,
                                             stratify=df['target'],
                                             test_size=0.3,
                                             random_state=self._random_state)

        test_df = self._drop_target_column(test_df)

        return train_df, test_df

    def _drop_target_column(self, df):
        return df.drop(['target'], axis=1)

    def _truncate_datetime(self, df):
        date_max = df.time.max() - timedelta(minutes=self.time_offset)
        return df[df.time <= date_max]

    def _get_declampage_event(self, df):
        """
        Create Bool features on event declampage_cote1 & declampage_cote2 from
        Static Dataset

        - Input : df : [DataFrame] : dynmaic DataFrame
        - Ouput : df : [DataFrame] : dynmaic DataFrame + declampage_cote1_done &
                                     declampage_cote2_done
        """

        df_static = pd.read_csv(PATH_STATIC_CLEAN, 
                                usecols=['id_patient', 'Heure_declampage_cote1', 
                                'Heure_declampage_cote2', 'date_transplantation',
                                'heure_arrivee_bloc']
                                )

        # Concat Date + heure begin of operaiton
        df_static['date_debut_operation'] = pd.to_datetime(df_static['date_transplantation'] + 
                                                           ' ' + 
                                                           df_static['heure_arrivee_bloc'])

        # Merging on id_patient
        df = df.merge(df_static, on='id_patient', how='left')

        # Add date to time for declampage_cote
        df['Heure_declampage_cote1'] = pd.to_datetime(df['time'].dt.strftime("%Y-%m-%d") + 
                                                      ' ' + 
                                                      df['Heure_declampage_cote1'])
        df['Heure_declampage_cote2'] = pd.to_datetime(df['time'].dt.strftime("%Y-%m-%d") + 
                                                      ' ' + 
                                                      df['Heure_declampage_cote2'])

        # Create event features
        ## declampage_cote1_done
        df['declampage_cote1_done'] = 0
        df.loc[(df['Heure_declampage_cote1'] <= df['time']) & 
               (df['Heure_declampage_cote1'] > df['date_debut_operation']), 
               'declampage_cote1_done'] = 1

        # Fix declampage_cote1_done to 0 because new day.
        max_date_declampage_1_by_patient = \
            df[df.declampage_cote1_done == 1].groupby('id_patient',
                                                        as_index=False)['time'].max()
        max_date_declampage_1_by_patient.columns = ['id_patient', 'max_date_declampage_1']

        df = df.merge(max_date_declampage_1_by_patient, 
                      on='id_patient', 
                      how='inner')

        df.loc[(df['declampage_cote1_done'] == 0) & 
               (df['time'] > df['max_date_declampage_1']), 
                'declampage_cote1_done'] = 1

        ## declampage_cote2_done
        df['declampage_cote2_done'] = 0
        df.loc[(df['Heure_declampage_cote2'] <= df['time']) &
               (df['Heure_declampage_cote2'] > df['date_debut_operation']), 
               'declampage_cote2_done'] = 1


        # Drop non usefull column
        df.drop(['Heure_declampage_cote1', 'Heure_declampage_cote2', 
                'date_debut_operation', 'date_transplantation', 
                'heure_arrivee_bloc', 'max_date_declampage_1'], 
                axis=1, inplace=True)

        return df
