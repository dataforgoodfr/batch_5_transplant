import os
import sys
import glob
import hashlib
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from transplant.config import *


PATIENT_TO_DROP = [
    405  # Missing data for static vars:  Survival_days_27_10_2018 = 'xxx'
]


# Dynamic variables methods
#######################################
def load_dynamic_raw(dir_raw, file_pattern):
    '''Load raw files into one single DataFrame'''
    dfs = []
    paths_raw = sorted(glob.glob(os.path.join(dir_raw, file_pattern)))
    if len(paths_raw) == 0:
        raise FileNotFoundError('No files found in %s with file pattern %s'
                                % (dir_raw, file_pattern))
    for path in paths_raw:
        df = pd.read_excel(path, header=None)       # header=None is crucial...
        dfs += split_dynamic_raw_multiple_blocs(df)  # ...for this method
    return pd.concat(dfs, axis=0, ignore_index=True, sort=True)


def split_dynamic_raw_multiple_blocs(df):
    """Split multiple data blocs of a raw Bloc*D4G.xls file loaded
    into a dataframe.

    If you look carefully, you can see that many Bloc*D4G.xls files have
    multiple header rows inside the file followed by new blocs of data...
    ...and the terrible thing is that sometimes the new header is not
    even aligned with the other ones...

    This method simply splits the dataframe into new dataframes with
    proper headers.
    """
    # Detect dynamic header indexes
    def get_header_indexes(min_header):
        return df[df.isin(RAW_DYNAMIC_HEADERS).sum(axis=1) >= min_header].index
    header_idx = get_header_indexes(1)
    # Check: we ensure that it is exactly the same thing to detect the headers
    # looking for at least 1 DYNAMIC_HEADERS or 6 in a row. We choose 6 because
    # the header row with the minimum number of RAW_DYNAMIC_HEADERS was found
    # in Bloc8D4G.xls and has 6 headers. If the check fails, a false positive
    # might have been detected (ex: text cell with a RAW_DYNAMIC_HEADERS).
    assert header_idx.equals(get_header_indexes(6)), "Failed to detect headers"
    # Add last index
    header_idx = list(header_idx) + [len(df)]

    # For each data bloc, extract "df_split" and update its columns
    # with the correct headers
    dfs = []

    for i in range(len(header_idx) - 1):
        df_s = df.loc[header_idx[i]: header_idx[i + 1] - 1].copy()
        df_s.columns = ['time', 'date', 'foreign_key'] + \
            df_s.iloc[0].tolist()[3:]
        df_s = df_s.loc[:, ~df_s.columns.isna()]  # Remove other NaN columns
        dfs.append(df_s.reset_index(drop=True))
    return dfs


def clean_dynamic_raw(df_dynamic, df_static):
    '''Clean dynamic raw DataFrame'''
    # Rename some columns and trim spaces
    df_dynamic.columns = [c.strip() for c in df_dynamic.columns]

    # Create a static_lookup, matching id_patient and foreign_key
    key_lookup = pd.read_csv(PATH_STATIC_LOOKUP)

    static_lookup = pd.merge(df_static[['id_patient',
                                        'date_transplantation',
                                        'date_sortie_bloc',
                                        'heure_arrivee_bloc',
                                        'heure_transfert_rea']],
                             key_lookup, how='left', on='id_patient')
    static_lookup.dropna(subset=['foreign_key'], inplace=True)

    # The foreign_key is the unique identifier of a user. Since a user can have
    # multiple transplantations, we create two matching keys, one for the
    # beginning (date_transplantation), one for the end (date_sortie_bloc.)
    # More details here - https://github.com/dataforgoodfr/batch_5_transplant
    # issues/62.
    static_lookup['id_transplant_begin'] = \
        static_lookup['foreign_key'].astype(int).astype(str) + \
        '-' + static_lookup['date_transplantation'].astype(str)

    static_lookup['id_transplant_end'] = \
        static_lookup['foreign_key'].astype(int).astype(str) + \
        '-' + static_lookup['date_sortie_bloc'].astype(str)

    static_lookup.drop('foreign_key', axis=1, inplace=True)

    # Drop corrupted or useless data
    col_to_drop = [col for col in df_dynamic.columns
                   if col.startswith('Unnamed:')]
    df_dynamic = df_dynamic.drop(columns=col_to_drop)
    df_dynamic = df_dynamic.dropna(subset=['foreign_key', 'date'])

    # Format dtypes
    df_dynamic = cast_integers(df_dynamic)

    # From dynamic dataset, parse datetime. Beware the format might be
    # interpreted wrong by Pandas ('%d/%m/%Y' vs '%m/%d/%Y') resulting in bad
    # matching.
    df_dynamic['date'] = pd.to_datetime(df_dynamic['date'],
                                        format='%d/%m/%Y',
                                        exact=True)

    # Create a matching key for the dynamic set
    df_dynamic['id_transplant'] = \
        df_dynamic['foreign_key'].astype(int).astype(str) + \
        '-' + df_dynamic['date'].astype(str)

    # Since a patient can be operated on multiple days, we isolate patients
    # in a separate DataFrame static_lookup_multi_days
    static_lookup_multi_days = \
        static_lookup[static_lookup['date_sortie_bloc'] >
            static_lookup['date_transplantation']]

    # We perform two merges between dynamic and static for both begin and end
    # of transplantation.
    begin = pd.merge(df_dynamic, static_lookup, left_on='id_transplant',
                     right_on='id_transplant_begin', how='inner')
    end = pd.merge(df_dynamic, static_lookup_multi_days,
                   left_on='id_transplant',
                   right_on='id_transplant_end', how='inner')

    df_dynamic_transplant = pd.concat([begin, end])

    # Create time column by concatenating date and time variables
    df_dynamic_transplant['time'] = pd.to_datetime(
        df_dynamic_transplant['date'].dt.strftime('%Y-%m-%d') +
        ' ' + df_dynamic_transplant['time'])

    # Filter datetime after the hour of operation beginning (heure_arrivee_bloc)
    # and before end of operation (heure_transfert_rea).
    df_dynamic_transplant['operation_begin'] = pd.to_datetime(
        df_dynamic_transplant['date_transplantation'].dt.strftime('%Y-%m-%d') +
        ' ' + df_dynamic_transplant['heure_arrivee_bloc'].astype(str))

    df_dynamic_transplant['operation_end'] = pd.to_datetime(
        df_dynamic_transplant['date_sortie_bloc'].dt.strftime('%Y-%m-%d') +
        ' ' + df_dynamic_transplant['heure_transfert_rea'].astype(str))

    transplantation_limits_mask = \
        (df_dynamic_transplant['time'] >= df_dynamic_transplant['operation_begin']) & \
        (df_dynamic_transplant['time'] <= df_dynamic_transplant['operation_end'])

    df_dynamic_transplant = df_dynamic_transplant[transplantation_limits_mask]

    # Change column order
    df_dynamic_transplant = df_dynamic_transplant. \
        set_index(['id_patient', 'time']).reset_index()

    df_dynamic_transplant = df_dynamic_transplant.drop(
        columns=['date', 'foreign_key', 'id_transplant_begin',
                 'id_transplant_end', 'date_sortie_bloc',
                 'date_transplantation', 'id_transplant',
                 'operation_begin', 'operation_end', 'heure_arrivee_bloc',
                 'heure_transfert_rea'])

    # Checks
    assert (df_dynamic_transplant.id_patient.dtypes == 'int'),\
        "TypeError: Inconsistency in parsed dynamic data: id_patient not int"

    return df_dynamic_transplant


def correct_date_shift(x):
    idx_0h = (x['time'] - x['time'].shift(1)) < timedelta(days=0)  # 0h indexes
    for i in idx_0h.index[idx_0h]:  # loop over all 0h index
        x['time'].loc[i:] = x['time'].loc[i:] + timedelta(days=1)
    return x


# Static variables methods
#######################################
def load_static_raw(dir_raw, file_pattern):
    '''Load raw files into one single DataFrame'''
    paths_raw = glob.glob(os.path.join(dir_raw, file_pattern))
    # Check that there is only one file
    if len(paths_raw) != 1:
        files = [os.path.basename(p) for p in paths_raw]
        print("\nERROR: this script supports only 1 static file, but %d file"
              "(s) were found in %s with file pattern %s: %s"
              % (len(paths_raw), file_pattern, dir_raw, files))
        sys.exit(1)

    df = pd.read_excel(paths_raw[0], sheet_name='ensemble')
    return df


def clean_static_raw(df):
    '''Clean static raw DataFrame'''
    # Rename some columns
    df = df.rename(columns={'numero': 'id_patient'})
    df.columns = [c.strip() for c in df.columns]   # trim spaces

    # Drop corrupted or useless data
    df = df.dropna(subset=['id_patient'])  # drop rows with nan in id_patient
    df = df[~df.id_patient.isin(PATIENT_TO_DROP)]

    # Replace null values (date 1900, NF, etc.) by NaNs
    df.loc[df['date_sortie_bloc'] < datetime(2000, 1, 1),
           'date_sortie_bloc'] = np.NaN
    df.replace({'NF': np.NaN}, inplace=True)

    # Replace heure_arrivee_bloc to 00:00:00 if missing
    df['heure_arrivee_bloc'] = df['heure_arrivee_bloc'].fillna('00:00:00')

    # Format dtypes
    df = cast_integers(df)

    return df


# Common methods
#######################################
def cast_integers(df):
    """Try to cast all columns of a DataFrame to integer"""
    for col in df.columns:
        try:
            if (df[col].astype(int) == df[col]).all():
                df[col] = df[col].astype(int)
        except (ValueError, TypeError):
            pass
    return df


def get_hash_raw_and_build_clean():
    """ Get the md5sum of all the raw files + the current python
    file (__file__)."""
    # Get paths
    dir_raws = os.path.realpath(os.path.join(PATH_STATIC_RAW, '../'))
    paths_raws = glob.glob(os.path.join(dir_raws, '*/*'))
    paths_files_to_hash = paths_raws + [os.path.realpath(__file__)]

    # Hash!
    md5 = hashlib.md5()
    for path in paths_files_to_hash:
        with open(path, 'rb') as f:
            md5.update(f.read())
    return md5.hexdigest()


# Script
#######################################
if __name__ == '__main__':
    print('Building clean csv for static data...')
    df_static = load_static_raw(PATH_STATIC_RAW, PATTERNS_RAW["static"])
    df_static = clean_static_raw(df_static)
    df_static.to_csv(PATH_STATIC_CLEAN, index=False)

    print('Building clean csv for dynamic data...')
    df_dynamic = load_dynamic_raw(PATH_DYNAMIC_RAW, PATTERNS_RAW["dynamic"])
    df_dynamic = clean_dynamic_raw(df_dynamic, df_static)
    df_dynamic.to_csv(PATH_DYNAMIC_CLEAN, index=False)

    print('GREAT SUCCESS!')
