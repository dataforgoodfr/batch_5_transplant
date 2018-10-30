#!/usr/bin/python
import pandas as pd
from config.config import *
import glob

class Parser:

    def __init__(self):
        self.map_fields = MODEL_TABLE_FIELDS
        self.data_clean_dir = DATA_CLEAN

    def import_clean_file(self, filename):
        try:
            file = pd.read_csv(filename)
            file.columns = map(str.lower, file.columns)
            str_to_replace = (
                (' ', '_'),
                (' ', '_'),
                ('(', '_'),
                (')', ''),
                ('.', '')
            )
            for s in str_to_replace:
                file.columns = file.columns.str.replace(*s)

            return file
        except Exception as e:
            print("Error importing your clean file :\nAn exception of type {0} occurred. \nArguments:{1!r}".format(type(e).__name__, e))
            print("\nIs the file exists in {} ?".format(self.data_clean_dir))

    def split_fact_tables(self, filename):
        data = self.import_clean_file(filename)
        for name, array in self.map_fields.items():
            df = data[data.columns.intersection(array)]
            filename = '../data/clean_data/model/fct_{}.csv'.format(name)
            df.to_csv(filename)


    def upload_xls_files(self):
        return glob.glob('{}/*.xls'.format(DATA_ORIGINAL_MACHINES))

    def read_xls_files(self, path_xls):
        """
        Read xls file in a pandas DataFrame.
        Look for specific header by patient, adapt patient header to HEADER_FULL
        Conact all result in data [DataFrame]

        Input :
            - path_xls : [string] path to xls file
        Return :
            - data : [DataFrame]
        """

        df = pd.read_excel(path_xls)

        # Rename columns (First 2 columns)
        df.rename(columns={'Unnamed: 0': 'id_patient'}, inplace=True)
        df.rename(columns={'Unnamed: 1': 'time'}, inplace=True)

        # List of id_patient in files (dropping NaN values)
        ## Error in file if id_patient = Nan (??)
        list_patient_in_file = list(df[~pd.isnull(df['id_patient'])]['id_patient'].unique())

        # New DataFrame, will be fill by patiend DataFrame
        data = pd.DataFrame(columns=FULL_HEADER)

        # For Each id_patient
        ## Trying to find patient headher
        ## Adpate this header
        ## Concat with an empty DataFrame (with HEADER_FULL)
        for id_patient in list_patient_in_file:
            try:
                # patient specifiq DataFrame
                patient_df = df[df['id_patient'] == id_patient].copy()

                # Specifiq case (first patient in df)
                if patient_df[0:1].index.values[0] == 1:  # Check if this is the first patient in file
                    patient_header = patient_df.columns
                    # Drop `Unnamed:`columns
                    patient_header_fix = [col for col in patient_df.columns if not col.startswith('Unnamed:')]
                    data = pd.concat([data, patient_df[patient_header_fix]], axis=0, sort=True)
                # Generiq case
                else:
                    patient_header_fix = [col for col in patient_df.columns if not col.startswith('Unnamed:')]
                    first_idx_patient = patient_df[0:1].index.values[0]

                    # Looking for specifiq header for our patient
                    patient_header = df.loc[first_idx_patient - 2].values
                    patient_df.columns = patient_header

                    patient_header[0] = 'id_patient'  # NaN -> 'id_patient'
                    patient_header[1] = 'time'  # NaN -> 'time'
                    # Drop NaN columns
                    patient_header = [col for col in patient_header if str(col) != 'nan']
                    patient_df = patient_df[patient_header]

                    # Fill unknow columns for this patient ()
                    patient_df = self.fill_unknow_col_in_df(patient_df)

                    data = pd.concat([data, patient_df[patient_header_fix]], axis=0, sort=True)
            except Exception as e:
                print('Error during reading files ' + str(path_xls) + ' for id_patient : ' + str(id_patient))
                print(e)

        # Cast id_patient to int
        data['id_patient'] = data['id_patient'].astype(int)
        data.fillna(0, inplace=True)

        return data

    def fill_unknow_col_in_df(self, data):
        """
        Check if data have all columns from FULL_HEADER
        If not, fill unkonw columns by 0
        Using in read_xls_files()

        Input :
            - data : [DataFrame]
        Ouput :
            - data : [DataFrame]
        """
        for unknow_col in [col for col in FULL_HEADER if col not in data.columns]:
            data[unknow_col] = 0

        return data