import pandas as pd
import numpy as np
import warnings
from transplant.config import PATH_DYNAMIC_CLEAN

warnings.filterwarnings('ignore')


class Dataset:
    """
    Transform csv patient and donors into a dimension dataset that
    can be used for modeling. Following steps are applied:
    Step 1 - Select a subset of columns
    Step 2 - Build the target variable
    Step 3 - Export data
    """
    data_folder = "../data/"
    columns = []
    export_name = 'data_merged.csv'
    pre_operatoire_cols = [
        "numero",
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
        "numero",
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
        "numero",
        "LOS_first_ventilation",
        " immediate_extubation",
        "secondary_intubation",
        "Survival_days_27_10_2018"
    ]

    def merge_datasets(self):
        """
        Merge pre, post and donor datasets.
        """
        static = pd.read_csv(PATH_STATIC_CLEAN)

        df_pre_operatoire = static[self.pre_operatoire_cols]
        df_donor = static[self.donor_cols]
        df_post_operatoire = static[self.post_operatoire_cols]

        data = pd.merge(df_pre_operatoire,
                        df_donor,
                        how='left',
                        on="numero")

        data = pd.merge(data,
                        df_post_operatoire,
                        how='left',
                        on='numero')

        return data

    def build_training_set(self):

        id_col = "numero"

        data = self.merge_datasets()

        data.columns = [i.lower() for i in data.columns]

        data["target"] = np.nan
        data["target"][(data["secondary_intubation"] == 1)] = "unsuccessful IE"
        data["target"][(data["secondary_intubation"] == 0)] = "successful IE"

        data.drop(['secondary_intubation'
                  , 'immediate_extubation'], inplace=True, axis=1)

        msg = "Done! Found {} patients with {} variables".format(data.shape[0],
                                                                 data.shape[1])
        print(msg)

        return data
