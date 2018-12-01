import pandas as pd
import numpy as np
import warnings
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
        "id_patient",
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
        "id_patient",
        "LOS_first_ventilation",
        "immediate_extubation",
        "secondary_intubation",
        "Survival_days_27_10_2018"
    ]

    def build_training_set(self):

        data = pd.read_csv(PATH_STATIC_CLEAN)

        data = data[self.pre_operatoire_cols +
                    self.donor_cols +
                    self.post_operatoire_cols]

        data["target"] = np.nan
        data["target"][(data["secondary_intubation"] == 1)] = "unsuccessful IE"
        data["target"][(data["secondary_intubation"] == 0)] = "successful IE"

        data.drop(['secondary_intubation'
                  , 'immediate_extubation'], inplace=True, axis=1)

        msg = "Done! Found {} patients with {} variables".format(data.shape[0],
                                                                 data.shape[1])
        print(msg)

        return data
