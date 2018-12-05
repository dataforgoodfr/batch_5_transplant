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

    test = False
    train = False
    time_offset = 30
    smooth_dynamic = False
    q_high = 0.95  # Upper quantile to filter
    q_low = 0.05   # Lower quantile to filter outliers

    _random_state = 1

    def __init__(self, test=False, train=False, time_offset=30):
        self.test = test
        self.train = train
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
        idx_successA = (data.immediate_extubation == 1) &
                        (data.secondary_intubation == 0)

        # Success B
        idx_successB = (data.immediate_extubation == 0) &
                        (data.secondary_intubation == 0) &
                        (data.LOS_first_ventilation < 2) &
                        (data.Survival_days_27_10_2018 >= 2)
        data.loc[idx_successA | idx_successB, 'target'] = 1

        # Drop post_operation variables
        data.drop(STATIC_CATEGORIES['patient_postoperative_filtered'],
                  inplace=True,
                  axis=1)

        return self._sample_data(data)

    def get_dynamic(self):

        df = pd.read_csv(PATH_DYNAMIC_CLEAN, parse_dates=['time'])

        # Truncate dynamic file to time_offset before end of operation

        df = df.groupby('id_patient').apply(self._truncate_datetime)

        # Filter result based on static set

        selector = self.get_static()['id_patient']
        df = df[df.id_patient.isin(selector)]

        return df

    def _sample_data(self, df):
        if not self.test and not self.train:
            return df

        train_df, test_df = train_test_split(df,
                                             test_size=0.3,
                                             random_state=self._random_state)

        if self.train:
            return train_df

        if self.test:
            return self._drop_target_column(test_df)

    def _drop_target_column(self, df):
        return df.drop(['target'], axis=1)

    def _truncate_datetime(self, df, offset):
        date_max = df.time.max() - timedelta(minutes=self.time_offset)
        return df[df.time <= date_max]
