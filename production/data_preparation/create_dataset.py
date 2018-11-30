import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')


class DimensionDataSet:
    """
    Transform csv patient and donors into a dimension dataset that
    can be used for modeling. Following steps are applied:
    Step 1 - Define feature type
    Step 2 - Build the target variable
    Step 3 - Drop unecessary rows
    Step 4 - Export data
    """
    data_folder = "../data/"
    columns = []
    export_name = 'data_merged.csv'
    cat_col = [
        "date_transplantation",
        "heure_arrivee_bloc",
        "pathologie",
        "age",
        "sex",
        "other_organ_transplantation",
        "transplanted_twice_during_study_period",
        "super_urgence",
        "retransplant",
        "preoperative_ICU",
        "preoperative_vasopressor",
        "preoperative_mechanical_ventilation",
        "PFO",
        "diabetes",
        "preoperative_pulmonary_hypertension"
        "Insuffisance_renale",
        "CMV_receveur",
        "plasmapherese",
        "preoperative_ECMO",
        "ATCD_chirugicaux",
        "thoracic_surgery_history",
        "CMV_donneur",
        "EBV_donneur",
        "Sex_donor",
        "BMI_donor"
    ]

    num_col = [
        "Poids",
        "Taille",
        "time_on_waiting_liste",
        "LAS",
        "body_mass_index",
        "PAPS",
        "Age_donor",
        "Poids_donor",
        "Taille_donor",
        "Donneur_CPT",
        "Tabagisme_donor",
        "Aspirations_donor",
        "RX_donor",
        "PF_donor",
        "oto_score"
    ]

    text = [
        "ATCD_medicaux",
        "ATCD_chirugicaux"
    ]
    target = [
        'secondary_intubation'
    ]

    def merge_datasets(self):
        """
        Merge pre, post and donor datasets.
        """
        dim_patient_preoperatoire = pd.read_csv(
                                        "{}dim_patient_preoperatoire.csv"
                                        .format(self.data_folder))

        dim_donneur = pd.read_csv("{}dim_donneur.csv".format(self.data_folder))

        dim_patient_intraoperatoire = pd.read_csv(
                                        "{}dim_patient_intraoperatoire.csv"
                                        .format(self.data_folder))

        dim_patient_postoperatoire = pd.read_csv(
                                        "{}dim_patient_postoperatoire.csv"
                                        .format(self.data_folder))

        data = pd.merge(dim_patient_preoperatoire,
                        dim_donneur,
                        how='left',
                        on="numero")

        data = pd.merge(data,
                        dim_patient_postoperatoire[["numero",
                                                    " immediate_extubation",
                                                    "secondary_intubation"]],
                        how='left',
                        on='numero').rename(columns={' immediate_extubation':
                                                     'immediate_extubation'})

        return data

    def build_training_set(self):

        id_col = "numero"

        col_drop = ["Unnamed: 0_x", "Unnamed: 0_y"]

        data = self.merge_datasets()

        data.drop(col_drop, axis=1, inplace=True)
        data.columns = [i.lower() for i in data.columns]

        data["target"] = np.nan
        data["target"][(data["secondary_intubation"] == 1)] = "unsuccessful IE"
        data["target"][(data["secondary_intubation"] == 0)] = "successful IE"

        data.drop(['secondary_intubation'
                  , 'immediate_extubation'], inplace=True, axis=1)

        return data

    def export_training_set(self):
        data = self.build_training_set()
        data.to_csv('{}data_merged.csv'.format(self.data_folder), index=False)
        msg = "Done! Found {} patients with {} variables".format(data.shape[0],
                                                                 data.shape[1])
        print(msg)
