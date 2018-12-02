import pandas as pd
import numpy as np
import warnings
from sklearn.model_selection import train_test_split

from transplant.config import PATH_STATIC_CLEAN

warnings.filterwarnings('ignore')


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

    _random_state = 1

    def __init__(self, test=False, train=False, time_offset=30):
        self.test = test
        self.train = train
        self.time_offset = time_offset

    pre_operatoire_cols = [
        "id_patient",
        "date_transplantation",
        "heure_arrivee_bloc",
        "pathologie",
        "age",
        "sexe",
        "Poids",
        "Taille",
        "other_organ_transplantation",
        "super_urgence",
        "retransplant",
        "transplanted_twice_during_study_period",
        "time_on_waiting_liste",
        "LAS",
        "preoperative_ICU",
        "preoperative_vasopressor",
        "preoperative_mechanical_ventilation",
        "PFO",
        "body_mass_index",
        "diabetes",
        "preoperative_pulmonary_hypertension",
        "PAPS",
        "Insuffisance_renale",
        "CMV_receveur",
        "plasmapherese",
        "preoperative_ECMO",
        "thoracic_surgery_history"
    ]

    donor_cols = [
        "Age_donor",
        "Sex_donor",
        "BMI_donor",
        "Poids_donor",
        "Taille_donor",
        "Donneur_CPT",
        "Tabagisme_donor",
        "Aspirations_donor",
        "RX_donor",
        "PF_donor",
        "oto_score"
    ]

    post_operatoire_cols = [
        "LOS_first_ventilation",
        "immediate_extubation",
        "secondary_intubation",
        "Survival_days_27_10_2018"
    ]

    def get_static(self):

        data = pd.read_csv(PATH_STATIC_CLEAN)

        data = data[self.pre_operatoire_cols +
                    self.donor_cols +
                    self.post_operatoire_cols]

        # See https://github.com/dataforgoodfr/batch_5_transplant/blob/master/data/README.md#target

        data['target'] = np.nan

        # Success A
        data['target'] = np.where((data.immediate_extubation == 1) &
                               (data.secondary_intubation == 0), 1, np.nan)

        # Success B
        data['target'] = np.where((data.target == 1) |
                                  ((data.immediate_extubation == 0) &
                                  (data.secondary_intubation == 0) &
                                  (data.LOS_first_ventilation < 2) &
                                  (data.Survival_days_27_10_2018 >= 2)), 1, 0)

        # Drop post_operation variables
        data.drop(['secondary_intubation'
                  , 'immediate_extubation'
                  , 'LOS_first_ventilation'
                  , 'Survival_days_27_10_2018']
                  , inplace=True
                  , axis=1)

        return self._sample_data(data)

    def _sample_data(self, df):
        if not self.test and not self.train:
            return df

        train_df, test_df = train_test_split(df
                                             , test_size=0.3
                                             , random_state=self._random_state)

        if self.train:
            return train_df

        if self.test:
            return self._drop_target_column(test_df)

    def _drop_target_column(self, df):
        return df.drop(['target'], axis=1)
